// ©AngelaMos | 2026
// commands_test.go

package main

import (
	"bytes"
	"os"
	"path/filepath"
	"testing"
)

func TestInitializeKeysRecoversMissingPublicKey(t *testing.T) {
	directory := t.TempDir()
	if err := initializeKeys(directory); err != nil {
		t.Fatal(err)
	}
	privatePath := filepath.Join(directory, "private.pem")
	publicPath := filepath.Join(directory, "public.pem")
	privateBefore, err := os.ReadFile(privatePath)
	if err != nil {
		t.Fatal(err)
	}
	publicBefore, err := os.ReadFile(publicPath)
	if err != nil {
		t.Fatal(err)
	}
	if err := os.Remove(publicPath); err != nil {
		t.Fatal(err)
	}
	for range 2 {
		if err := initializeKeys(directory); err != nil {
			t.Fatal(err)
		}
	}
	privateAfter, err := os.ReadFile(privatePath)
	if err != nil {
		t.Fatal(err)
	}
	publicAfter, err := os.ReadFile(publicPath)
	if err != nil {
		t.Fatal(err)
	}
	if !bytes.Equal(privateBefore, privateAfter) || !bytes.Equal(publicBefore, publicAfter) {
		t.Fatal("initialization changed the signing identity")
	}
	info, err := os.Stat(privatePath)
	if err != nil || info.Mode().Perm() != 0600 {
		t.Fatal("private key must remain readable only by its owner")
	}
}

func TestInitializeKeysRejectsMismatchedPair(t *testing.T) {
	directory, other := t.TempDir(), t.TempDir()
	for _, path := range []string{directory, other} {
		if err := initializeKeys(path); err != nil {
			t.Fatal(err)
		}
	}
	wrongKey, err := os.ReadFile(filepath.Join(other, "public.pem"))
	if err != nil {
		t.Fatal(err)
	}
	publicPath := filepath.Join(directory, "public.pem")
	if err := os.WriteFile(publicPath, wrongKey, 0600); err != nil {
		t.Fatal(err)
	}
	if err := initializeKeys(directory); err == nil {
		t.Fatal("mismatched keys were accepted")
	}
	after, err := os.ReadFile(publicPath)
	if err != nil || !bytes.Equal(after, wrongKey) {
		t.Fatal("existing key was overwritten")
	}
}

func TestInitializeKeysRefusesDamagedPrivateKey(t *testing.T) {
	directory := t.TempDir()
	path := filepath.Join(directory, "private.pem")
	if err := os.WriteFile(path, []byte("interrupted legacy write"), 0600); err != nil {
		t.Fatal(err)
	}
	if err := initializeKeys(directory); err == nil {
		t.Fatal("damaged private key was accepted")
	}
	data, err := os.ReadFile(path)
	if err != nil || string(data) != "interrupted legacy write" {
		t.Fatal("damaged private key was replaced")
	}
}

func TestInitializeKeysRefusesPublicOnlyPair(t *testing.T) {
	directory := t.TempDir()
	if err := initializeKeys(directory); err != nil {
		t.Fatal(err)
	}
	path := filepath.Join(directory, "private.pem")
	if err := os.Remove(path); err != nil {
		t.Fatal(err)
	}
	if err := initializeKeys(directory); err == nil {
		t.Fatal("a replacement private key was created for an existing public key")
	}
	if _, err := os.Stat(path); !os.IsNotExist(err) {
		t.Fatal("initialization replaced the missing identity")
	}
}

func TestInitializeKeysConcurrently(t *testing.T) {
	directory := t.TempDir()
	results := make(chan error, 12)
	for range cap(results) {
		go func() { results <- initializeKeys(directory) }()
	}
	for range cap(results) {
		if err := <-results; err != nil {
			t.Fatal(err)
		}
	}
	if err := initializeKeys(directory); err != nil {
		t.Fatal(err)
	}
}
