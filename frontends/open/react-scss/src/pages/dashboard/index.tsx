/**
 * ©AngelaMos | 2026
 * index.tsx
 */

import styles from './dashboard.module.scss'

const AVAILABLE_STORES = [
  {
    name: 'useUIStore()',
    file: 'core/lib/shell.ui.store.ts',
    description: 'Theme, sidebar open/collapsed state',
  },
]

const SUGGESTED_FEATURES = [
  'Stats and metrics',
  'Recent activity feed',
  'Quick actions',
  'Charts and analytics',
  'Notifications overview',
  'Task/project summary',
]

export function Component(): React.ReactElement {
  return (
    <div className={styles.page}>
      <div className={styles.container}>
        <div className={styles.header}>
          <h1 className={styles.title}>Welcome</h1>
          <p className={styles.subtitle}>
            Template page — build your dashboard here
          </p>
        </div>

        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>Available Stores</h2>
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
          <h2 className={styles.sectionTitle}>Suggested Features</h2>
          <ul className={styles.list}>
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
