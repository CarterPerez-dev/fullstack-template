// ©AngelaMos | 2026
// commands.go

package main

import (
	"context"
	"crypto/ecdsa"
	"crypto/elliptic"
	"crypto/rand"
	"crypto/x509"
	"encoding/pem"
	"errors"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/go-playground/validator/v10"
	"github.com/google/uuid"

	"github.com/carterperez-dev/templates/go-backend/internal/auth"
	"github.com/carterperez-dev/templates/go-backend/internal/config"
	"github.com/carterperez-dev/templates/go-backend/internal/core"
	"github.com/carterperez-dev/templates/go-backend/internal/user"
)

func initializeKeys(directory string) error {
	privatePath := filepath.Join(directory, "private.pem")
	publicPath := filepath.Join(directory, "public.pem")
	if err := os.MkdirAll(directory, 0700); err != nil {
		return err
	}
	block, err := readKeyBlock(privatePath)
	if errors.Is(err, os.ErrNotExist) {
		if _, publicErr := os.Lstat(publicPath); publicErr == nil {
			block, err = readKeyBlock(privatePath)
			if err != nil {
				return errors.New("public key exists without a readable private key; restore the matching private key")
			}
		} else if !errors.Is(publicErr, os.ErrNotExist) {
			return publicErr
		} else {
			key, generateErr := ecdsa.GenerateKey(elliptic.P256(), rand.Reader)
			if generateErr != nil {
				return generateErr
			}
			der, marshalErr := x509.MarshalECPrivateKey(key)
			if marshalErr != nil {
				return marshalErr
			}
			writeErr := publishKey(privatePath, "EC PRIVATE KEY", der)
			if writeErr != nil && !errors.Is(writeErr, os.ErrExist) {
				return writeErr
			}
			block, err = readKeyBlock(privatePath)
		}
	}
	if err != nil {
		return err
	}
	key, err := x509.ParseECPrivateKey(block.Bytes)
	if err != nil || key.Curve != elliptic.P256() {
		return errors.New("private key must be a valid P-256 EC key")
	}
	publicDER, err := x509.MarshalPKIXPublicKey(&key.PublicKey)
	if err != nil {
		return err
	}
	publicBlock, err := readKeyBlock(publicPath)
	if errors.Is(err, os.ErrNotExist) {
		writeErr := publishKey(publicPath, "PUBLIC KEY", publicDER)
		if writeErr != nil && !errors.Is(writeErr, os.ErrExist) {
			return writeErr
		}
		publicBlock, err = readKeyBlock(publicPath)
	}
	if err != nil {
		return err
	}
	publicKey, err := x509.ParsePKIXPublicKey(publicBlock.Bytes)
	if err != nil || !key.PublicKey.Equal(publicKey) {
		return errors.New("public key does not match the existing private key")
	}
	return nil
}

func readKeyBlock(path string) (*pem.Block, error) {
	info, err := os.Lstat(path)
	if err != nil {
		return nil, err
	}
	if !info.Mode().IsRegular() || info.Size() > 16384 {
		return nil, fmt.Errorf("key must be a regular PEM file no larger than 16 KiB: %s", path)
	}
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}
	block, rest := pem.Decode(data)
	if block == nil || len(strings.TrimSpace(string(rest))) != 0 {
		return nil, fmt.Errorf("invalid PEM key: %s", path)
	}
	return block, nil
}

func publishKey(path, kind string, data []byte) error {
	file, err := os.CreateTemp(filepath.Dir(path), ".key-*.pem")
	if err != nil {
		return err
	}
	defer os.Remove(file.Name())
	encodeErr := pem.Encode(file, &pem.Block{Type: kind, Bytes: data})
	syncErr := file.Sync()
	closeErr := file.Close()
	if err := errors.Join(encodeErr, syncErr, closeErr); err != nil {
		return err
	}
	if err := os.Link(file.Name(), path); err != nil {
		return err
	}
	directory, err := os.Open(filepath.Dir(path))
	if err != nil {
		return err
	}
	return errors.Join(directory.Sync(), directory.Close())
}

func checkHealth() error {
	client := &http.Client{Timeout: 4 * time.Second}
	response, err := client.Get("http://127.0.0.1:8080/readyz")
	if err != nil {
		return err
	}
	defer response.Body.Close()
	if response.StatusCode != http.StatusOK {
		return fmt.Errorf("readiness returned HTTP %d", response.StatusCode)
	}
	return nil
}

func runMigrations(configPath string) error {
	cfg, err := config.Load(configPath)
	if err != nil {
		return err
	}
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Minute)
	defer cancel()
	db, err := core.NewDatabase(ctx, cfg.Database)
	if err != nil {
		return err
	}
	defer db.Close()
	return core.Migrate(ctx, db.DB, "migrations")
}

func createAdministrator(configPath, email string) error {
	input, err := os.Stdin.Stat()
	if err != nil {
		return err
	}
	if input.Mode()&os.ModeCharDevice != 0 {
		return errors.New("provide the password on standard input from a hidden prompt or password manager")
	}
	data, err := io.ReadAll(io.LimitReader(os.Stdin, 515))
	if err != nil {
		return err
	}
	request := auth.RegisterRequest{
		Email:    strings.ToLower(strings.TrimSpace(email)),
		Password: strings.TrimSuffix(strings.TrimSuffix(string(data), "\n"), "\r"),
	}
	if err := validator.New().Struct(request); err != nil {
		return errors.New(core.FormatValidationError(err))
	}
	passwordHash, err := core.HashPassword(request.Password)
	if err != nil {
		return err
	}
	cfg, err := config.Load(configPath)
	if err != nil {
		return err
	}
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()
	db, err := core.NewDatabase(ctx, cfg.Database)
	if err != nil {
		return err
	}
	defer db.Close()
	account := &user.User{
		ID: uuid.NewString(), Email: request.Email, PasswordHash: passwordHash,
		Role: user.RoleAdmin, Tier: user.TierFree,
	}
	if err := user.NewRepository(db.DB).Create(ctx, account); err != nil {
		return fmt.Errorf("create administrator without replacing existing accounts: %w", err)
	}
	fmt.Println("Administrator created")
	return nil
}
