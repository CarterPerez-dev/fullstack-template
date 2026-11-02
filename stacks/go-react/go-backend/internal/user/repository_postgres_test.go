// ©AngelaMos | 2026
// repository_postgres_test.go

package user

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

func TestPostgresUserStateTransitions(t *testing.T) {
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
	if err := core.Migrate(ctx, db, "../../migrations"); err != nil {
		t.Fatal(err)
	}
	repo := NewRepository(db)
	account := &User{
		ID: uuid.NewString(), Email: "owner@example.com", PasswordHash: "original",
		Role: RoleAdmin, Tier: TierFree,
	}
	if err := repo.Create(ctx, account); err != nil {
		t.Fatal(err)
	}
	if err := repo.RehashPassword(ctx, account.ID, "original", "upgraded"); err != nil {
		t.Fatal(err)
	}
	stored, err := repo.GetByID(ctx, account.ID)
	if err != nil || stored.PasswordHash != "upgraded" || stored.TokenVersion != 0 {
		t.Fatalf("rehash changed session version or failed: %v", err)
	}
	start := make(chan struct{})
	results := make(chan error, 2)
	for range 2 {
		go func() {
			<-start
			results <- repo.UpdatePassword(ctx, account.ID, "upgraded", "replacement")
		}()
	}
	close(start)
	var successes, conflicts int
	for range 2 {
		switch err := <-results; {
		case err == nil:
			successes++
		case errors.Is(err, core.ErrConflict):
			conflicts++
		default:
			t.Fatal(err)
		}
	}
	if successes != 1 || conflicts != 1 {
		t.Fatalf("successes=%d conflicts=%d", successes, conflicts)
	}
	if err := repo.RehashPassword(ctx, account.ID, "upgraded", "stale"); !errors.Is(err, core.ErrConflict) {
		t.Fatalf("stale rehash accepted: %v", err)
	}
	stored, err = repo.GetByID(ctx, account.ID)
	if err != nil || stored.PasswordHash != "replacement" || stored.TokenVersion != 1 {
		t.Fatalf("password and session version were not updated atomically: %v", err)
	}
	duplicate := &User{
		ID: uuid.NewString(), Email: account.Email, PasswordHash: "overwrite",
		Role: RoleUser, Tier: TierFree,
	}
	if err := repo.Create(ctx, duplicate); !errors.Is(err, core.ErrDuplicateKey) {
		t.Fatalf("duplicate enrollment accepted: %v", err)
	}
	stored, err = repo.GetByID(ctx, account.ID)
	if err != nil || stored.Role != RoleAdmin || stored.PasswordHash != "replacement" {
		t.Fatalf("duplicate enrollment changed owner: %v", err)
	}
	service := NewService(repo)
	if _, err := service.UpdateUserRole(ctx, account.ID, RoleUser); err != nil {
		t.Fatal(err)
	}
	if _, err := service.UpdateUserTier(ctx, account.ID, TierEnterprise); err != nil {
		t.Fatal(err)
	}
	name := "Updated profile"
	for _, request := range []UpdateUserRequest{{Name: &name}, {}} {
		updated, err := service.UpdateMe(ctx, account.ID, request)
		if err != nil {
			t.Fatal(err)
		}
		if updated.Name != name || updated.Role != RoleUser || updated.Tier != TierEnterprise || updated.TokenVersion != 1 || updated.PasswordHash != "replacement" {
			t.Fatal("profile update changed unrelated account attributes")
		}
	}
	if err := repo.SoftDelete(ctx, account.ID); err != nil {
		t.Fatal(err)
	}
	updates := []func() (*User, error){
		func() (*User, error) { return repo.UpdateName(ctx, account.ID, &name) },
		func() (*User, error) { return repo.UpdateRole(ctx, account.ID, RoleAdmin) },
		func() (*User, error) { return repo.UpdateTier(ctx, account.ID, TierPro) },
	}
	for _, update := range updates {
		if _, err := update(); !errors.Is(err, core.ErrNotFound) {
			t.Fatalf("deleted account remained writable: %v", err)
		}
	}
}
