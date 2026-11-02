// ===================
// © AngelaMos | 2026
// routers.tsx
// ===================

import { createBrowserRouter, type RouteObject } from 'react-router-dom'
import { UserRole } from '@/api/types'
import { ROUTES } from '@/config'
import { ProtectedRoute } from './protected-route'
import { Shell } from './shell'

const routes: RouteObject[] = [
  {
    path: ROUTES.HOME,
    lazy: () => import('@/pages/portfolio'),
  },
  {
    path: ROUTES.LOGIN,
    lazy: () => import('@/pages/login'),
  },
  {
    path: ROUTES.REGISTER,
    lazy: () => import('@/pages/register'),
  },
  {
    element: <ProtectedRoute allowedRoles={[UserRole.ADMIN]} />,
    children: [
      {
        element: <Shell />,
        children: [
          {
            path: ROUTES.ADMIN.PROFILE,
            lazy: () => import('@/pages/admin/profile'),
          },
          {
            path: ROUTES.ADMIN.APPEARANCE,
            lazy: () => import('@/pages/admin/appearance'),
          },
          {
            path: ROUTES.ADMIN.CERTIFICATIONS,
            lazy: () => import('@/pages/admin/certifications'),
          },
          {
            path: ROUTES.ADMIN.PROJECTS,
            lazy: () => import('@/pages/admin/projects'),
          },
          {
            path: ROUTES.ADMIN.EXPERIENCE,
            lazy: () => import('@/pages/admin/experience'),
          },
          {
            path: ROUTES.ADMIN.SKILLS,
            lazy: () => import('@/pages/admin/skills'),
          },
          {
            path: ROUTES.ADMIN.LINKS,
            lazy: () => import('@/pages/admin/links'),
          },
          {
            path: ROUTES.ADMIN.SECTIONS,
            lazy: () => import('@/pages/admin/sections'),
          },
          {
            path: ROUTES.ADMIN.MEDIA,
            lazy: () => import('@/pages/admin/media'),
          },
          {
            path: ROUTES.ADMIN.USERS,
            lazy: () => import('@/pages/admin'),
          },
          {
            path: ROUTES.SETTINGS,
            lazy: () => import('@/pages/settings'),
          },
        ],
      },
    ],
  },
  {
    path: ROUTES.UNAUTHORIZED,
    lazy: () => import('@/pages/portfolio'),
  },
  {
    path: '*',
    lazy: () => import('@/pages/portfolio'),
  },
]

export const router = createBrowserRouter(routes)
