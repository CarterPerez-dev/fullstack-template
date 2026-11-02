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
  useCreateLink,
  useDeleteLink,
  useLinks,
  useReorderLinks,
  useUpdateLink,
} from '@/api/hooks'
import type { LinkInput, LinkResponse } from '@/api/types'
import { MediaPicker } from '../_components'
import styles from '../admin.module.scss'

type ModalState =
  | { type: 'closed' }
  | { type: 'create' }
  | { type: 'edit'; item: LinkResponse }
  | { type: 'delete'; item: LinkResponse }

export function Component(): React.ReactElement {
  const { data, isLoading } = useLinks()
  const create = useCreateLink()
  const update = useUpdateLink()
  const remove = useDeleteLink()
  const reorder = useReorderLinks()

  const [modal, setModal] = useState<ModalState>({ type: 'closed' })
  const [form, setForm] = useState<LinkInput>({})

  const items = data ?? []

  const openCreate = (): void => {
    setForm({})
    setModal({ type: 'create' })
  }

  const openEdit = (item: LinkResponse): void => {
    setForm({
      label: item.label,
      url: item.url ?? '',
      icon: item.icon ?? '',
      media_id: item.media_id,
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

  const setField = (patch: Partial<LinkInput>): void =>
    setForm((prev) => ({ ...prev, ...patch }))

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <div className={styles.headerLeft}>
          <span className={styles.headerTag}>Content</span>
          <h1 className={styles.title}>Links</h1>
        </div>
        <button type="button" className={styles.createBtn} onClick={openCreate}>
          <LuPlus />
          Add
        </button>
      </div>

      {isLoading && <div className={styles.loading}>Loading…</div>}
      {!isLoading && items.length === 0 && (
        <div className={styles.empty}>No links yet.</div>
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
              <p className={styles.cardTitle}>{item.label}</p>
              <p className={styles.cardSub}>{item.url ?? '(uploaded file)'}</p>
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
                {modal.type === 'create' ? 'Add link' : 'Edit link'}
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
                  <label className={styles.label} htmlFor="label">
                    Label
                  </label>
                  <input
                    id="label"
                    type="text"
                    className={styles.input}
                    placeholder="GitHub, Resume…"
                    value={form.label ?? ''}
                    onChange={(e) => setField({ label: e.target.value })}
                    required
                  />
                </div>
                <div className={`${styles.field} ${styles.fieldFull}`}>
                  <label className={styles.label} htmlFor="url">
                    URL
                  </label>
                  <span className={styles.hint}>
                    Leave blank if attaching a file below.
                  </span>
                  <input
                    id="url"
                    type="url"
                    className={styles.input}
                    value={form.url ?? ''}
                    onChange={(e) => setField({ url: e.target.value })}
                  />
                </div>
                <div className={styles.field}>
                  <label className={styles.label} htmlFor="icon">
                    Icon
                  </label>
                  <input
                    id="icon"
                    type="text"
                    className={styles.input}
                    placeholder="github, linkedin, mail, download…"
                    value={form.icon ?? ''}
                    onChange={(e) => setField({ icon: e.target.value })}
                  />
                </div>
                <div className={`${styles.field} ${styles.fieldFull}`}>
                  <span className={styles.label}>Or attach a file</span>
                  <span className={styles.hint}>e.g. a resume PDF.</span>
                  <MediaPicker
                    value={form.media_id ?? null}
                    onChange={(id) => setField({ media_id: id })}
                    accept="any"
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
              <h2 className={styles.modalTitle}>Delete link</h2>
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
                Delete “{modal.item.label}”? This cannot be undone.
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

Component.displayName = 'AdminLinks'
