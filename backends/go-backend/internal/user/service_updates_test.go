// ©AngelaMos | 2026
// service_updates_test.go

package user

import (
	"context"
	"testing"
)

type staleUserRepository struct {
	Repository
	stored User
	stale  User
}

func (r *staleUserRepository) GetByID(context.Context, string) (*User, error) {
	copy := r.stale
	return &copy, nil
}

func (r *staleUserRepository) Update(_ context.Context, account *User) error {
	r.stored.Name = account.Name
	r.stored.Role = account.Role
	r.stored.Tier = account.Tier
	return nil
}

func (r *staleUserRepository) UpdateName(_ context.Context, _ string, name *string) (*User, error) {
	if name != nil {
		r.stored.Name = *name
	}
	return &r.stored, nil
}

func (r *staleUserRepository) UpdateRole(_ context.Context, _, role string) (*User, error) {
	r.stored.Role = role
	return &r.stored, nil
}

func (r *staleUserRepository) UpdateTier(_ context.Context, _, tier string) (*User, error) {
	r.stored.Tier = tier
	return &r.stored, nil
}

func TestUpdatesDoNotRestoreStaleUserAttributes(t *testing.T) {
	name := "New name"
	cases := []struct {
		name   string
		update func(*Service) (*User, error)
		want   User
	}{
		{"profile", func(s *Service) (*User, error) {
			return s.UpdateMe(t.Context(), "user-id", UpdateUserRequest{Name: &name})
		}, User{Name: name, Role: RoleUser, Tier: TierFree}},
		{"empty profile", func(s *Service) (*User, error) {
			return s.UpdateMe(t.Context(), "user-id", UpdateUserRequest{})
		}, User{Name: "Current name", Role: RoleUser, Tier: TierFree}},
		{"role", func(s *Service) (*User, error) {
			return s.UpdateUserRole(t.Context(), "user-id", RoleAdmin)
		}, User{Name: "Current name", Role: RoleAdmin, Tier: TierFree}},
		{"tier", func(s *Service) (*User, error) {
			return s.UpdateUserTier(t.Context(), "user-id", TierEnterprise)
		}, User{Name: "Current name", Role: RoleUser, Tier: TierEnterprise}},
	}
	for _, test := range cases {
		t.Run(test.name, func(t *testing.T) {
			repo := &staleUserRepository{
				stored: User{Name: "Current name", Role: RoleUser, Tier: TierFree},
				stale:  User{Name: "Old name", Role: RoleAdmin, Tier: TierPro},
			}
			result, err := test.update(NewService(repo))
			if err != nil {
				t.Fatal(err)
			}
			if repo.stored.Name != test.want.Name || repo.stored.Role != test.want.Role || repo.stored.Tier != test.want.Tier {
				t.Fatalf("update overwrote other attributes: %+v", repo.stored)
			}
			if result.Name != test.want.Name || result.Role != test.want.Role || result.Tier != test.want.Tier {
				t.Fatalf("response returned stale attributes: %+v", result)
			}
		})
	}
}
