// ===================
// © AngelaMos | 2025
// protected-route.tsx
// ===================

import { useEffect } from 'react'
import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useCurrentUser } from '@/api/hooks/useAuth'
import type { UserRole } from '@/api/types'
import { ROUTES } from '@/config'
import { useAuthStore } from '@/core/lib'

interface ProtectedRouteProps {
  allowedRoles?: UserRole[]
  redirectTo?: string
}

export function ProtectedRoute({
  allowedRoles,
  redirectTo = ROUTES.LOGIN,
}: ProtectedRouteProps): React.ReactElement {
  const location = useLocation()
  const { isAuthenticated, isLoading, updateUser } = useAuthStore()
  const currentUser = useCurrentUser()
  const user = currentUser.data

  useEffect(() => {
    if (user) updateUser(user)
  }, [user, updateUser])

  if (isLoading || (isAuthenticated && currentUser.isPending)) {
    return <div>Loading...</div>
  }

  if (!isAuthenticated || currentUser.isError) {
    return (
      <Navigate
        to={redirectTo}
        state={{ from: location.pathname + location.search }}
        replace
      />
    )
  }

  if (
    allowedRoles !== undefined &&
    allowedRoles.length > 0 &&
    (user === undefined || !allowedRoles.includes(user.role))
  ) {
    return <Navigate to={ROUTES.UNAUTHORIZED} replace />
  }

  return <Outlet />
}
