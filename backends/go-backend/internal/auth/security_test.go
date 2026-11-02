// ©AngelaMos | 2026
// security_test.go

package auth

import (
	"context"
	"net/http"
	"net/http/httptest"
	"path/filepath"
	"testing"
	"time"

	"github.com/carterperez-dev/templates/go-backend/internal/config"
	"github.com/carterperez-dev/templates/go-backend/internal/core"
	"github.com/carterperez-dev/templates/go-backend/internal/middleware"
)

type securityUserProvider struct {
	UserProvider
	user *UserInfo
}

func (p securityUserProvider) GetByID(_ context.Context, id string) (*UserInfo, error) {
	if p.user == nil || p.user.ID != id {
		return nil, core.ErrNotFound
	}
	return p.user, nil
}

func TestAuthenticationUsesCurrentUserState(t *testing.T) {
	directory := t.TempDir()
	privatePath := filepath.Join(directory, "private.pem")
	publicPath := filepath.Join(directory, "public.pem")
	if err := GenerateKeyPair(privatePath, publicPath); err != nil {
		t.Fatal(err)
	}
	manager, err := NewJWTManager(config.JWTConfig{
		PrivateKeyPath: privatePath, PublicKeyPath: publicPath,
		Issuer: "security-test", Audience: "security-test",
		AccessTokenExpire: time.Minute,
	})
	if err != nil {
		t.Fatal(err)
	}
	token, err := manager.CreateAccessToken(AccessTokenClaims{
		UserID: "test-user", Role: "admin", Tier: "free", TokenVersion: 7,
	})
	if err != nil {
		t.Fatal(err)
	}
	cases := []struct {
		name   string
		user   *UserInfo
		status int
	}{
		{"valid", &UserInfo{ID: "test-user", Role: "admin", TokenVersion: 7}, http.StatusNoContent},
		{"revoked", &UserInfo{ID: "test-user", Role: "admin", TokenVersion: 8}, http.StatusUnauthorized},
		{"demoted", &UserInfo{ID: "test-user", Role: "user", TokenVersion: 7}, http.StatusForbidden},
		{"deleted", nil, http.StatusUnauthorized},
	}
	for _, test := range cases {
		t.Run(test.name, func(t *testing.T) {
			service := NewService(nil, manager, securityUserProvider{user: test.user}, nil)
			handler := middleware.Authenticator(service)(middleware.RequireAdmin(http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
				w.WriteHeader(http.StatusNoContent)
			})))
			request := httptest.NewRequest(http.MethodGet, "/admin", nil)
			request.Header.Set("Authorization", "Bearer "+token)
			recorder := httptest.NewRecorder()
			handler.ServeHTTP(recorder, request)
			if recorder.Code != test.status {
				t.Fatalf("got %d, want %d: %s", recorder.Code, test.status, recorder.Body.String())
			}
		})
	}
}
