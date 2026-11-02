/**
 * ©AngelaMos | 2026
 * index.tsx
 */

import { useUser } from '@/core/lib'
import styles from './dashboard.module.scss'

export function Component(): React.ReactElement {
  const user = useUser()

  return (
    <section className={styles.page}>
      <h1>Dashboard</h1>
      <p>Signed in as {user?.email}.</p>
      <dl>
        <dt>Name</dt>
        <dd>{user?.full_name || 'Not set'}</dd>
        <dt>Role</dt>
        <dd>{user?.role}</dd>
      </dl>
    </section>
  )
}

Component.displayName = 'Dashboard'
