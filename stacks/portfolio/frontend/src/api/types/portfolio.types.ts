// ===================
// © AngelaMos | 2026
// portfolio.types.ts
// ===================

import { z } from 'zod'

export const ItemStatus = {
  COMPLETED: 'completed',
  IN_PROGRESS: 'in_progress',
  PLANNED: 'planned',
} as const

export type ItemStatus = (typeof ItemStatus)[keyof typeof ItemStatus]

export const ITEM_STATUS_LABELS: Record<ItemStatus, string> = {
  completed: 'Completed',
  in_progress: 'In Progress',
  planned: 'Planned',
}

const baseEntity = {
  id: z.string().uuid(),
  created_at: z.string(),
  updated_at: z.string().nullable(),
}

export const mediaResponseSchema = z.object({
  ...baseEntity,
  original_filename: z.string(),
  content_type: z.string(),
  byte_size: z.number(),
})

export const profileResponseSchema = z.object({
  ...baseEntity,
  name: z.string(),
  headline: z.string(),
  subtitle: z.string().nullable(),
  location: z.string().nullable(),
  availability: z.string().nullable(),
  bio: z.string().nullable(),
  email: z.string().nullable(),
  avatar_media_id: z.string().uuid().nullable(),
  eyebrow_left: z.string().nullable(),
  eyebrow_right: z.string().nullable(),
  meta_items: z.array(z.string()),
  section_titles: z.record(z.string(), z.string()),
})

export const siteSettingsResponseSchema = z.object({
  ...baseEntity,
  site_title: z.string(),
  meta_description: z.string().nullable(),
  favicon_media_id: z.string().uuid().nullable(),
  color_bg: z.string(),
  color_surface: z.string(),
  color_text: z.string(),
  color_text_muted: z.string(),
  color_accent: z.string(),
  color_dark_bg: z.string(),
  color_dark_text: z.string(),
  font_display: z.string(),
  font_body: z.string(),
  font_mono: z.string(),
  dark_mode: z.boolean(),
  theme_extra: z.record(z.string(), z.string()),
})

export const certificationResponseSchema = z.object({
  ...baseEntity,
  name: z.string(),
  code: z.string().nullable(),
  issuer: z.string().nullable(),
  status: z.nativeEnum(ItemStatus),
  issue_date: z.string().nullable(),
  credential_url: z.string().nullable(),
  badge_media_id: z.string().uuid().nullable(),
  display_order: z.number(),
})

export const projectResponseSchema = z.object({
  ...baseEntity,
  title: z.string(),
  description: z.string().nullable(),
  status: z.nativeEnum(ItemStatus),
  tags: z.array(z.string()),
  repo_url: z.string().nullable(),
  live_url: z.string().nullable(),
  image_media_id: z.string().uuid().nullable(),
  display_order: z.number(),
})

export const experienceResponseSchema = z.object({
  ...baseEntity,
  role: z.string(),
  company: z.string().nullable(),
  dates: z.string().nullable(),
  bullets: z.array(z.string()),
  display_order: z.number(),
})

export const skillGroupResponseSchema = z.object({
  ...baseEntity,
  label: z.string(),
  items: z.array(z.string()),
  display_order: z.number(),
})

export const linkResponseSchema = z.object({
  ...baseEntity,
  label: z.string(),
  url: z.string().nullable(),
  media_id: z.string().uuid().nullable(),
  icon: z.string().nullable(),
  display_order: z.number(),
})

export const customSectionResponseSchema = z.object({
  ...baseEntity,
  title: z.string(),
  subtitle: z.string().nullable(),
  body: z.string().nullable(),
  items: z.array(z.string()),
  display_order: z.number(),
})

export const portfolioResponseSchema = z.object({
  profile: profileResponseSchema,
  settings: siteSettingsResponseSchema,
  certifications: z.array(certificationResponseSchema),
  projects: z.array(projectResponseSchema),
  experience: z.array(experienceResponseSchema),
  skill_groups: z.array(skillGroupResponseSchema),
  links: z.array(linkResponseSchema),
  custom_sections: z.array(customSectionResponseSchema),
})

export const registrationStatusSchema = z.object({
  registration_open: z.boolean(),
})

export type MediaResponse = z.infer<typeof mediaResponseSchema>
export type ProfileResponse = z.infer<typeof profileResponseSchema>
export type SiteSettingsResponse = z.infer<typeof siteSettingsResponseSchema>
export type CertificationResponse = z.infer<typeof certificationResponseSchema>
export type ProjectResponse = z.infer<typeof projectResponseSchema>
export type ExperienceResponse = z.infer<typeof experienceResponseSchema>
export type SkillGroupResponse = z.infer<typeof skillGroupResponseSchema>
export type LinkResponse = z.infer<typeof linkResponseSchema>
export type CustomSectionResponse = z.infer<typeof customSectionResponseSchema>
export type PortfolioResponse = z.infer<typeof portfolioResponseSchema>
export type RegistrationStatus = z.infer<typeof registrationStatusSchema>

export type ProfileUpdateRequest = Partial<
  Omit<ProfileResponse, keyof typeof baseEntity>
>
export type SiteSettingsUpdateRequest = Partial<
  Omit<SiteSettingsResponse, keyof typeof baseEntity>
>

export type CertificationInput = Partial<
  Omit<CertificationResponse, keyof typeof baseEntity>
>
export type ProjectInput = Partial<Omit<ProjectResponse, keyof typeof baseEntity>>
export type ExperienceInput = Partial<
  Omit<ExperienceResponse, keyof typeof baseEntity>
>
export type SkillGroupInput = Partial<
  Omit<SkillGroupResponse, keyof typeof baseEntity>
>
export type LinkInput = Partial<Omit<LinkResponse, keyof typeof baseEntity>>
export type CustomSectionInput = Partial<
  Omit<CustomSectionResponse, keyof typeof baseEntity>
>

export const isValidPortfolioResponse = (
  data: unknown
): data is PortfolioResponse => {
  return portfolioResponseSchema.safeParse(data).success
}

export const isValidRegistrationStatus = (
  data: unknown
): data is RegistrationStatus => {
  return registrationStatusSchema.safeParse(data).success
}

export class PortfolioResponseError extends Error {
  readonly endpoint?: string

  constructor(message: string, endpoint?: string) {
    super(message)
    this.name = 'PortfolioResponseError'
    this.endpoint = endpoint
    Object.setPrototypeOf(this, PortfolioResponseError.prototype)
  }
}

export const PORTFOLIO_ERROR_MESSAGES = {
  INVALID_RESPONSE: 'Invalid portfolio data from server',
  FAILED_TO_SAVE: 'Failed to save changes',
  FAILED_TO_DELETE: 'Failed to delete item',
  FAILED_TO_UPLOAD: 'Failed to upload file',
  FAILED_TO_REORDER: 'Failed to reorder items',
} as const

export const PORTFOLIO_SUCCESS_MESSAGES = {
  SAVED: 'Saved',
  CREATED: 'Created',
  DELETED: 'Deleted',
  UPLOADED: 'File uploaded',
  REORDERED: 'Order updated',
} as const
