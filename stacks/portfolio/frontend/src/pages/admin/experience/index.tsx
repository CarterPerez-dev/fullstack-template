// ===================
// © AngelaMos | 2026
// index.tsx
// ===================

import { useState } from 'react'
import {
  LuChevronDown,
  LuChevronUp,
  LuPencil,
  LuPlus,
  LuTrash2,
  LuX,
} from 'react-icons/lu'
import {
  useCreateExperience,
  useDeleteExperience,
  useExperience,
  useReorderExperience,
  useUpdateExperience,
} from '@/api/hooks'
import type { ExperienceInput, ExperienceResponse } from '@/api/types'
import { LineList } from '../_components'
import styles from '../admin.module.scss'

type ModalState =
  | { type: 'closed' }
  | { type: 'create' }
  | { type: 'edit'; item: ExperienceResponse }
  | { type: 'delete'; item: ExperienceResponse }

export function Component(): React.ReactElement {
  const { data, isLoading } = useExperience()
  const create = useCreateExperience()
  const update = useUpdateExperience()
  const remove = useDeleteExperience()
  const reorder = useReorderExperience()

  const [modal, setModal] = useState<ModalState>({ type: 'closed' })
  const [form, setForm] = useState<ExperienceInput>({})

  const items = data ?? []

  const openCreate = (): void => {
    setForm({ bullets: [] })
    setModal({ type: 'create' })
  }

  const openEdit = (item: ExperienceResponse): void => {
    setForm({
      role: item.role,
      company: item.company ?? '',
      dates: item.dates ?? '',
      bullets: item.bullets,
    })
    setModal({ type: 'edit', item })
  }

  const submit = (e: React.FormEvent): void => {
    e.preventDefault()
    if (modal.type === 'create') {
      create.mutate(form, { onSuccess: () => setModal({ type: 'closed' }) })
    } else if (modal.type === 'edit') {
      update.mutate(
        { id: modal.item.id, data: form },
        { onSuccess: () => setModal({ type: 'closed' }) }
      )
    }
  }

  const move = (index: number, dir: -1 | 1): void => {
    const target = index + dir
    if (target < 0 || target >= items.length) return
    const next = [...items]
    const [moved] = next.splice(index, 1)
    next.splice(target, 0, moved)
    reorder.mutate(next.map((i) => i.id))
  }

  const setField = (patch: Partial<ExperienceInput>): void =>
    setForm((prev) => ({ ...prev, ...patch }))

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <div className={styles.headerLeft}>
          <span className={styles.headerTag}>Content</span>
          <h1 className={styles.title}>Experience</h1>
        </div>
        <button type="button" className={styles.createBtn} onClick={openCreate}>
          <LuPlus />
          Add
        </button>
      </div>

      {isLoading && <div className={styles.loading}>Loading…</div>}
      {!isLoading && items.length === 0 && (
        <div className={styles.empty}>No experience yet.</div>
      )}

      <div className={styles.list}>
        {items.map((item, index) => (
          <div key={item.id} className={styles.card}>
            <div className={styles.orderBtns}>
              <button
                type="button"
                className={styles.orderBtn}
                onClick={() => move(index, -1)}
                disabled={index === 0}
                aria-label="Move up"
              >
                <LuChevronUp />
              </button>
              <button
                type="button"
                className={styles.orderBtn}
                onClick={() => move(index, 1)}
                disabled={index === items.length - 1}
                aria-label="Move down"
              >
                <LuChevronDown />
              </button>
            </div>
            <div className={styles.cardMain}>
              <p className={styles.cardTitle}>{item.role}</p>
              <p className={styles.cardSub}>
                {[item.company, item.dates].filter(Boolean).join(' · ') || '—'}
              </p>
            </div>
            <div className={styles.cardActions}>
              <button
                type="button"
                className={styles.iconBtn}
                onClick={() => openEdit(item)}
                aria-label="Edit"
              >
                <LuPencil />
              </button>
              <button
                type="button"
                className={styles.iconBtnDanger}
                onClick={() => setModal({ type: 'delete', item })}
                aria-label="Delete"
              >
                <LuTrash2 />
              </button>
            </div>
          </div>
        ))}
      </div>

      {(modal.type === 'create' || modal.type === 'edit') && (
        <div className={styles.modal}>
          <button
            type="button"
            className={styles.modalOverlay}
            onClick={() => setModal({ type: 'closed' })}
            aria-label="Close"
          />
          <div className={styles.modalContent}>
            <div className={styles.modalHeader}>
              <h2 className={styles.modalTitle}>
                {modal.type === 'create' ? 'Add experience' : 'Edit experience'}
              </h2>
              <button
                type="button"
                className={styles.modalClose}
                onClick={() => setModal({ type: 'closed' })}
              >
                <LuX />
              </button>
            </div>
            <form className={styles.form} onSubmit={submit}>
              <div className={styles.formGrid}>
                <div className={`${styles.field} ${styles.fieldFull}`}>
                  <label className={styles.label} htmlFor="role">
                    Role
                  </label>
                  <input
                    id="role"
                    type="text"
                    className={styles.input}
                    value={form.role ?? ''}
                    onChange={(e) => setField({ role: e.target.value })}
                    required
                  />
                </div>
                <div className={styles.field}>
                  <label className={styles.label} htmlFor="company">
                    Company
                  </label>
                  <input
                    id="company"
                    type="text"
                    className={styles.input}
                    value={form.company ?? ''}
                    onChange={(e) => setField({ company: e.target.value })}
                  />
                </div>
                <div className={styles.field}>
                  <label className={styles.label} htmlFor="dates">
                    Dates
                  </label>
                  <input
                    id="dates"
                    type="text"
                    className={styles.input}
                    placeholder="Jan 2026 – Present"
                    value={form.dates ?? ''}
                    onChange={(e) => setField({ dates: e.target.value })}
                  />
                </div>
                <div className={`${styles.field} ${styles.fieldFull}`}>
                  <span className={styles.label}>Bullets</span>
                  <LineList
                    value={form.bullets ?? []}
                    onChange={(next) => setField({ bullets: next })}
                    placeholder="Achievement or responsibility"
                  />
                </div>
              </div>
              <div className={styles.saveBar}>
                <button
                  type="button"
                  className={styles.cancelBtn}
                  onClick={() => setModal({ type: 'closed' })}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className={styles.submitBtn}
                  disabled={create.isPending || update.isPending}
                >
                  Save
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {modal.type === 'delete' && (
        <div className={styles.modal}>
          <button
            type="button"
            className={styles.modalOverlay}
            onClick={() => setModal({ type: 'closed' })}
            aria-label="Close"
          />
          <div className={styles.modalContent}>
            <div className={styles.modalHeader}>
              <h2 className={styles.modalTitle}>Delete experience</h2>
              <button
                type="button"
                className={styles.modalClose}
                onClick={() => setModal({ type: 'closed' })}
              >
                <LuX />
              </button>
            </div>
            <div className={styles.deleteConfirm}>
              <p className={styles.deleteText}>
                Delete “{modal.item.role}”? This cannot be undone.
              </p>
              <div className={styles.formActions}>
                <button
                  type="button"
                  className={styles.cancelBtn}
                  onClick={() => setModal({ type: 'closed' })}
                >
                  Cancel
                </button>
                <button
                  type="button"
                  className={styles.deleteBtn}
                  onClick={() =>
                    remove.mutate(modal.item.id, {
                      onSuccess: () => setModal({ type: 'closed' }),
                    })
                  }
                  disabled={remove.isPending}
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

Component.displayName = 'AdminExperience'
