// ===================
// © AngelaMos | 2026
// index.tsx
// ===================

import { useEffect, useMemo } from 'react'
import type { IconType } from 'react-icons'
import {
  LuDownload,
  LuExternalLink,
  LuFileText,
  LuGithub,
  LuGlobe,
  LuInstagram,
  LuLinkedin,
  LuMail,
  LuTwitter,
  LuYoutube,
} from 'react-icons/lu'
import { usePortfolio } from '@/api/hooks'
import {
  type CustomSectionResponse,
  ITEM_STATUS_LABELS,
  type PortfolioResponse,
  type SiteSettingsResponse,
} from '@/api/types'
import { mediaUrl } from '@/config'
import styles from './portfolio.module.scss'

const STATUS_STYLES = {
  completed: styles.completed,
  in_progress: styles.inProgress,
  planned: styles.planned,
}

const LINK_ICONS: Record<string, IconType> = {
  github: LuGithub,
  linkedin: LuLinkedin,
  mail: LuMail,
  email: LuMail,
  download: LuDownload,
  resume: LuDownload,
  file: LuFileText,
  globe: LuGlobe,
  website: LuGlobe,
  web: LuGlobe,
  twitter: LuTwitter,
  x: LuTwitter,
  instagram: LuInstagram,
  youtube: LuYoutube,
}

const linkIcon = (icon: string | null): IconType =>
  (icon !== null && LINK_ICONS[icon.toLowerCase()]) || LuExternalLink

function themeVars(settings: SiteSettingsResponse): Record<string, string> {
  const bg = settings.dark_mode ? settings.color_dark_bg : settings.color_bg
  const text = settings.dark_mode ? settings.color_dark_text : settings.color_text
  return {
    '--pf-bg': bg,
    '--pf-surface': settings.color_surface,
    '--pf-text': text,
    '--pf-muted': settings.color_text_muted,
    '--pf-accent': settings.color_accent,
    '--pf-font-display': settings.font_display,
    '--pf-font-body': settings.font_body,
    '--pf-font-mono': settings.font_mono,
  }
}

function paragraphs(text: string | null): string[] {
  if (text === null) return []
  return text
    .split(/\n\s*\n/)
    .map((p) => p.trim())
    .filter((p) => p.length > 0)
}

function sectionTitle(
  data: PortfolioResponse,
  key: string,
  fallback: string
): string {
  return data.profile.section_titles[key] ?? fallback
}

function CustomSectionBlock({
  section,
  index,
}: {
  section: CustomSectionResponse
  index: number
}): React.ReactElement {
  const num = String(index).padStart(2, '0')
  return (
    <section className={styles.section}>
      <div className={styles.sectionHead}>
        <span className={styles.sectionNum}>{num}</span>
        <h2 className={styles.sectionTitle}>{section.title}</h2>
      </div>
      {section.subtitle !== null && (
        <p className={styles.sectionLede}>{section.subtitle}</p>
      )}
      {paragraphs(section.body).map((p) => (
        <p key={p} className={styles.paragraph}>
          {p}
        </p>
      ))}
      {section.items.length > 0 && (
        <ul className={styles.plainList}>
          {section.items.map((item) => (
            <li key={item} className={styles.plainListItem}>
              {item}
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}

export function Component(): React.ReactElement {
  const { data, isLoading, isError } = usePortfolio()

  useEffect(() => {
    if (data === undefined) return
    document.title = data.settings.site_title
    const desc = document.querySelector('meta[name="description"]')
    if (desc !== null && data.settings.meta_description !== null) {
      desc.setAttribute('content', data.settings.meta_description)
    }
  }, [data])

  const style = useMemo(
    () =>
      data !== undefined
        ? (themeVars(data.settings) as React.CSSProperties)
        : undefined,
    [data]
  )

  if (isLoading) {
    return <div className={styles.status}>Loading…</div>
  }

  if (isError || data === undefined) {
    return <div className={styles.status}>Unable to load portfolio.</div>
  }

  const { profile, settings, certifications, projects, experience } = data
  const { skill_groups, links, custom_sections } = data
  const avatar = mediaUrl(profile.avatar_media_id)
  let sectionIndex = 0
  const nextNum = (): string => {
    sectionIndex += 1
    return String(sectionIndex).padStart(2, '0')
  }

  return (
    <div className={styles.root} style={style}>
      <div className={styles.inner}>
        <header className={styles.hero}>
          <div className={styles.eyebrow}>
            <span>{profile.eyebrow_left ?? settings.site_title}</span>
            <span>{profile.eyebrow_right ?? profile.location ?? ''}</span>
          </div>
          {avatar !== null && (
            <img className={styles.avatar} src={avatar} alt={profile.name} />
          )}
          <h1 className={styles.name}>{profile.name || settings.site_title}</h1>
          {profile.headline.length > 0 && (
            <p className={styles.headline}>{profile.headline}</p>
          )}
          {profile.meta_items.length > 0 && (
            <div className={styles.metaRow}>
              {profile.meta_items.map((item) => (
                <span key={item} className={styles.metaChip}>
                  {item}
                </span>
              ))}
            </div>
          )}
        </header>

        {(profile.bio !== null || profile.email !== null) && (
          <section className={styles.section}>
            <div className={styles.sectionHead}>
              <span className={styles.sectionNum}>{nextNum()}</span>
              <h2 className={styles.sectionTitle}>
                {sectionTitle(data, 'about', 'About')}
              </h2>
            </div>
            {paragraphs(profile.bio).map((p) => (
              <p key={p} className={styles.paragraph}>
                {p}
              </p>
            ))}
            {(profile.email !== null || links.length > 0) && (
              <div className={styles.contactRow}>
                {profile.email !== null && (
                  <a
                    className={styles.contactLink}
                    href={`mailto:${profile.email}`}
                  >
                    {profile.email}
                  </a>
                )}
              </div>
            )}
          </section>
        )}

        {certifications.length > 0 && (
          <section className={styles.section}>
            <div className={styles.sectionHead}>
              <span className={styles.sectionNum}>{nextNum()}</span>
              <h2 className={styles.sectionTitle}>
                {sectionTitle(data, 'certifications', 'Certifications')}
              </h2>
            </div>
            <ul className={styles.certList}>
              {certifications.map((cert) => (
                <li key={cert.id} className={styles.certItem}>
                  <span
                    className={`${styles.statusDot} ${STATUS_STYLES[cert.status]}`}
                  />
                  {cert.code !== null && (
                    <span className={styles.certCode}>{cert.code}</span>
                  )}
                  <span className={styles.certName}>
                    {cert.credential_url !== null ? (
                      <a
                        href={cert.credential_url}
                        target="_blank"
                        rel="noreferrer"
                      >
                        {cert.name}
                      </a>
                    ) : (
                      cert.name
                    )}
                  </span>
                  <span className={styles.certStatus}>
                    {ITEM_STATUS_LABELS[cert.status]}
                  </span>
                </li>
              ))}
            </ul>
          </section>
        )}

        {projects.length > 0 && (
          <section className={styles.section}>
            <div className={styles.sectionHead}>
              <span className={styles.sectionNum}>{nextNum()}</span>
              <h2 className={styles.sectionTitle}>
                {sectionTitle(data, 'projects', 'Projects')}
              </h2>
            </div>
            <div className={styles.projectList}>
              {projects.map((project) => {
                const image = mediaUrl(project.image_media_id)
                return (
                  <article key={project.id} className={styles.project}>
                    {image !== null && (
                      <img
                        className={styles.projectImage}
                        src={image}
                        alt={project.title}
                      />
                    )}
                    <div className={styles.projectHead}>
                      <h3 className={styles.projectTitle}>{project.title}</h3>
                      <span className={styles.certStatus}>
                        {ITEM_STATUS_LABELS[project.status]}
                      </span>
                    </div>
                    {project.description !== null && (
                      <p className={styles.paragraph}>{project.description}</p>
                    )}
                    {project.tags.length > 0 && (
                      <div className={styles.tagRow}>
                        {project.tags.map((tag) => (
                          <span key={tag} className={styles.projectTag}>
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}
                    <div className={styles.projectLinks}>
                      {project.repo_url !== null && (
                        <a
                          href={project.repo_url}
                          target="_blank"
                          rel="noreferrer"
                        >
                          Source
                        </a>
                      )}
                      {project.live_url !== null && (
                        <a
                          href={project.live_url}
                          target="_blank"
                          rel="noreferrer"
                        >
                          Live
                        </a>
                      )}
                    </div>
                  </article>
                )
              })}
            </div>
          </section>
        )}

        {experience.length > 0 && (
          <section className={styles.section}>
            <div className={styles.sectionHead}>
              <span className={styles.sectionNum}>{nextNum()}</span>
              <h2 className={styles.sectionTitle}>
                {sectionTitle(data, 'experience', 'Experience')}
              </h2>
            </div>
            <div className={styles.expList}>
              {experience.map((entry) => (
                <div key={entry.id} className={styles.expItem}>
                  <div className={styles.expHead}>
                    <span className={styles.expRole}>
                      {entry.role}
                      {entry.company !== null && (
                        <span className={styles.expCompany}>
                          {' '}
                          — {entry.company}
                        </span>
                      )}
                    </span>
                    {entry.dates !== null && (
                      <span className={styles.expDates}>{entry.dates}</span>
                    )}
                  </div>
                  {entry.bullets.length > 0 && (
                    <ul className={styles.bullets}>
                      {entry.bullets.map((bullet) => (
                        <li key={bullet} className={styles.bullet}>
                          {bullet}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              ))}
            </div>
          </section>
        )}

        {skill_groups.length > 0 && (
          <section className={styles.section}>
            <div className={styles.sectionHead}>
              <span className={styles.sectionNum}>{nextNum()}</span>
              <h2 className={styles.sectionTitle}>
                {sectionTitle(data, 'skills', 'Skills')}
              </h2>
            </div>
            <div className={styles.skillGrid}>
              {skill_groups.map((group) => (
                <div key={group.id} className={styles.skillGroup}>
                  <span className={styles.skillLabel}>{group.label}</span>
                  <ul className={styles.skillItems}>
                    {group.items.map((item) => (
                      <li key={item} className={styles.skillItem}>
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </section>
        )}

        {custom_sections.map((section, i) => (
          <CustomSectionBlock
            key={section.id}
            section={section}
            index={sectionIndex + i + 1}
          />
        ))}

        <footer className={styles.footer}>
          <div className={styles.footerLinks}>
            {links.map((link) => {
              const href = link.url ?? mediaUrl(link.media_id) ?? undefined
              if (href === undefined) return null
              const Icon = linkIcon(link.icon)
              return (
                <a
                  key={link.id}
                  href={href}
                  className={styles.footerLink}
                  target="_blank"
                  rel="noreferrer"
                >
                  <Icon className={styles.footerIcon} />
                  <span>{link.label}</span>
                </a>
              )
            })}
          </div>
          <span className={styles.footerYear}>{settings.site_title}</span>
        </footer>
      </div>
    </div>
  )
}

Component.displayName = 'Portfolio'
