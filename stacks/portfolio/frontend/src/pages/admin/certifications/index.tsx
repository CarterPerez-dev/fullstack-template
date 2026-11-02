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
  useCertifications,
  useCreateCertification,
  useDeleteCertification,
  useReorderCertifications,
  useUpdateCertification,
} from '@/api/hooks'
import {
  type CertificationInput,
  type CertificationResponse,
  ITEM_STATUS_LABELS,
  ItemStatus,
} from '@/api/types'
import { MediaPicker } from '../_components'
import styles from '../admin.module.scss'

type ModalState =
  | { type: 'closed' }
  | { type: 'create' }
  | { type: 'edit'; item: CertificationResponse }
  | { type: 'delete'; item: CertificationResponse }

const STATUS_CLASS: Record<ItemStatus, string> = {
  completed: styles.badgeCompleted,
  in_progress: styles.badgeInProgress,
  planned: styles.badgePlanned,
}

export function Component(): React.ReactElement {
  const { data, isLoading } = useCertifications()
  const create = useCreateCertification()
  const update = useUpdateCertification()
  const remove = useDeleteCertification()
  const reorder = useReorderCertifications()

  const [modal, setModal] = useState<ModalState>({ type: 'closed' })
  const [form, setForm] = useState<CertificationInput>({})

  const items = data ?? []

  const openCreate = (): void => {
    setForm({ status: ItemStatus.PLANNED })
    setModal({ type: 'create' })
  }

  const openEdit = (item: CertificationResponse): void => {
    setForm({
      name: item.name,
      code: item.code ?? '',
      issuer: item.issuer ?? '',
      status: item.status,
      issue_date: item.issue_date ?? '',
      credential_url: item.credential_url ?? '',
      badge_media_id: item.badge_media_id,
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

  const setField = (patch: Partial<CertificationInput>): void =>
    setForm((prev) => ({ ...prev, ...patch }))

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <div className={styles.headerLeft}>
          <span className={styles.headerTag}>Content</span>
          <h1 className={styles.title}>Certifications</h1>
        </div>
        <button type="button" className={styles.createBtn} onClick={openCreate}>
          <LuPlus />
          Add
        </button>
      </div>

      {isLoading && <div className={styles.loading}>Loading…</div>}
      {!isLoading && items.length === 0 && (
        <div className={styles.empty}>No certifications yet.</div>
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
              <p className={styles.cardTitle}>{item.name}</p>
              <p className={styles.cardSub}>
                {[item.code, item.issuer].filter(Boolean).join(' · ') || '—'}
              </p>
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
                {modal.type === 'create'
                  ? 'Add certification'
                  : 'Edit certification'}
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
                  <label className={styles.label} htmlFor="name">
                    Name
                  </label>
                  <input
                    id="name"
                    type="text"
                    className={styles.input}
                    value={form.name ?? ''}
                    onChange={(e) => setField({ name: e.target.value })}
                    required
                  />
                </div>
                <div className={styles.field}>
                  <label className={styles.label} htmlFor="code">
                    Code
                  </label>
                  <input
                    id="code"
                    type="text"
                    className={styles.input}
                    value={form.code ?? ''}
                    onChange={(e) => setField({ code: e.target.value })}
                  />
                </div>
                <div className={styles.field}>
                  <label className={styles.label} htmlFor="issuer">
                    Issuer
                  </label>
                  <input
                    id="issuer"
                    type="text"
                    className={styles.input}
                    value={form.issuer ?? ''}
                    onChange={(e) => setField({ issuer: e.target.value })}
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
                  <label className={styles.label} htmlFor="issue_date">
                    Date
                  </label>
                  <input
                    id="issue_date"
                    type="text"
                    className={styles.input}
                    placeholder="2026"
                    value={form.issue_date ?? ''}
                    onChange={(e) => setField({ issue_date: e.target.value })}
                  />
                </div>
                <div className={`${styles.field} ${styles.fieldFull}`}>
                  <label className={styles.label} htmlFor="credential_url">
                    Credential URL
                  </label>
                  <input
                    id="credential_url"
                    type="url"
                    className={styles.input}
                    value={form.credential_url ?? ''}
                    onChange={(e) => setField({ credential_url: e.target.value })}
                  />
                </div>
                <div className={`${styles.field} ${styles.fieldFull}`}>
                  <span className={styles.label}>Badge image</span>
                  <MediaPicker
                    value={form.badge_media_id ?? null}
                    onChange={(id) => setField({ badge_media_id: id })}
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
              <h2 className={styles.modalTitle}>Delete certification</h2>
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
                Delete “{modal.item.name}”? This cannot be undone.
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

Component.displayName = 'AdminCertifications'
