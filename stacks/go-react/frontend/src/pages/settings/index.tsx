/**
 * ©AngelaMos | 2026
 * index.tsx
 */

import { useChangePassword, useLogoutAll, useUpdateProfile } from '@/api/hooks'
import { ROUTES } from '@/config'
import { useAuthStore, useUser } from '@/core/lib'

export function Component(): React.ReactElement {
  const user = useUser()
  const profile = useUpdateProfile()
  const password = useChangePassword()
  const sessions = useLogoutAll()

  return (
    <section>
      <h1>Settings</h1>
      <h2>Profile</h2>
      <form
        onSubmit={(event) => {
          event.preventDefault()
          const data = new FormData(event.currentTarget)
          profile.mutate({ full_name: String(data.get('full_name')) })
        }}
      >
        <label>
          Name
          <input
            name="full_name"
            autoComplete="name"
            defaultValue={user?.full_name ?? ''}
            maxLength={100}
            required
          />
        </label>
        <button type="submit" disabled={profile.isPending}>
          {profile.isPending ? 'Saving...' : 'Save profile'}
        </button>
        {profile.error && <p role="alert">{profile.error.message}</p>}
      </form>
      <h2>Password</h2>
      <p>Changing your password signs you out on every device.</p>
      <form
        onSubmit={(event) => {
          event.preventDefault()
          const data = new FormData(event.currentTarget)
          password.mutate(
            {
              current_password: String(data.get('current_password')),
              new_password: String(data.get('new_password')),
            },
            {
              onSuccess: () => {
                useAuthStore.getState().logout()
                window.location.href = ROUTES.LOGIN
              },
            }
          )
        }}
      >
        <label>
          Current password
          <input
            name="current_password"
            type="password"
            autoComplete="current-password"
            required
          />
        </label>
        <label>
          New password
          <input
            name="new_password"
            type="password"
            autoComplete="new-password"
            minLength={12}
            maxLength={128}
            required
          />
        </label>
        <button type="submit" disabled={password.isPending}>
          {password.isPending ? 'Updating...' : 'Change password'}
        </button>
        {password.error && <p role="alert">{password.error.message}</p>}
      </form>
      <h2>Sessions</h2>
      <button
        type="button"
        disabled={sessions.isPending}
        onClick={() => sessions.mutate()}
      >
        Log out everywhere
      </button>
      {sessions.error && <p role="alert">{sessions.error.message}</p>}
    </section>
  )
}

Component.displayName = 'Settings'
