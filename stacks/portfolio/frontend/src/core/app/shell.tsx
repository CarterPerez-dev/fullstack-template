// ===================
// © AngelaMos | 2026
// shell.tsx
// ===================

import { Suspense } from 'react'
import { ErrorBoundary, type FallbackProps } from 'react-error-boundary'
import {
  LuAward,
  LuBriefcase,
  LuChevronLeft,
  LuChevronRight,
  LuExternalLink,
  LuFolderGit2,
  LuImage,
  LuLayers,
  LuLink,
  LuLogOut,
  LuMenu,
  LuPalette,
  LuSettings,
  LuShield,
  LuUser,
  LuWrench,
} from 'react-icons/lu'
import { Link, NavLink, Outlet, useLocation } from 'react-router-dom'
import { useLogout } from '@/api/hooks'
import { ROUTES } from '@/config'
import { useUIStore, useUser } from '@/core/lib'
import styles from './shell.module.scss'

const NAV_ITEMS = [
  { path: ROUTES.ADMIN.PROFILE, label: 'Profile', icon: LuUser },
  { path: ROUTES.ADMIN.APPEARANCE, label: 'Appearance', icon: LuPalette },
  { path: ROUTES.ADMIN.CERTIFICATIONS, label: 'Certifications', icon: LuAward },
  { path: ROUTES.ADMIN.PROJECTS, label: 'Projects', icon: LuFolderGit2 },
  { path: ROUTES.ADMIN.EXPERIENCE, label: 'Experience', icon: LuBriefcase },
  { path: ROUTES.ADMIN.SKILLS, label: 'Skills', icon: LuWrench },
  { path: ROUTES.ADMIN.LINKS, label: 'Links', icon: LuLink },
  { path: ROUTES.ADMIN.SECTIONS, label: 'Sections', icon: LuLayers },
  { path: ROUTES.ADMIN.MEDIA, label: 'Media', icon: LuImage },
  { path: ROUTES.ADMIN.USERS, label: 'Users', icon: LuShield },
  { path: ROUTES.SETTINGS, label: 'Settings', icon: LuSettings },
]

function ShellErrorFallback({ error }: FallbackProps): React.ReactElement {
  return (
    <div className={styles.error}>
      <h2>Something went wrong</h2>
      <pre>{error instanceof Error ? error.message : 'Please try again.'}</pre>
    </div>
  )
}

function ShellLoading(): React.ReactElement {
  return <div className={styles.loading}>Loading...</div>
}

function getPageTitle(pathname: string): string {
  const item = NAV_ITEMS.find((i) => i.path === pathname)
  return item?.label ?? 'Admin'
}

export function Shell(): React.ReactElement {
  const location = useLocation()
  const { sidebarOpen, sidebarCollapsed, toggleSidebar, toggleSidebarCollapsed } =
    useUIStore()
  const { mutate: logout } = useLogout()
  const user = useUser()

  const pageTitle = getPageTitle(location.pathname)
  const avatarLetter =
    user?.full_name?.[0]?.toUpperCase() ?? user?.email?.[0]?.toUpperCase() ?? 'A'

  return (
    <div className={styles.shell}>
      <aside
        className={`${styles.sidebar} ${sidebarOpen ? styles.open : ''} ${sidebarCollapsed ? styles.collapsed : ''}`}
      >
        <div className={styles.sidebarHeader}>
          <span className={styles.logo}>Studio</span>
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

        <div className={styles.sidebarFooter}>
          <Link to={ROUTES.HOME} className={styles.logoutBtn} target="_blank">
            <LuExternalLink className={styles.logoutIcon} />
            <span className={styles.logoutText}>View site</span>
          </Link>
          <button
            type="button"
            className={styles.logoutBtn}
            onClick={() => logout()}
          >
            <LuLogOut className={styles.logoutIcon} />
            <span className={styles.logoutText}>Logout</span>
          </button>
        </div>
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

          <div className={styles.headerRight}>
            <Link to={ROUTES.SETTINGS} className={styles.avatar}>
              {avatarLetter}
            </Link>
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
