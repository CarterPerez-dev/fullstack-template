// AngelaMos | 2026
// repository.go

package auth

import (
	"context"
	"database/sql"
	"errors"
	"fmt"
	"time"

	"github.com/jmoiron/sqlx"

	"github.com/carterperez-dev/templates/go-backend/internal/core"
)

type Repository interface {
	Create(ctx context.Context, token *RefreshToken) error
	FindByHash(ctx context.Context, tokenHash string) (*RefreshToken, error)
	FindByID(ctx context.Context, id string) (*RefreshToken, error)
	Rotate(ctx context.Context, oldID string, token *RefreshToken) error
	RevokeByID(ctx context.Context, id string) error
	RevokeByFamilyID(ctx context.Context, familyID string) error
	RevokeAllForUser(ctx context.Context, userID string) error
	GetActiveSessionsForUser(
		ctx context.Context,
		userID string,
	) ([]RefreshToken, error)
	DeleteExpired(ctx context.Context) (int64, error)
}

type repository struct {
	db *sqlx.DB
}

func NewRepository(db *sqlx.DB) Repository {
	return &repository{db: db}
}

func (r *repository) Create(ctx context.Context, token *RefreshToken) error {
	query := `
		INSERT INTO refresh_tokens (
			id, user_id, token_hash, family_id, expires_at,
			user_agent, ip_address, token_version
		) VALUES (
			$1, $2, $3, $4, $5, $6, $7, $8
		)
		RETURNING created_at`

	err := r.db.GetContext(ctx, &token.CreatedAt, query,
		token.ID,
		token.UserID,
		token.TokenHash,
		token.FamilyID,
		token.ExpiresAt,
		token.UserAgent,
		token.IPAddress,
		token.TokenVersion,
	)
	if err != nil {
		return fmt.Errorf("create refresh token: %w", err)
	}

	return nil
}

func (r *repository) FindByHash(
	ctx context.Context,
	tokenHash string,
) (*RefreshToken, error) {
	query := `
		SELECT
			id, user_id, token_hash, family_id, token_version, expires_at, created_at,
			is_used, used_at, revoked_at, replaced_by_id, user_agent, ip_address
		FROM refresh_tokens
		WHERE token_hash = $1`

	var token RefreshToken
	err := r.db.GetContext(ctx, &token, query, tokenHash)
	if errors.Is(err, sql.ErrNoRows) {
		return nil, fmt.Errorf("find refresh token: %w", core.ErrNotFound)
	}
	if err != nil {
		return nil, fmt.Errorf("find refresh token: %w", err)
	}

	return &token, nil
}

func (r *repository) FindByID(
	ctx context.Context,
	id string,
) (*RefreshToken, error) {
	query := `
		SELECT
			id, user_id, token_hash, family_id, token_version, expires_at, created_at,
			is_used, used_at, revoked_at, replaced_by_id, user_agent, ip_address
		FROM refresh_tokens
		WHERE id = $1`

	var token RefreshToken
	err := r.db.GetContext(ctx, &token, query, id)
	if errors.Is(err, sql.ErrNoRows) {
		return nil, fmt.Errorf("find refresh token: %w", core.ErrNotFound)
	}
	if err != nil {
		return nil, fmt.Errorf("find refresh token: %w", err)
	}

	return &token, nil
}

func (r *repository) Rotate(
	ctx context.Context,
	oldID string,
	token *RefreshToken,
) error {
	query := `
		WITH consumed AS (
			UPDATE refresh_tokens
			SET is_used = true, used_at = NOW(), replaced_by_id = $2
			WHERE id = $1 AND user_id = $3 AND family_id = $5
				AND is_used = false AND revoked_at IS NULL AND expires_at > NOW()
				AND token_version = $9
				AND EXISTS (SELECT 1 FROM users WHERE id = $3 AND token_version = $9 AND deleted_at IS NULL)
			RETURNING user_id, family_id
		)
		INSERT INTO refresh_tokens (
			id, user_id, token_hash, family_id, expires_at, user_agent, ip_address, token_version
		)
		SELECT $2, user_id, $4, family_id, $6, $7, $8, $9 FROM consumed
		RETURNING created_at`
	err := core.InTx(ctx, r.db, func(tx *sqlx.Tx) error {
		var userID string
		if err := tx.GetContext(ctx, &userID, "SELECT id FROM users WHERE id = $1 FOR UPDATE", token.UserID); err != nil {
			return err
		}
		return tx.GetContext(ctx, &token.CreatedAt, query,
			oldID, token.ID, token.UserID, token.TokenHash, token.FamilyID,
			token.ExpiresAt, token.UserAgent, token.IPAddress, token.TokenVersion,
		)
	})
	if errors.Is(err, sql.ErrNoRows) {
		return core.ErrTokenRevoked
	}
	if err != nil {
		return fmt.Errorf("rotate refresh token: %w", err)
	}
	return nil
}

func (r *repository) RevokeByID(ctx context.Context, id string) error {
	query := `
		UPDATE refresh_tokens
		SET revoked_at = NOW()
		WHERE id = $1 AND revoked_at IS NULL`

	result, err := r.db.ExecContext(ctx, query, id)
	if err != nil {
		return fmt.Errorf("revoke refresh token: %w", err)
	}

	rows, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("revoke refresh token: %w", err)
	}

	if rows == 0 {
		return fmt.Errorf("revoke refresh token: %w", core.ErrNotFound)
	}

	return nil
}

func (r *repository) RevokeByFamilyID(
	ctx context.Context,
	familyID string,
) error {
	query := `
		UPDATE refresh_tokens
		SET revoked_at = NOW()
		WHERE family_id = $1 AND revoked_at IS NULL`

	err := core.InTx(ctx, r.db, func(tx *sqlx.Tx) error {
		var userID string
		err := tx.GetContext(ctx, &userID, `
			SELECT id FROM users WHERE id = (
				SELECT user_id FROM refresh_tokens WHERE family_id = $1 LIMIT 1
			) FOR UPDATE`, familyID)
		if errors.Is(err, sql.ErrNoRows) {
			return nil
		}
		if err != nil {
			return err
		}
		_, err = tx.ExecContext(ctx, query, familyID)
		return err
	})
	if err != nil {
		return fmt.Errorf("revoke token family: %w", err)
	}

	return nil
}

func (r *repository) RevokeAllForUser(
	ctx context.Context,
	userID string,
) error {
	query := `
		UPDATE refresh_tokens
		SET revoked_at = NOW()
		WHERE user_id = $1 AND revoked_at IS NULL`

	_, err := r.db.ExecContext(ctx, query, userID)
	if err != nil {
		return fmt.Errorf("revoke all user tokens: %w", err)
	}

	return nil
}

func (r *repository) GetActiveSessionsForUser(
	ctx context.Context,
	userID string,
) ([]RefreshToken, error) {
	query := `
		SELECT
			id, user_id, token_hash, family_id, token_version, expires_at, created_at,
			is_used, used_at, revoked_at, replaced_by_id, user_agent, ip_address
		FROM refresh_tokens
		WHERE user_id = $1
			AND token_version = (SELECT token_version FROM users WHERE id = $1 AND deleted_at IS NULL)
			AND revoked_at IS NULL
			AND is_used = false
			AND expires_at > NOW()
		ORDER BY created_at DESC`

	var tokens []RefreshToken
	err := r.db.SelectContext(ctx, &tokens, query, userID)
	if err != nil {
		return nil, fmt.Errorf("get active sessions: %w", err)
	}

	return tokens, nil
}

func (r *repository) DeleteExpired(ctx context.Context) (int64, error) {
	query := `
		DELETE FROM refresh_tokens
		WHERE expires_at < $1`

	cutoff := time.Now().Add(-24 * time.Hour)

	result, err := r.db.ExecContext(ctx, query, cutoff)
	if err != nil {
		return 0, fmt.Errorf("delete expired tokens: %w", err)
	}

	rows, err := result.RowsAffected()
	if err != nil {
		return 0, fmt.Errorf("delete expired tokens: %w", err)
	}

	return rows, nil
}
