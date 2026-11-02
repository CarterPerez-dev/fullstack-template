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
  useCreateProject,
  useDeleteProject,
  useProjects,
  useReorderProjects,
  useUpdateProject,
} from '@/api/hooks'
import {
  ITEM_STATUS_LABELS,
  ItemStatus,
  type ProjectInput,
  type ProjectResponse,
} from '@/api/types'
import { MediaPicker, TagInput } from '../_components'
import styles from '../admin.module.scss'

type ModalState =
  | { type: 'closed' }
  | { type: 'create' }
  | { type: 'edit'; item: ProjectResponse }
  | { type: 'delete'; item: ProjectResponse }

const STATUS_CLASS: Record<ItemStatus, string> = {
  completed: styles.badgeCompleted,
  in_progress: styles.badgeInProgress,
  planned: styles.badgePlanned,
}

export function Component(): React.ReactElement {
  const { data, isLoading } = useProjects()
  const create = useCreateProject()
  const update = useUpdateProject()
  const remove = useDeleteProject()
  const reorder = useReorderProjects()

  const [modal, setModal] = useState<ModalState>({ type: 'closed' })
  const [form, setForm] = useState<ProjectInput>({})

  const items = data ?? []

  const openCreate = (): void => {
    setForm({ status: ItemStatus.PLANNED, tags: [] })
    setModal({ type: 'create' })
  }

  const openEdit = (item: ProjectResponse): void => {
    setForm({
      title: item.title,
      description: item.description ?? '',
      status: item.status,
      repo_url: item.repo_url ?? '',
      live_url: item.live_url ?? '',
      tags: item.tags,
      image_media_id: item.image_media_id,
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

  const setField = (patch: Partial<ProjectInput>): void =>
    setForm((prev) => ({ ...prev, ...patch }))

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <div className={styles.headerLeft}>
          <span className={styles.headerTag}>Content</span>
          <h1 className={styles.title}>Projects</h1>
        </div>
        <button type="button" className={styles.createBtn} onClick={openCreate}>
          <LuPlus />
          Add
        </button>
      </div>

      {isLoading && <div className={styles.loading}>Loading…</div>}
      {!isLoading && items.length === 0 && (
        <div className={styles.empty}>No projects yet.</div>
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
              <p className={styles.cardSub}>{item.tags.join(' · ') || '—'}</p>
            </div>
            <span className={`${styles.badge} ${STATUS_CLASS[item.status]}`}>
              {ITEM_STATUS_LABELS[item.status]}
            </span>
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
                {modal.type === 'create' ? 'Add project' : 'Edit project'}
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
                  <label className={styles.label} htmlFor="description">
                    Description
                  </label>
                  <textarea
                    id="description"
                    className={styles.textarea}
                    value={form.description ?? ''}
                    onChange={(e) => setField({ description: e.target.value })}
                  />
                </div>
                <div className={styles.field}>
                  <label className={styles.label} htmlFor="status">
                    Status
                  </label>
                  <select
                    id="status"
                    className={styles.select}
                    value={form.status ?? ItemStatus.PLANNED}
                    onChange={(e) =>
                      setField({ status: e.target.value as ItemStatus })
                    }
                  >
                    {Object.values(ItemStatus).map((status) => (
                      <option key={status} value={status}>
                        {ITEM_STATUS_LABELS[status]}
                      </option>
                    ))}
                  </select>
                </div>
                <div className={styles.field}>
                  <label className={styles.label} htmlFor="repo_url">
                    Repo URL
                  </label>
                  <input
                    id="repo_url"
                    type="url"
                    className={styles.input}
                    value={form.repo_url ?? ''}
                    onChange={(e) => setField({ repo_url: e.target.value })}
                  />
                </div>
                <div className={styles.field}>
                  <label className={styles.label} htmlFor="live_url">
                    Live URL
                  </label>
                  <input
                    id="live_url"
                    type="url"
                    className={styles.input}
                    value={form.live_url ?? ''}
                    onChange={(e) => setField({ live_url: e.target.value })}
                  />
                </div>
                <div className={`${styles.field} ${styles.fieldFull}`}>
                  <span className={styles.label}>Tags</span>
                  <TagInput
                    value={form.tags ?? []}
                    onChange={(next) => setField({ tags: next })}
                  />
                </div>
                <div className={`${styles.field} ${styles.fieldFull}`}>
                  <span className={styles.label}>Image</span>
                  <MediaPicker
                    value={form.image_media_id ?? null}
                    onChange={(id) => setField({ image_media_id: id })}
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
              <h2 className={styles.modalTitle}>Delete project</h2>
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

Component.displayName = 'AdminProjects'
