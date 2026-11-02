// ©AngelaMos | 2026
// password_capacity.go

package core

import (
	"errors"
	"sync"
)

const passwordMemoryBudget = 128 * 1024

var ErrPasswordCapacity = errors.New("password processing capacity exhausted")

var passwordMemoryMu sync.Mutex
var activePasswordMemory uint32

func reservePasswordMemory(memory uint32) (func(), error) {
	passwordMemoryMu.Lock()
	defer passwordMemoryMu.Unlock()
	if memory > passwordMemoryBudget || activePasswordMemory > passwordMemoryBudget-memory {
		return nil, ErrPasswordCapacity
	}
	activePasswordMemory += memory
	return func() {
		passwordMemoryMu.Lock()
		activePasswordMemory -= memory
		passwordMemoryMu.Unlock()
	}, nil
}
