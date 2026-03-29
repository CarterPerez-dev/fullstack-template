/**
 * ©AngelaMos | 2026
 * shell.tsx
 */

import { Suspense } from 'react'
import { ErrorBoundary } from 'react-error-boundary'
import { GiCardAceClubs, GiCardJoker } from 'react-icons/gi'
import { LuChevronLeft, LuChevronRight, LuMenu } from 'react-icons/lu'
import { NavLink, Outlet, useLocation } from 'react-router-dom'
import { ROUTES } from '@/config'
import { useUIStore } from '@/core/lib'
import styles from './shell.module.scss'

const NAV_ITEMS = [
  { path: ROUTES.DASHBOARD, label: 'Dashboard', icon: GiCardJoker },
  { path: ROUTES.SETTINGS, label: 'Settings', icon: GiCardAceClubs },
]

function ShellErrorFallback({ error }: { error: Error }): React.ReactElement {
  return (
    <div className={styles.error}>
      <h2>Something went wrong</h2>
      <pre>{error.message}</pre>
    </div>
  )
}

function ShellLoading(): React.ReactElement {
  return <div className={styles.loading}>Loading...</div>
}

function getPageTitle(pathname: string): string {
  const item = NAV_ITEMS.find((i) => i.path === pathname)
  return item?.label ?? 'Dashboard'
}

export function Shell(): React.ReactElement {
  const location = useLocation()
  const { sidebarOpen, sidebarCollapsed, toggleSidebar, toggleSidebarCollapsed } =
    useUIStore()

  const pageTitle = getPageTitle(location.pathname)

  return (
    <div className={styles.shell}>
      <aside
        className={`${styles.sidebar} ${sidebarOpen ? styles.open : ''} ${sidebarCollapsed ? styles.collapsed : ''}`}
      >
        <div className={styles.sidebarHeader}>
          <span className={styles.logo}>NavBar Template</span>
          <button
            type="button"
            className={styles.collapseBtn}
            onClick={toggleSidebarCollapsed}
            aria-label={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {sidebarCollapsed ? <LuChevronRight /> : <LuChevronLeft />}
          </button>
        </div>

        <nav className={styles.nav}>
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `${styles.navItem} ${isActive ? styles.active : ''}`
              }
              onClick={() => sidebarOpen && toggleSidebar()}
            >
              <item.icon className={styles.navIcon} />
              <span className={styles.navLabel}>{item.label}</span>
            </NavLink>
          ))}
        </nav>
      </aside>

      {sidebarOpen && (
        <button
          type="button"
          className={styles.overlay}
          onClick={toggleSidebar}
          onKeyDown={(e) => e.key === 'Escape' && toggleSidebar()}
          aria-label="Close sidebar"
        />
      )}

      <div
        className={`${styles.main} ${sidebarCollapsed ? styles.collapsed : ''}`}
      >
        <header className={styles.header}>
          <div className={styles.headerLeft}>
            <button
              type="button"
              className={styles.menuBtn}
              onClick={toggleSidebar}
              aria-label="Toggle menu"
            >
              <LuMenu />
            </button>
            <h1 className={styles.pageTitle}>{pageTitle}</h1>
          </div>
        </header>

        <main className={styles.content}>
          <ErrorBoundary FallbackComponent={ShellErrorFallback}>
            <Suspense fallback={<ShellLoading />}>
              <Outlet />
            </Suspense>
          </ErrorBoundary>
        </main>
      </div>
    </div>
  )
}
