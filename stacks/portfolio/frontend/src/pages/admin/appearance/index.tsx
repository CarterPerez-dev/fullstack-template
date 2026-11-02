// ===================
// © AngelaMos | 2026
// index.tsx
// ===================

import { useEffect, useState } from 'react'
import { usePortfolio, useUpdateSettings } from '@/api/hooks'
import type { SiteSettingsUpdateRequest } from '@/api/types'
import { MediaPicker } from '../_components'
import styles from '../admin.module.scss'

type ColorFontKey =
  | 'color_bg'
  | 'color_text'
  | 'color_text_muted'
  | 'color_surface'
  | 'color_accent'
  | 'color_dark_bg'
  | 'color_dark_text'
  | 'font_display'
  | 'font_body'
  | 'font_mono'

const COLOR_FIELDS: { key: ColorFontKey; label: string }[] = [
  { key: 'color_bg', label: 'Background' },
  { key: 'color_text', label: 'Text' },
  { key: 'color_text_muted', label: 'Muted text' },
  { key: 'color_surface', label: 'Surface / lines' },
  { key: 'color_accent', label: 'Accent' },
  { key: 'color_dark_bg', label: 'Dark background' },
  { key: 'color_dark_text', label: 'Dark text' },
]

const FONT_FIELDS: { key: ColorFontKey; label: string }[] = [
  { key: 'font_display', label: 'Display font' },
  { key: 'font_body', label: 'Body font' },
  { key: 'font_mono', label: 'Mono font' },
]

export function Component(): React.ReactElement {
  const { data } = usePortfolio()
  const update = useUpdateSettings()
  const [form, setForm] = useState<SiteSettingsUpdateRequest>({})

  useEffect(() => {
    if (data === undefined) return
    const s = data.settings
    setForm({
      site_title: s.site_title,
      meta_description: s.meta_description ?? '',
      favicon_media_id: s.favicon_media_id,
      color_bg: s.color_bg,
      color_surface: s.color_surface,
      color_text: s.color_text,
      color_text_muted: s.color_text_muted,
      color_accent: s.color_accent,
      color_dark_bg: s.color_dark_bg,
      color_dark_text: s.color_dark_text,
      font_display: s.font_display,
      font_body: s.font_body,
      font_mono: s.font_mono,
      dark_mode: s.dark_mode,
    })
  }, [data])

  const setForm2 = (patch: SiteSettingsUpdateRequest): void =>
    setForm((prev) => ({ ...prev, ...patch }))

  const setKey = (key: ColorFontKey, value: string): void =>
    setForm((prev) => ({ ...prev, [key]: value }))

  const submit = (e: React.FormEvent): void => {
    e.preventDefault()
    update.mutate(form)
  }

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <div className={styles.headerLeft}>
          <span className={styles.headerTag}>Appearance</span>
          <h1 className={styles.title}>Appearance</h1>
          <p className={styles.subtitle}>
            Site title, colors and fonts. Deeper layout is done in code.
          </p>
        </div>
      </div>

      <form className={styles.form} onSubmit={submit}>
        <div className={styles.formGrid}>
          <div className={styles.field}>
            <label className={styles.label} htmlFor="site_title">
              Site title
            </label>
            <input
              id="site_title"
              type="text"
              className={styles.input}
              value={form.site_title ?? ''}
              onChange={(e) => setForm2({ site_title: e.target.value })}
            />
          </div>
          <div className={styles.field}>
            <label className={styles.label} htmlFor="meta_description">
              Meta description
            </label>
            <input
              id="meta_description"
              type="text"
              className={styles.input}
              value={form.meta_description ?? ''}
              onChange={(e) => setForm2({ meta_description: e.target.value })}
            />
          </div>

          {COLOR_FIELDS.map((f) => {
            const value = (form[f.key] as string | undefined) ?? '#000000'
            return (
              <div className={styles.field} key={f.key}>
                <span className={styles.label}>{f.label}</span>
                <div className={styles.colorField}>
                  <input
                    type="color"
                    className={styles.colorInput}
                    value={value}
                    onChange={(e) => setKey(f.key, e.target.value)}
                    aria-label={f.label}
                  />
                  <input
                    type="text"
                    className={`${styles.input} ${styles.colorText}`}
                    value={value}
                    onChange={(e) => setKey(f.key, e.target.value)}
                  />
                </div>
              </div>
            )
          })}

          {FONT_FIELDS.map((f) => (
            <div className={styles.field} key={f.key}>
              <label className={styles.label} htmlFor={f.key}>
                {f.label}
              </label>
              <input
                id={f.key}
                type="text"
                className={styles.input}
                value={(form[f.key] as string | undefined) ?? ''}
                onChange={(e) => setKey(f.key, e.target.value)}
              />
            </div>
          ))}

          <div className={styles.field}>
            <span className={styles.label}>Dark mode</span>
            <label className={styles.checkbox}>
              <input
                type="checkbox"
                checked={form.dark_mode ?? false}
                onChange={(e) => setForm2({ dark_mode: e.target.checked })}
              />
              <span>Use dark background</span>
            </label>
          </div>

          <div className={`${styles.field} ${styles.fieldFull}`}>
            <span className={styles.label}>Favicon</span>
            <MediaPicker
              value={form.favicon_media_id ?? null}
              onChange={(id) => setForm2({ favicon_media_id: id })}
              accept="image"
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

Component.displayName = 'AdminAppearance'
