// ©AngelaMos | 2026
// browser_test.go

package auth

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"path/filepath"
	"strings"
	"testing"
	"time"

	"github.com/carterperez-dev/templates/go-backend/internal/config"
)

type browserRepository struct {
	Repository
	token *RefreshToken
}

func (r browserRepository) FindByHash(context.Context, string) (*RefreshToken, error) {
	return r.token, nil
}

func (r browserRepository) Rotate(context.Context, string, *RefreshToken) error {
	return nil
}

func TestRefreshTransport(t *testing.T) {
	directory := t.TempDir()
	privatePath, publicPath := filepath.Join(directory, "private.pem"), filepath.Join(directory, "public.pem")
	if err := GenerateKeyPair(privatePath, publicPath); err != nil {
		t.Fatal(err)
	}
	manager, err := NewJWTManager(config.JWTConfig{
		PrivateKeyPath: privatePath, PublicKeyPath: publicPath,
		Issuer: "test", Audience: "test", AccessTokenExpire: 2 * time.Minute,
		RefreshTokenExpire: time.Hour,
	})
	if err != nil {
		t.Fatal(err)
	}
	for _, test := range []struct {
		name    string
		header  string
		body    string
		version int
		status  int
	}{
		{"browser", "cookie", "", 3, http.StatusOK},
		{"native", "", `{"refresh_token":"fixture"}`, 3, http.StatusOK},
		{"cookie-without-header", "", "", 3, http.StatusUnauthorized},
		{"form-cannot-select-cookie", "", "refresh_token=fixture", 3, http.StatusUnauthorized},
		{"revoked-version", "cookie", "", 4, http.StatusUnauthorized},
	} {
		t.Run(test.name, func(t *testing.T) {
			repo := browserRepository{token: &RefreshToken{
				ID: "old", UserID: "user", FamilyID: "family", TokenVersion: 3,
				ExpiresAt: time.Now().Add(time.Hour),
			}}
			users := securityUserProvider{user: &UserInfo{
				ID: "user", Email: "user@example.com", Role: "user", Tier: "free",
				TokenVersion: test.version,
			}}
			handler := NewHandler(NewService(repo, manager, users, nil), true)
			request := httptest.NewRequest(http.MethodPost, "/v1/auth/refresh", strings.NewReader(test.body))
			request.Header.Set("X-Auth-Transport", test.header)
			request.AddCookie(&http.Cookie{Name: "refresh_token", Value: "fixture"})
			response := httptest.NewRecorder()
			handler.Refresh(response, request)
			if response.Code != test.status {
				t.Fatalf("status = %d, expected %d: %s", response.Code, test.status, response.Body.String())
			}
			if test.status != http.StatusOK {
				return
			}
			var envelope struct {
				Data AuthResponse `json:"data"`
			}
			if err := json.Unmarshal(response.Body.Bytes(), &envelope); err != nil {
				t.Fatal(err)
			}
			if envelope.Data.Tokens.ExpiresIn != 120 {
				t.Fatal("token lifetime does not match configuration")
			}
			cookies := response.Result().Cookies()
			if test.header == "cookie" {
				if envelope.Data.Tokens.RefreshToken != "" || len(cookies) != 1 {
					t.Fatal("browser refresh token must only be delivered in its cookie")
				}
				cookie := cookies[0]
				if !cookie.HttpOnly || !cookie.Secure || cookie.SameSite != http.SameSiteLaxMode || cookie.MaxAge != 3600 {
					t.Fatal("cookie security attributes are incorrect")
				}
			} else if envelope.Data.Tokens.RefreshToken == "" || len(cookies) != 0 {
				t.Fatal("native refresh must return a body token without setting a cookie")
			}
		})
	}
}
