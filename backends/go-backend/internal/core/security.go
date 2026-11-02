// AngelaMos | 2026
// security.go

package core

import (
	"crypto/rand"
	"crypto/sha256"
	"crypto/subtle"
	"encoding/base64"
	"encoding/hex"
	"fmt"
	"strings"

	"golang.org/x/crypto/argon2"
)

const (
	argonTime    = 1
	argonMemory  = 64 * 1024
	argonThreads = 4
	argonKeyLen  = 32
	saltLength   = 16
)

func HashPassword(password string) (string, error) {
	release, err := reservePasswordMemory(argonMemory)
	if err != nil {
		return "", err
	}
	defer release()

	salt := make([]byte, saltLength)
	if _, err := rand.Read(salt); err != nil {
		return "", fmt.Errorf("generate salt: %w", err)
	}

	hash := argon2.IDKey(
		[]byte(password),
		salt,
		argonTime,
		argonMemory,
		argonThreads,
		argonKeyLen,
	)

	b64Salt := base64.RawStdEncoding.EncodeToString(salt)
	b64Hash := base64.RawStdEncoding.EncodeToString(hash)

	encoded := fmt.Sprintf(
		"$argon2id$v=%d$m=%d,t=%d,p=%d$%s$%s",
		argon2.Version,
		argonMemory,
		argonTime,
		argonThreads,
		b64Salt,
		b64Hash,
	)

	return encoded, nil
}

func VerifyPassword(password, encodedHash string) (bool, error) {
	params, salt, hash, err := decodeHash(encodedHash)
	if err != nil {
		return false, err
	}
	release, err := reservePasswordMemory(params.memory)
	if err != nil {
		return false, err
	}
	defer release()

	otherHash := argon2.IDKey(
		[]byte(password),
		salt,
		params.time,
		params.memory,
		params.threads,
		params.keyLen,
	)

	if subtle.ConstantTimeCompare(hash, otherHash) == 1 {
		return true, nil
	}

	return false, nil
}

func VerifyPasswordWithRehash(
	password, encodedHash string,
) (bool, string, error) {
	valid, err := VerifyPassword(password, encodedHash)
	if err != nil {
		return false, "", err
	}

	if !valid {
		return false, "", nil
	}

	if needsRehash(encodedHash) {
		newHash, hashErr := HashPassword(password)
		if hashErr != nil {
			//nolint:nilerr // password verified successfully; rehash failure is non-critical
			return true, "", nil
		}
		return true, newHash, nil
	}

	return true, "", nil
}

var dummyHash string

func init() {
	hash, err := HashPassword("dummy_password_for_timing_attack_prevention")
	if err != nil {
		panic(fmt.Sprintf("security: failed to generate dummy hash: %v", err))
	}
	dummyHash = hash
}

func VerifyPasswordTimingSafe(
	password string,
	encodedHash *string,
) (bool, string, error) {
	hashToVerify := dummyHash
	if encodedHash != nil && *encodedHash != "" {
		hashToVerify = *encodedHash
	}

	valid, newHash, err := VerifyPasswordWithRehash(password, hashToVerify)
	if err != nil {
		return false, "", err
	}

	if encodedHash == nil || *encodedHash == "" {
		return false, "", nil
	}

	return valid, newHash, err
}

type argonParams struct {
	memory  uint32
	time    uint32
	threads uint8
	keyLen  uint32
}

func decodeHash(encodedHash string) (*argonParams, []byte, []byte, error) {
	if len(encodedHash) > 512 {
		return nil, nil, nil, fmt.Errorf("encoded hash exceeds the supported length")
	}
	parts := strings.Split(encodedHash, "$")
	if len(parts) != 6 {
		return nil, nil, nil, fmt.Errorf("invalid hash format")
	}

	if parts[1] != "argon2id" {
		return nil, nil, nil, fmt.Errorf("unsupported algorithm: %s", parts[1])
	}

	var version int
	_, err := fmt.Sscanf(parts[2], "v=%d", &version)
	if err != nil {
		return nil, nil, nil, fmt.Errorf("invalid version: %w", err)
	}

	if version != argon2.Version {
		return nil, nil, nil, fmt.Errorf("incompatible version: %d", version)
	}

	params := &argonParams{}
	_, err = fmt.Sscanf(
		parts[3],
		"m=%d,t=%d,p=%d",
		&params.memory,
		&params.time,
		&params.threads,
	)
	if err != nil {
		return nil, nil, nil, fmt.Errorf("invalid params: %w", err)
	}
	if params.threads == 0 || params.threads > 16 ||
		params.time == 0 || params.time > 10 ||
		params.memory < 8*uint32(params.threads) || params.memory > passwordMemoryBudget {
		return nil, nil, nil, fmt.Errorf("hash parameters exceed the supported resource bounds")
	}

	salt, err := base64.RawStdEncoding.DecodeString(parts[4])
	if err != nil {
		return nil, nil, nil, fmt.Errorf("decode salt: %w", err)
	}

	hash, err := base64.RawStdEncoding.DecodeString(parts[5])
	if err != nil {
		return nil, nil, nil, fmt.Errorf("decode hash: %w", err)
	}
	if len(salt) < 8 || len(salt) > 64 || len(hash) < 16 || len(hash) > 64 {
		return nil, nil, nil, fmt.Errorf("invalid salt or hash length")
	}

	//nolint:gosec // G115: hash length is always small (32 bytes for Argon2id)
	params.keyLen = uint32(len(hash))

	return params, salt, hash, nil
}

func needsRehash(encodedHash string) bool {
	params, _, _, err := decodeHash(encodedHash)
	if err != nil {
		return true
	}

	return params.memory != argonMemory ||
		params.time != argonTime ||
		params.threads != argonThreads ||
		params.keyLen != argonKeyLen
}

func GenerateSecureToken(length int) (string, error) {
	bytes := make([]byte, length)
	if _, err := rand.Read(bytes); err != nil {
		return "", fmt.Errorf("generate random bytes: %w", err)
	}
	return base64.URLEncoding.EncodeToString(bytes), nil
}

func GenerateRefreshToken() (string, error) {
	return GenerateSecureToken(32)
}

func HashToken(token string) string {
	hash := sha256.Sum256([]byte(token))
	return hex.EncodeToString(hash[:])
}

func CompareTokenHash(token, hash string) bool {
	tokenHash := HashToken(token)
	return subtle.ConstantTimeCompare([]byte(tokenHash), []byte(hash)) == 1
}
