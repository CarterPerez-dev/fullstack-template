// ©AngelaMos | 2026
// jwt_keyid_test.go

package auth

import (
	"crypto"
	"encoding/base64"
	"net/http"
	"net/http/httptest"
	"path/filepath"
	"testing"
	"time"

	"github.com/lestrrat-go/jwx/v3/jwk"
	"github.com/lestrrat-go/jwx/v3/jwt"

	"github.com/carterperez-dev/templates/go-backend/internal/config"
)

func keyIDTestManager(t *testing.T) *JWTManager {
	t.Helper()
	directory := t.TempDir()
	privatePath := filepath.Join(directory, "private.pem")
	publicPath := filepath.Join(directory, "public.pem")
	if err := GenerateKeyPair(privatePath, publicPath); err != nil {
		t.Fatal(err)
	}
	manager, err := NewJWTManager(config.JWTConfig{
		PrivateKeyPath: privatePath, PublicKeyPath: publicPath,
		Issuer: "key-id-test", Audience: "key-id-test",
		AccessTokenExpire: time.Minute,
	})
	if err != nil {
		t.Fatal(err)
	}
	return manager
}

func TestCachedJWKSVerifiesTokensAfterRestart(t *testing.T) {
	manager := keyIDTestManager(t)
	thumbprint, err := manager.GetPublicKey().Thumbprint(crypto.SHA256)
	if err != nil {
		t.Fatal(err)
	}
	if manager.GetKeyID() != base64.RawURLEncoding.EncodeToString(thumbprint) {
		t.Fatal("key ID does not match the public key thumbprint")
	}
	recorder := httptest.NewRecorder()
	manager.GetJWKSHandler().ServeHTTP(recorder, httptest.NewRequest(http.MethodGet, "/.well-known/jwks.json", nil))
	if recorder.Code != http.StatusOK {
		t.Fatalf("JWKS response: %d", recorder.Code)
	}
	cachedKeys, err := jwk.Parse(recorder.Body.Bytes())
	if err != nil {
		t.Fatal(err)
	}
	restarted, err := NewJWTManager(manager.config)
	if err != nil {
		t.Fatal(err)
	}
	if manager.GetKeyID() != restarted.GetKeyID() {
		t.Fatal("restarting with the same signing key changed its ID")
	}
	token, err := restarted.CreateAccessToken(AccessTokenClaims{
		UserID: "test-user", Role: "user", Tier: "free", TokenVersion: 1,
	})
	if err != nil {
		t.Fatal(err)
	}
	if _, err := jwt.Parse([]byte(token), jwt.WithKeySet(cachedKeys), jwt.WithIssuer(manager.config.Issuer), jwt.WithAudience(manager.config.Audience)); err != nil {
		t.Fatalf("cached JWKS cannot verify a token after restart: %v", err)
	}
}

func TestChangingSigningKeyChangesKeyID(t *testing.T) {
	first := keyIDTestManager(t)
	second := keyIDTestManager(t)
	if first.GetKeyID() == second.GetKeyID() {
		t.Fatal("different signing keys have the same ID")
	}
	token, err := first.CreateAccessToken(AccessTokenClaims{
		UserID: "test-user", Role: "user", Tier: "free", TokenVersion: 1,
	})
	if err != nil {
		t.Fatal(err)
	}
	if _, err := second.VerifyAccessToken(t.Context(), token); err == nil {
		t.Fatal("a token signed by an unrelated key was accepted")
	}
}
