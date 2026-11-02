/**
 * ©AngelaMos | 2026
 * shell.tsx
 */

import { Suspense } from 'react'
import { ErrorBoundary, type FallbackProps } from 'react-error-boundary'
import { Link, NavLink, Outlet, useLocation } from 'react-router-dom'
import { ROUTES } from '@/config'
import styles from './shell.module.scss'

function ShellErrorFallback({ error }: FallbackProps): React.ReactElement {
  return (
    <div role="alert">
      <h1>Unable to display this page</h1>
      <p>{error instanceof Error ? error.message : 'Please try again.'}</p>
    </div>
  )
}

export function Shell(): React.ReactElement {
  const location = useLocation()

  return (
    <div className={styles.shell}>
      <a className={styles.skip} href="#main-content">
        Skip to content
      </a>
      <header className={styles.header}>
        <Link to={ROUTES.HOME} className={styles.name}>
          {import.meta.env.VITE_APP_TITLE || 'Your project'}
        </Link>
        <nav aria-label="Main navigation" className={styles.nav}>
          <NavLink to={ROUTES.DASHBOARD}>Dashboard</NavLink>
          <NavLink to={ROUTES.SETTINGS}>Settings</NavLink>
        </nav>
      </header>
      <main id="main-content" className={styles.content} tabIndex={-1}>
        <ErrorBoundary
          FallbackComponent={ShellErrorFallback}
          resetKeys={[location.pathname]}
        >
          <Suspense fallback={<output>Loading...</output>}>
            <Outlet />
          </Suspense>
        </ErrorBoundary>
      </main>
    </div>
  )
}
