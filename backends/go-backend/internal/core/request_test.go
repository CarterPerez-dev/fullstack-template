// ©AngelaMos | 2026
// request_test.go

package core

import (
	"io"
	"net/http/httptest"
	"strings"
	"testing"
)

type countingBody struct {
	io.Reader
	bytesRead int
}

func (b *countingBody) Read(data []byte) (int, error) {
	n, err := b.Reader.Read(data)
	b.bytesRead += n
	return n, err
}

func TestDecodeJSONBoundsAndTrailingInput(t *testing.T) {
	large := `{"value":"` + strings.Repeat("x", MaxJSONBodyBytes) + `"}`
	for _, tc := range []struct {
		name    string
		body    string
		unknown bool
		status  int
	}{
		{"valid", `{"value":"ok"}`, false, 0},
		{"whitespace", "{\"value\":\"ok\"}\n ", true, 0},
		{"empty", "", true, 400},
		{"truncated", `{"value":`, true, 400},
		{"second value", `{"value":"ok"} {}`, true, 400},
		{"trailing junk", `{"value":"ok"} junk`, true, 400},
		{"known length", large, false, 413},
		{"unknown length", large, true, 413},
		{"oversized whitespace", `{}` + strings.Repeat(" ", MaxJSONBodyBytes), true, 413},
	} {
		t.Run(tc.name, func(t *testing.T) {
			body := &countingBody{Reader: strings.NewReader(tc.body)}
			r := httptest.NewRequest("POST", "/", body)
			if tc.unknown {
				r.ContentLength = -1
			} else {
				r.ContentLength = int64(len(tc.body))
			}
			var value struct {
				Value string `json:"value"`
			}
			err := DecodeJSON(r, &value)
			if tc.status == 0 {
				if err != nil || value.Value != "ok" {
					t.Fatalf("valid body rejected: %v", err)
				}
			} else if err == nil || GetAppError(err).StatusCode != tc.status {
				t.Fatalf("expected status %d, got %v", tc.status, err)
			}
			if body.bytesRead > MaxJSONBodyBytes+1 {
				t.Fatalf("read %d bytes beyond the body bound", body.bytesRead)
			}
		})
	}
}
