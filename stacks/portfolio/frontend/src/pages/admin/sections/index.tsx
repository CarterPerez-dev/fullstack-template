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
  useCreateCustomSection,
  useCustomSections,
  useDeleteCustomSection,
  useReorderCustomSections,
  useUpdateCustomSection,
} from '@/api/hooks'
import type { CustomSectionInput, CustomSectionResponse } from '@/api/types'
import { LineList } from '../_components'
import styles from '../admin.module.scss'

type ModalState =
  | { type: 'closed' }
  | { type: 'create' }
  | { type: 'edit'; item: CustomSectionResponse }
  | { type: 'delete'; item: CustomSectionResponse }

export function Component(): React.ReactElement {
  const { data, isLoading } = useCustomSections()
  const create = useCreateCustomSection()
  const update = useUpdateCustomSection()
  const remove = useDeleteCustomSection()
  const reorder = useReorderCustomSections()

  const [modal, setModal] = useState<ModalState>({ type: 'closed' })
  const [form, setForm] = useState<CustomSectionInput>({})

  const items = data ?? []

  const openCreate = (): void => {
    setForm({ items: [] })
    setModal({ type: 'create' })
  }

  const openEdit = (item: CustomSectionResponse): void => {
    setForm({
      title: item.title,
      subtitle: item.subtitle ?? '',
      body: item.body ?? '',
      items: item.items,
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

  const setField = (patch: Partial<CustomSectionInput>): void =>
    setForm((prev) => ({ ...prev, ...patch }))

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <div className={styles.headerLeft}>
          <span className={styles.headerTag}>Content</span>
          <h1 className={styles.title}>Sections</h1>
        </div>
        <button type="button" className={styles.createBtn} onClick={openCreate}>
          <LuPlus />
          Add
        </button>
      </div>

      {isLoading && <div className={styles.loading}>Loading…</div>}
      {!isLoading && items.length === 0 && (
        <div className={styles.empty}>No custom sections yet.</div>
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
              <p className={styles.cardTitle}>{item.title}</p>
              <p className={styles.cardSub}>
                {item.subtitle ?? item.body ?? '—'}
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
                {modal.type === 'create' ? 'Add section' : 'Edit section'}
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
                  <label className={styles.label} htmlFor="title">
                    Title
                  </label>
                  <input
                    id="title"
                    type="text"
                    className={styles.input}
                    value={form.title ?? ''}
                    onChange={(e) => setField({ title: e.target.value })}
                    required
                  />
                </div>
                <div className={`${styles.field} ${styles.fieldFull}`}>
                  <label className={styles.label} htmlFor="subtitle">
                    Subtitle
                  </label>
                  <input
                    id="subtitle"
                    type="text"
                    className={styles.input}
                    value={form.subtitle ?? ''}
                    onChange={(e) => setField({ subtitle: e.target.value })}
                  />
                </div>
                <div className={`${styles.field} ${styles.fieldFull}`}>
                  <label className={styles.label} htmlFor="body">
                    Body
                  </label>
                  <textarea
                    id="body"
                    className={styles.textarea}
                    value={form.body ?? ''}
                    onChange={(e) => setField({ body: e.target.value })}
                  />
                  <span className={styles.hint}>
                    Separate paragraphs with a blank line.
                  </span>
                </div>
                <div className={`${styles.field} ${styles.fieldFull}`}>
                  <span className={styles.label}>List items</span>
                  <LineList
                    value={form.items ?? []}
                    onChange={(next) => setField({ items: next })}
                    placeholder="List item"
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
              <h2 className={styles.modalTitle}>Delete section</h2>
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
                Delete “{modal.item.title}”? This cannot be undone.
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

Component.displayName = 'AdminSections'
