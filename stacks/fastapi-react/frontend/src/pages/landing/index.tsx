/**
 * ©AngelaMos | 2026
 * index.tsx
 */

import { FiGithub } from 'react-icons/fi'
import { Link } from 'react-router-dom'
import { ROUTES } from '@/config'
import styles from './landing.module.scss'

export function Component(): React.ReactElement {
  return (
    <div className={styles.page}>
      <nav className={styles.topBar}>
        <div className={styles.topLeft}>
          <span className={styles.mark}>FST</span>
          <span>V1.0</span>
        </div>
        <div className={styles.topRight}>
          <span>FASTAPI + REACT</span>
          <span className={styles.status}>OPERATIONAL</span>
        </div>
      </nav>

      <div className={styles.hero}>
        <h1 className={styles.heroTitle}>
          Build
          <br />
          Production
          <br />
          Systems
        </h1>
        <p className={styles.heroSub}>
          Opinionated full-stack template for medium-large scale applications.
          Modern patterns, strict typing, security best practices.
        </p>
      </div>

      <div className={styles.pattern} />

      <div className={styles.grid}>
        <section className={styles.cell}>
          <span className={styles.cellLabel}>01 — Frontend</span>
          <ul className={styles.list}>
            <li>React 19 + TypeScript strict mode</li>
            <li>TanStack Query server state caching</li>
            <li>Zustand stores with persistence</li>
            <li>Axios interceptors + auto token refresh</li>
            <li>Zod runtime validation</li>
            <li>SCSS modules + design tokens</li>
          </ul>
        </section>

        <section className={styles.cell}>
          <span className={styles.cellLabel}>02 — Backend</span>
          <ul className={styles.list}>
            <li>DDD + DI Architecture</li>
            <li>FastAPI async/await throughout</li>
            <li>SQLAlchemy 2.0+ async + pooling</li>
            <li>JWT auth with token rotation</li>
            <li>Argon2id hashing</li>
            <li>Pydantic v2 strict validation</li>
          </ul>
        </section>

        <section className={styles.cell}>
          <span className={styles.cellLabel}>03 — Infrastructure</span>
          <ul className={styles.list}>
            <li>Docker Compose dev/prod configs</li>
            <li>Nginx reverse proxy + rate limiting</li>
            <li>PostgreSQL 18 + Redis 7</li>
            <li>Health checks + graceful shutdown</li>
          </ul>
        </section>

        <section className={styles.cell}>
          <span className={styles.cellLabel}>04 — DevOps</span>
          <ul className={styles.list}>
            <li>GitHub Actions CI pipeline</li>
            <li>Ruff, Pylint, Mypy, Biome linting</li>
            <li>Strict type checking both ends</li>
            <li>Alembic async migrations</li>
          </ul>
        </section>
      </div>

      <div className={styles.actions}>
        <Link to={ROUTES.REGISTER} className={styles.primaryBtn}>
          Try Auth Flow
        </Link>
        <a
          href="/api/docs"
          target="_blank"
          rel="noopener noreferrer"
          className={styles.secondaryBtn}
        >
          API Docs
        </a>
      </div>

      <footer className={styles.footer}>
        <span>© AngelaMos + CarterPerez-dev · 2026</span>
        <a
          href="https://github.com/CarterPerez-dev/fullstack-template"
          target="_blank"
          rel="noopener noreferrer"
          className={styles.github}
          aria-label="View on GitHub"
        >
          <FiGithub />
        </a>
      </footer>
    </div>
  )
}

Component.displayName = 'Landing'
