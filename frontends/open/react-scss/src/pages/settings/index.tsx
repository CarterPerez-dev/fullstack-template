/**
 * ©AngelaMos | 2026
 * index.tsx
 */

import styles from './settings.module.scss'

const AVAILABLE_STORES = [
  {
    name: 'useUIStore()',
    file: 'core/lib/shell.ui.store.ts',
    description: 'Theme, sidebar open/collapsed state',
  },
]

export function Component(): React.ReactElement {
  return (
    <div className={styles.page}>
      <div className={styles.container}>
        <div className={styles.header}>
          <h1 className={styles.title}>Settings</h1>
          <p className={styles.subtitle}>
            Template page — available stores for building your settings UI
          </p>
        </div>

        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>Available Stores</h2>
          <div className={styles.grid}>
            {AVAILABLE_STORES.map((store) => (
              <div key={store.name} className={styles.card}>
                <code className={styles.hookName}>{store.name}</code>
                <p className={styles.description}>{store.description}</p>
                <div className={styles.meta}>
                  <span className={styles.file}>{store.file}</span>
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>Suggested Features</h2>
          <ul className={styles.list}>
            <li>Profile form</li>
            <li>Theme toggle (dark/light)</li>
            <li>Notification settings</li>
            <li>Application preferences</li>
          </ul>
        </section>
      </div>
    </div>
  )
}

Component.displayName = 'Settings'
