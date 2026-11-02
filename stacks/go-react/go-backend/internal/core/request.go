// ©AngelaMos | 2026
// request.go

package core

import (
	"encoding/json"
	"errors"
	"io"
	"net/http"
)

const MaxJSONBodyBytes = 1 << 20

func DecodeJSON(r *http.Request, target any) error {
	if r.ContentLength > MaxJSONBodyBytes {
		return requestBodyTooLarge()
	}
	decoder := json.NewDecoder(http.MaxBytesReader(nil, r.Body, MaxJSONBodyBytes))
	if err := decoder.Decode(target); err != nil {
		return requestBodyError(err)
	}
	var trailing any
	if err := decoder.Decode(&trailing); !errors.Is(err, io.EOF) {
		if err != nil {
			return requestBodyError(err)
		}
		return ValidationError("request body must contain a single JSON value")
	}
	return nil
}

func requestBodyError(err error) error {
	var limitError *http.MaxBytesError
	if errors.As(err, &limitError) {
		return requestBodyTooLarge()
	}
	return ValidationError("invalid request body")
}

func requestBodyTooLarge() error {
	return NewAppError(
		ErrInvalidInput,
		"request body exceeds the 1 MiB limit",
		http.StatusRequestEntityTooLarge,
		"BODY_TOO_LARGE",
	)
}
