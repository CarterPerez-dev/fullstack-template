// ©AngelaMos | 2026
// browser.go

package auth

import (
	"net/http"
	"time"

	"github.com/carterperez-dev/templates/go-backend/internal/core"
)

func browserTransport(r *http.Request) bool {
	return r.Header.Get("X-Auth-Transport") == "cookie"
}

func readRefreshRequest(r *http.Request) (RefreshRequest, error) {
	var request RefreshRequest
	if browserTransport(r) {
		cookie, err := r.Cookie("refresh_token")
		if err != nil {
			return request, err
		}
		request.RefreshToken = cookie.Value
		return request, nil
	}
	err := core.DecodeJSON(r, &request)
	return request, err
}

func (h *Handler) setBrowserSession(w http.ResponseWriter, r *http.Request, response *AuthResponse) {
	w.Header().Set("Cache-Control", "no-store")
	if !browserTransport(r) {
		return
	}
	http.SetCookie(w, &http.Cookie{
		Name:     "refresh_token",
		Value:    response.Tokens.RefreshToken,
		Path:     "/",
		HttpOnly: true,
		Secure:   h.secureCookies,
		SameSite: http.SameSiteLaxMode,
		MaxAge:   int(h.service.jwt.config.RefreshTokenExpire / time.Second),
	})
	response.Tokens.RefreshToken = ""
}

func (h *Handler) clearBrowserSession(w http.ResponseWriter) {
	http.SetCookie(w, &http.Cookie{
		Name:     "refresh_token",
		Path:     "/",
		HttpOnly: true,
		Secure:   h.secureCookies,
		SameSite: http.SameSiteLaxMode,
		MaxAge:   -1,
	})
}
