/**
 * ©AngelaMos | 2026
 * index.tsx
 */

import { Link } from 'react-router-dom'
import { ROUTES } from '@/config'
import styles from './landing.module.scss'

export function Component(): React.ReactElement {
  return (
    <main className={styles.page}>
      <h1>{import.meta.env.VITE_APP_TITLE || 'Your project'}</h1>
      <p>A starting point for your application.</p>
      <nav className={styles.actions} aria-label="Get started">
        <Link to={ROUTES.LOGIN}>Sign in</Link>
        <Link to={ROUTES.REGISTER}>Create an account</Link>
      </nav>
    </main>
  )
}

Component.displayName = 'Landing'
