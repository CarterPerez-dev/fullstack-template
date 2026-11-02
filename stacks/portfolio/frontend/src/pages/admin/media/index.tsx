// ===================
// © AngelaMos | 2026
// index.tsx
// ===================

import { useState } from 'react'
import { LuFileText, LuTrash2, LuUpload, LuX } from 'react-icons/lu'
import { useDeleteMedia, useMediaList, useUploadMedia } from '@/api/hooks'
import type { MediaResponse } from '@/api/types'
import { mediaUrl } from '@/config'
import styles from '../admin.module.scss'

export function Component(): React.ReactElement {
  const { data, isLoading } = useMediaList()
  const upload = useUploadMedia()
  const remove = useDeleteMedia()
  const [pending, setPending] = useState<MediaResponse | null>(null)

  const items = data ?? []

  const onFiles = (files: FileList | null): void => {
    if (files === null) return
    for (const file of Array.from(files)) {
      upload.mutate(file)
    }
  }

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <div className={styles.headerLeft}>
          <span className={styles.headerTag}>Library</span>
          <h1 className={styles.title}>Media</h1>
          <p className={styles.subtitle}>
            Images and PDFs you can attach to any section.
          </p>
        </div>
      </div>

      <label className={styles.dropzone}>
        <LuUpload />
        <span>{upload.isPending ? 'Uploading…' : 'Click to upload files'}</span>
        <input
          type="file"
          hidden
          multiple
          onChange={(e) => onFiles(e.target.files)}
        />
      </label>

      {isLoading && <div className={styles.loading}>Loading…</div>}
      {!isLoading && items.length === 0 && (
        <div className={styles.empty}>No media uploaded yet.</div>
      )}

      {items.length > 0 && (
        <div className={styles.mediaGrid}>
          {items.map((item) => {
            const src = mediaUrl(item.id)
            const isImage = item.content_type.startsWith('image/')
            return (
              <div key={item.id} className={styles.mediaCard}>
                {isImage && src !== null ? (
                  <img
                    className={styles.mediaThumb}
                    src={src}
                    alt={item.original_filename}
                  />
                ) : (
                  <span className={styles.mediaThumbFile}>
                    <LuFileText />
                  </span>
                )}
                <div className={styles.mediaBody}>
                  <span className={styles.mediaName}>
                    {item.original_filename}
                  </span>
                  <button
                    type="button"
                    className={styles.iconBtnDanger}
                    onClick={() => setPending(item)}
                    aria-label="Delete"
                  >
                    <LuTrash2 />
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {pending !== null && (
        <div className={styles.modal}>
          <button
            type="button"
            className={styles.modalOverlay}
            onClick={() => setPending(null)}
            aria-label="Close"
          />
          <div className={styles.modalContent}>
            <div className={styles.modalHeader}>
              <h2 className={styles.modalTitle}>Delete media</h2>
              <button
                type="button"
                className={styles.modalClose}
                onClick={() => setPending(null)}
              >
                <LuX />
              </button>
            </div>
            <div className={styles.deleteConfirm}>
              <p className={styles.deleteText}>
                Delete “{pending.original_filename}”? Sections still pointing at
                it will lose their image.
              </p>
              <div className={styles.formActions}>
                <button
                  type="button"
                  className={styles.cancelBtn}
                  onClick={() => setPending(null)}
                >
                  Cancel
                </button>
                <button
                  type="button"
                  className={styles.deleteBtn}
                  onClick={() =>
                    remove.mutate(pending.id, {
                      onSuccess: () => setPending(null),
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

Component.displayName = 'AdminMedia'
