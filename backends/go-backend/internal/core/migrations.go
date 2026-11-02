// ©AngelaMos | 2026
// migrations.go

package core

import (
	"context"
	"crypto/sha256"
	"database/sql"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"strings"

	"github.com/jmoiron/sqlx"
)

func Migrate(ctx context.Context, db *sqlx.DB, directory string) error {
	entries, err := os.ReadDir(directory)
	if err != nil {
		return err
	}
	pattern := regexp.MustCompile(`^[0-9]{3}_[a-z0-9_]+\.sql$`)
	versions := make(map[string]bool)
	var names []string
	for _, entry := range entries {
		if entry.IsDir() || !pattern.MatchString(entry.Name()) {
			return fmt.Errorf("unexpected migration entry: %s", entry.Name())
		}
		version, _, _ := strings.Cut(entry.Name(), "_")
		if versions[version] {
			return fmt.Errorf("duplicate migration version: %s", version)
		}
		versions[version] = true
		names = append(names, entry.Name())
	}
	if len(names) == 0 {
		return errors.New("no migrations found")
	}
	return InTx(ctx, db, func(tx *sqlx.Tx) error {
		if _, err := tx.ExecContext(ctx, "SELECT pg_advisory_xact_lock(79382301)"); err != nil {
			return err
		}
		if _, err := tx.ExecContext(ctx, `CREATE TABLE IF NOT EXISTS schema_migrations (
			name TEXT PRIMARY KEY, checksum TEXT NOT NULL,
			applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
		)`); err != nil {
			return err
		}
		var applied []string
		if err := tx.SelectContext(ctx, &applied, "SELECT name FROM schema_migrations ORDER BY name"); err != nil {
			return err
		}
		if len(applied) > len(names) {
			return errors.New("database contains migrations absent from this build")
		}
		for index, name := range applied {
			if names[index] != name {
				return errors.New("applied migration history does not match this build")
			}
		}
		for _, name := range names {
			body, err := os.ReadFile(filepath.Join(directory, name))
			if err != nil {
				return err
			}
			checksum := fmt.Sprintf("%x", sha256.Sum256(body))
			var stored string
			err = tx.GetContext(ctx, &stored, "SELECT checksum FROM schema_migrations WHERE name = $1", name)
			if err == nil {
				if stored != checksum {
					return fmt.Errorf("applied migration was modified: %s", name)
				}
				continue
			}
			if !errors.Is(err, sql.ErrNoRows) {
				return err
			}
			if _, err := tx.ExecContext(ctx, string(body)); err != nil {
				return fmt.Errorf("apply %s: %w", name, err)
			}
			if _, err := tx.ExecContext(ctx, "INSERT INTO schema_migrations (name, checksum) VALUES ($1, $2)", name, checksum); err != nil {
				return err
			}
		}
		return nil
	})
}
