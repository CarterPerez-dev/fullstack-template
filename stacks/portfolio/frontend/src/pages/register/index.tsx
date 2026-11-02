/**
 * ©AngelaMos | 2026
 * index.tsx
 */

import { Navigate } from 'react-router-dom'
import { ROUTES } from '@/config'

export function Component(): React.ReactElement {
  return <Navigate to={ROUTES.LOGIN} replace />
}

Component.displayName = 'Register'
