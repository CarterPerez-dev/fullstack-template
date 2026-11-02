// ©AngelaMos | 2026
// request_limits_test.go

package auth

import (
	"fmt"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"github.com/carterperez-dev/templates/go-backend/internal/core"
)

func TestAuthHandlersRejectLargeBodiesBeforeServiceWork(t *testing.T) {
	handler := NewHandler(nil, false)
	for name, handle := range map[string]http.HandlerFunc{
		"login": handler.Login, "register": handler.Register, "refresh": handler.Refresh,
	} {
		t.Run(name, func(t *testing.T) {
			body := `{"padding":"` + strings.Repeat("x", core.MaxJSONBodyBytes) + `"}`
			r := httptest.NewRequest(http.MethodPost, "/", strings.NewReader(body))
			r.ContentLength = -1
			w := httptest.NewRecorder()
			handle(w, r)
			if w.Code != http.StatusRequestEntityTooLarge {
				t.Fatalf("oversized body returned %d", w.Code)
			}
		})
	}
}

func TestLoginRejectsTrailingJSONBeforeServiceWork(t *testing.T) {
	r := httptest.NewRequest(http.MethodPost, "/", strings.NewReader(
		`{"email":"owner@example.com","password":"long-password"} {}`,
	))
	w := httptest.NewRecorder()
	NewHandler(nil, false).Login(w, r)
	if w.Code != http.StatusBadRequest {
		t.Fatalf("trailing JSON returned %d", w.Code)
	}
}

func TestPasswordCapacityResponseIsRetryable(t *testing.T) {
	w := httptest.NewRecorder()
	if !writePasswordCapacityError(w, fmt.Errorf("verify password: %w", core.ErrPasswordCapacity)) {
		t.Fatal("wrapped capacity failure was not handled")
	}
	if w.Code != http.StatusServiceUnavailable || w.Header().Get("Retry-After") != "1" {
		t.Fatal("capacity failure did not return a retryable response")
	}
	w = httptest.NewRecorder()
	if writePasswordCapacityError(w, ErrInvalidCredentials) || w.Body.Len() != 0 {
		t.Fatal("credential failures were converted to capacity failures")
	}
}
