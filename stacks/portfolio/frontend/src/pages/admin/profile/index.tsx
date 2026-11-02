// ===================
// © AngelaMos | 2026
// index.tsx
// ===================

import { useEffect, useState } from 'react'
import { usePortfolio, useUpdatePortfolioProfile } from '@/api/hooks'
import type { ProfileUpdateRequest } from '@/api/types'
import { MediaPicker, TagInput } from '../_components'
import styles from '../admin.module.scss'

export function Component(): React.ReactElement {
  const { data } = usePortfolio()
  const update = useUpdatePortfolioProfile()
  const [form, setForm] = useState<ProfileUpdateRequest>({})

  useEffect(() => {
    if (data === undefined) return
    const p = data.profile
    setForm({
      name: p.name,
      headline: p.headline,
      subtitle: p.subtitle ?? '',
      location: p.location ?? '',
      availability: p.availability ?? '',
      bio: p.bio ?? '',
      email: p.email ?? '',
      eyebrow_left: p.eyebrow_left ?? '',
      eyebrow_right: p.eyebrow_right ?? '',
      meta_items: p.meta_items,
      avatar_media_id: p.avatar_media_id,
    })
  }, [data])

  const setField = (patch: Partial<ProfileUpdateRequest>): void =>
    setForm((prev) => ({ ...prev, ...patch }))

  const submit = (e: React.FormEvent): void => {
    e.preventDefault()
    update.mutate(form)
  }

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <div className={styles.headerLeft}>
          <span className={styles.headerTag}>Content</span>
          <h1 className={styles.title}>Profile</h1>
          <p className={styles.subtitle}>
            Your identity block: name, headline, bio and contact.
          </p>
        </div>
      </div>

      <form className={styles.form} onSubmit={submit}>
        <div className={styles.formGrid}>
          <div className={styles.field}>
            <label className={styles.label} htmlFor="name">
              Name
            </label>
            <input
              id="name"
              type="text"
              className={styles.input}
              value={form.name ?? ''}
              onChange={(e) => setField({ name: e.target.value })}
            />
          </div>
          <div className={styles.field}>
            <label className={styles.label} htmlFor="email">
              Email
            </label>
            <input
              id="email"
              type="email"
              className={styles.input}
              value={form.email ?? ''}
              onChange={(e) => setField({ email: e.target.value })}
            />
          </div>
          <div className={`${styles.field} ${styles.fieldFull}`}>
            <label className={styles.label} htmlFor="headline">
              Headline
            </label>
            <textarea
              id="headline"
              className={styles.textarea}
              value={form.headline ?? ''}
              onChange={(e) => setField({ headline: e.target.value })}
            />
          </div>
          <div className={styles.field}>
            <label className={styles.label} htmlFor="location">
              Location
            </label>
            <input
              id="location"
              type="text"
              className={styles.input}
              value={form.location ?? ''}
              onChange={(e) => setField({ location: e.target.value })}
            />
          </div>
          <div className={styles.field}>
            <label className={styles.label} htmlFor="availability">
              Availability
            </label>
            <input
              id="availability"
              type="text"
              className={styles.input}
              value={form.availability ?? ''}
              onChange={(e) => setField({ availability: e.target.value })}
            />
          </div>
          <div className={styles.field}>
            <label className={styles.label} htmlFor="eyebrow_left">
              Eyebrow (left)
            </label>
            <input
              id="eyebrow_left"
              type="text"
              className={styles.input}
              value={form.eyebrow_left ?? ''}
              onChange={(e) => setField({ eyebrow_left: e.target.value })}
            />
          </div>
          <div className={styles.field}>
            <label className={styles.label} htmlFor="eyebrow_right">
              Eyebrow (right)
            </label>
            <input
              id="eyebrow_right"
              type="text"
              className={styles.input}
              value={form.eyebrow_right ?? ''}
              onChange={(e) => setField({ eyebrow_right: e.target.value })}
            />
          </div>
          <div className={`${styles.field} ${styles.fieldFull}`}>
            <label className={styles.label} htmlFor="bio">
              Bio
            </label>
            <span className={styles.hint}>
              Separate paragraphs with a blank line.
            </span>
            <textarea
              id="bio"
              className={styles.textarea}
              value={form.bio ?? ''}
              onChange={(e) => setField({ bio: e.target.value })}
            />
          </div>
          <div className={`${styles.field} ${styles.fieldFull}`}>
            <span className={styles.label}>Status chips</span>
            <TagInput
              value={form.meta_items ?? []}
              onChange={(next) => setField({ meta_items: next })}
              placeholder="e.g. Available, Remote"
            />
          </div>
          <div className={`${styles.field} ${styles.fieldFull}`}>
            <span className={styles.label}>Photo</span>
            <MediaPicker
              value={form.avatar_media_id ?? null}
              onChange={(id) => setField({ avatar_media_id: id })}
            />
          </div>
        </div>

        <div className={styles.saveBar}>
          <button
            type="submit"
            className={styles.submitBtn}
            disabled={update.isPending}
          >
            {update.isPending ? 'Saving…' : 'Save changes'}
          </button>
        </div>
      </form>
    </div>
  )
}

Component.displayName = 'AdminProfile'
