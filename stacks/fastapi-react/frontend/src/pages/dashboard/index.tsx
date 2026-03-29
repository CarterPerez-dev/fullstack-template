/**
 * ©AngelaMos | 2026
 * index.tsx
 */

import { useUser } from '@/core/lib'
import styles from './dashboard.module.scss'

const AVAILABLE_STORES = [
  {
    name: 'useUser()',
    file: 'core/lib/auth.store.ts',
    description: 'Get current authenticated user',
  },
  {
    name: 'useIsAuthenticated()',
    file: 'core/lib/auth.store.ts',
    description: 'Check if user is logged in',
  },
  {
    name: 'useIsAdmin()',
    file: 'core/lib/auth.store.ts',
    description: 'Check if user has admin role',
  },
]

const SUGGESTED_FEATURES = [
  'User stats and metrics',
  'Recent activity feed',
  'Quick actions',
  'Charts and analytics',
  'Notifications overview',
  'Task/project summary',
]

export function Component(): React.ReactElement {
  const user = useUser()

  return (
    <div className={styles.page}>
      <div className={styles.container}>
        <div className={styles.header}>
          <div className={styles.headerMeta}>
            <span className={styles.tag}>Operations Overview</span>
            <span className={styles.tag}>Status: Online</span>
          </div>
          <h1 className={styles.title}>
            Welcome{user?.full_name ? `, ${user.full_name}` : ''}
          </h1>
          <p className={styles.subtitle}>
            Template page — build your dashboard here
          </p>
        </div>

        <div className={styles.userBar}>
          <div className={styles.avatar}>
            {user?.full_name?.[0]?.toUpperCase() ??
              user?.email?.[0]?.toUpperCase() ??
              'U'}
          </div>
          <div className={styles.userMeta}>
            <span className={styles.metaLabel}>Email</span>
            <span className={styles.metaValue}>{user?.email}</span>
          </div>
          <div className={styles.userMeta}>
            <span className={styles.metaLabel}>Role</span>
            <span className={styles.metaValue}>{user?.role}</span>
          </div>
          <div className={styles.userMeta}>
            <span className={styles.metaLabel}>Name</span>
            <span className={styles.metaValue}>
              {user?.full_name ?? '\u2014'}
            </span>
          </div>
        </div>

        <section className={styles.section}>
          <span className={styles.sectionLabel}>Available Stores</span>
          <div className={styles.grid}>
            {AVAILABLE_STORES.map((store) => (
              <div key={store.name} className={styles.card}>
                <code className={styles.hookName}>{store.name}</code>
                <p className={styles.description}>{store.description}</p>
                <span className={styles.file}>{store.file}</span>
              </div>
            ))}
          </div>
        </section>

        <section className={styles.section}>
          <span className={styles.sectionLabel}>Suggested Features</span>
          <ul className={styles.featureList}>
            {SUGGESTED_FEATURES.map((feature) => (
              <li key={feature}>{feature}</li>
            ))}
          </ul>
        </section>
      </div>
    </div>
  )
}

Component.displayName = 'Dashboard'
