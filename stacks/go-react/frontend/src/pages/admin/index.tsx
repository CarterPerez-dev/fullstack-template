/**
 * ©AngelaMos | 2026
 * index.tsx
 */

import { useState } from 'react'
import {
  useAdminDeleteUser,
  useAdminUpdateUser,
  useAdminUsers,
} from '@/api/hooks'
import { useUser } from '@/core/lib'
import styles from './admin.module.scss'

export function Component(): React.ReactElement {
  const [page, setPage] = useState(1)
  const currentUser = useUser()
  const users = useAdminUsers({ page, size: 20 })
  const update = useAdminUpdateUser()
  const remove = useAdminDeleteUser()
  const busy = update.isPending || remove.isPending

  return (
    <section className={styles.page}>
      <h1>Users</h1>
      {users.isPending && <output>Loading users...</output>}
      {users.isError && <p role="alert">{users.error.message}</p>}
      <div className={styles.tableWrapper}>
        <table>
          <thead>
            <tr>
              <th>Email</th>
              <th>Name</th>
              <th>Role</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.data?.items.map((user) => (
              <tr key={user.id}>
                <td>{user.email}</td>
                <td>{user.full_name || 'Unnamed'}</td>
                <td>{user.role}</td>
                <td>
                  <button
                    type="button"
                    disabled={busy || user.id === currentUser?.id}
                    onClick={() => {
                      const role = user.role === 'admin' ? 'user' : 'admin'
                      if (window.confirm(`Change ${user.email} to ${role}?`)) {
                        update.mutate({ id: user.id, role })
                      }
                    }}
                  >
                    Change role
                  </button>
                  <button
                    type="button"
                    disabled={busy || user.role === 'admin'}
                    onClick={() => {
                      if (
                        window.confirm(`Delete the account for ${user.email}?`)
                      ) {
                        remove.mutate(user.id)
                      }
                    }}
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {users.data?.total === 0 && <p>No users yet.</p>}
      <nav aria-label="User pages">
        <button
          type="button"
          disabled={page === 1}
          onClick={() => setPage(page - 1)}
        >
          Previous
        </button>
        <span>Page {page}</span>
        <button
          type="button"
          disabled={!users.data || page * 20 >= users.data.total}
          onClick={() => setPage(page + 1)}
        >
          Next
        </button>
      </nav>
    </section>
  )
}
