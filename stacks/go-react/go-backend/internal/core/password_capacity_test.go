// ©AngelaMos | 2026
// password_capacity_test.go

package core

import (
	"errors"
	"fmt"
	"strings"
	"sync"
	"sync/atomic"
	"testing"
)

func TestPasswordWorkRejectsSaturationAndRecovers(t *testing.T) {
	func() {
		release, err := reservePasswordMemory(passwordMemoryBudget)
		if err != nil {
			t.Fatal(err)
		}
		defer release()
		if _, err := HashPassword("valid-password"); !errors.Is(err, ErrPasswordCapacity) {
			t.Fatalf("hash bypassed capacity: %v", err)
		}
		if _, err := VerifyPassword("valid-password", dummyHash); !errors.Is(err, ErrPasswordCapacity) {
			t.Fatalf("verification bypassed capacity: %v", err)
		}
		if _, _, err := VerifyPasswordTimingSafe("valid-password", nil); !errors.Is(err, ErrPasswordCapacity) {
			t.Fatalf("missing-user verification discarded capacity failure: %v", err)
		}
	}()
	hash, err := HashPassword("valid-password")
	if err != nil {
		t.Fatal(err)
	}
	for password, want := range map[string]bool{"valid-password": true, "wrong-password": false} {
		valid, err := VerifyPassword(password, hash)
		if err != nil || valid != want {
			t.Fatalf("password verification failed after capacity was released: %v", err)
		}
	}
	release, err := reservePasswordMemory(passwordMemoryBudget)
	if err != nil {
		t.Fatalf("password operation leaked its reservation: %v", err)
	}
	release()
}

func TestPasswordMemoryReservationsAreConcurrentAndBounded(t *testing.T) {
	var attempted, finished sync.WaitGroup
	var accepted atomic.Int32
	gate := make(chan struct{})
	for range 20 {
		attempted.Add(1)
		finished.Add(1)
		go func() {
			defer finished.Done()
			release, err := reservePasswordMemory(argonMemory)
			if err == nil {
				accepted.Add(1)
				defer release()
			}
			attempted.Done()
			<-gate
		}()
	}
	attempted.Wait()
	count := accepted.Load()
	close(gate)
	finished.Wait()
	if count != 2 {
		t.Fatalf("expected two 64 MiB reservations, got %d", count)
	}
	release, err := reservePasswordMemory(passwordMemoryBudget)
	if err != nil {
		t.Fatal("concurrent reservations were not released")
	}
	release()
}

func TestInvalidHashParametersCannotReachArgon(t *testing.T) {
	parts := strings.Split(dummyHash, "$")
	for _, params := range []string{
		"m=65536,t=0,p=4", "m=65536,t=1,p=0", "m=0,t=1,p=4",
		"m=131073,t=1,p=4", "m=65536,t=11,p=4", "m=65536,t=1,p=17",
	} {
		t.Run(params, func(t *testing.T) {
			hash := fmt.Sprintf("$argon2id$v=19$%s$%s$%s", params, parts[4], parts[5])
			if _, err := VerifyPassword("password", hash); err == nil {
				t.Fatal("unsafe parameters were accepted")
			}
		})
	}
	for _, hash := range []string{
		strings.Repeat("x", 513),
		"$argon2id$v=19$m=65536,t=1,p=4$c2hvcnQ$c2hvcnQ",
		"$argon2id$v=19$m=65536,t=1,p=4$$",
	} {
		if _, err := VerifyPassword("password", hash); err == nil {
			t.Fatal("invalid stored hash was accepted")
		}
	}
}
