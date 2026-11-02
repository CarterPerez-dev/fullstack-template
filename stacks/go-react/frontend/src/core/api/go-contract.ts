/**
 * ©AngelaMos | 2026
 * go-contract.ts
 */

import { z } from 'zod'

const userSchema = z.object({
  id: z.string().uuid(),
  email: z.string().email(),
  name: z.string(),
  role: z.enum(['user', 'admin']),
  tier: z.string(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime().optional(),
})

const envelopeSchema = z.object({
  success: z.literal(true),
  data: z.unknown(),
  meta: z
    .object({
      page: z.number().optional(),
      page_size: z.number().optional(),
      total: z.number().optional(),
    })
    .optional(),
})

const authSchema = z.object({
  user: userSchema,
  tokens: z.object({ access_token: z.string().min(1), token_type: z.string() }),
})

function userView(user: z.infer<typeof userSchema>) {
  return { ...user, full_name: user.name, updated_at: user.updated_at ?? null }
}

export function decodeGoResponse(value: unknown): unknown {
  const envelope = envelopeSchema.parse(value)
  const auth = authSchema.safeParse(envelope.data)
  if (auth.success) {
    return { ...auth.data.tokens, user: userView(auth.data.user) }
  }
  const user = userSchema.safeParse(envelope.data)
  if (user.success) return userView(user.data)
  if (envelope.meta) {
    const users = z.array(userSchema).parse(envelope.data)
    return {
      items: users.map(userView),
      total: envelope.meta.total ?? 0,
      page: envelope.meta.page ?? 1,
      size: envelope.meta.page_size ?? 20,
    }
  }
  return envelope.data
}
