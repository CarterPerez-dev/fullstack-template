// ©AngelaMos | 2026
// repository_postgres_test.go

package auth

import (
	"context"
	"errors"
	"net/url"
	"os"
	"strings"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/jmoiron/sqlx"

	"github.com/carterperez-dev/templates/go-backend/internal/core"
)

func TestPostgresRefreshTransactions(t *testing.T) {
	dsn := os.Getenv("TEST_POSTGRES_URL")
	if dsn == "" {
		t.Skip("TEST_POSTGRES_URL must name a disposable PostgreSQL database")
	}
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()
	admin, err := sqlx.ConnectContext(ctx, "pgx", dsn)
	if err != nil {
		t.Fatal(err)
	}
	defer admin.Close()
	schema := "template_test_" + strings.ReplaceAll(uuid.NewString(), "-", "")
	if _, err := admin.ExecContext(ctx, "CREATE SCHEMA "+schema); err != nil {
		t.Fatal(err)
	}
	defer func() {
		if _, err := admin.ExecContext(context.Background(), "DROP SCHEMA "+schema+" CASCADE"); err != nil {
			t.Error(err)
		}
	}()
	parsed, err := url.Parse(dsn)
	if err != nil {
		t.Fatal(err)
	}
	query := parsed.Query()
	query.Set("search_path", schema)
	parsed.RawQuery = query.Encode()
	db, err := sqlx.ConnectContext(ctx, "pgx", parsed.String())
	if err != nil {
		t.Fatal(err)
	}
	defer db.Close()
	for range 2 {
		if err := core.Migrate(ctx, db, "../../migrations"); err != nil {
			t.Fatal(err)
		}
	}
	repo := NewRepository(db)
	userID := uuid.NewString()
	if _, err := db.ExecContext(ctx, `INSERT INTO users (id, email, password_hash, name)
		VALUES ($1, 'fixture@example.com', 'unused', 'Fixture')`, userID); err != nil {
		t.Fatal(err)
	}
	newToken := func(family string) *RefreshToken {
		return &RefreshToken{
			ID: uuid.NewString(), UserID: userID, FamilyID: family,
			TokenHash: core.HashToken(uuid.NewString()), ExpiresAt: time.Now().Add(time.Hour),
		}
	}
	seed := func() *RefreshToken {
		token := newToken(uuid.NewString())
		if err := repo.Create(ctx, token); err != nil {
			t.Fatal(err)
		}
		return token
	}

	t.Run("concurrent rotation has one successor", func(t *testing.T) {
		original := seed()
		start := make(chan struct{})
		results := make(chan error, 2)
		for range 2 {
			go func() {
				<-start
				results <- repo.Rotate(ctx, original.ID, newToken(original.FamilyID))
			}()
		}
		close(start)
		var successes, revoked int
		for range 2 {
			err := <-results
			switch {
			case err == nil:
				successes++
			case errors.Is(err, core.ErrTokenRevoked):
				revoked++
			default:
				t.Fatal(err)
			}
		}
		if successes != 1 || revoked != 1 {
			t.Fatalf("successes=%d revoked=%d", successes, revoked)
		}
		var count int
		if err := db.GetContext(ctx, &count, "SELECT count(*) FROM refresh_tokens WHERE family_id = $1", original.FamilyID); err != nil || count != 2 {
			t.Fatalf("family size=%d: %v", count, err)
		}
	})

	t.Run("insert failure preserves original", func(t *testing.T) {
		original := seed()
		successor := newToken(original.FamilyID)
		successor.TokenHash = original.TokenHash
		if err := repo.Rotate(ctx, original.ID, successor); err == nil {
			t.Fatal("expected unique hash failure")
		}
		stored, err := repo.FindByID(ctx, original.ID)
		if err != nil || stored.IsUsed || stored.ReplacedByID != nil {
			t.Fatalf("original was consumed on failure: %v", err)
		}
	})

	t.Run("family revocation races descendant rotation", func(t *testing.T) {
		original := seed()
		successor := newToken(original.FamilyID)
		if err := repo.Rotate(ctx, original.ID, successor); err != nil {
			t.Fatal(err)
		}
		start := make(chan struct{})
		results := make(chan error, 2)
		go func() {
			<-start
			results <- repo.RevokeByFamilyID(ctx, original.FamilyID)
		}()
		go func() {
			<-start
			results <- repo.Rotate(ctx, successor.ID, newToken(original.FamilyID))
		}()
		close(start)
		for range 2 {
			if err := <-results; err != nil && !errors.Is(err, core.ErrTokenRevoked) {
				t.Fatal(err)
			}
		}
		var active int
		if err := db.GetContext(ctx, &active, "SELECT count(*) FROM refresh_tokens WHERE family_id = $1 AND revoked_at IS NULL", original.FamilyID); err != nil || active != 0 {
			t.Fatalf("active family tokens=%d: %v", active, err)
		}
	})

	t.Run("version change cannot resurrect session", func(t *testing.T) {
		original := seed()
		if _, err := db.ExecContext(ctx, "UPDATE users SET token_version = token_version + 1 WHERE id = $1", userID); err != nil {
			t.Fatal(err)
		}
		if err := repo.Rotate(ctx, original.ID, newToken(original.FamilyID)); !errors.Is(err, core.ErrTokenRevoked) {
			t.Fatalf("expected revoked token, got %v", err)
		}
	})
}
