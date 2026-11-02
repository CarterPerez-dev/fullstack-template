// ===================
// © AngelaMos | 2026
// _components.tsx
// ===================

import { useState } from 'react'
import { LuFileText, LuUpload, LuX } from 'react-icons/lu'
import { useMediaList, useUploadMedia } from '@/api/hooks'
import { mediaUrl } from '@/config'
import styles from './admin.module.scss'

interface TagInputProps {
  value: string[]
  onChange: (next: string[]) => void
  placeholder?: string
}

export function TagInput({
  value,
  onChange,
  placeholder,
}: TagInputProps): React.ReactElement {
  const [draft, setDraft] = useState('')

  const add = (): void => {
    const trimmed = draft.trim()
    if (trimmed.length === 0 || value.includes(trimmed)) {
      setDraft('')
      return
    }
    onChange([...value, trimmed])
    setDraft('')
  }

  return (
    <div className={styles.tagEditor}>
      {value.length > 0 && (
        <div className={styles.tagList}>
          {value.map((tag) => (
            <span key={tag} className={styles.tag}>
              {tag}
              <button
                type="button"
                className={styles.tagRemove}
                onClick={() => onChange(value.filter((t) => t !== tag))}
                aria-label={`Remove ${tag}`}
              >
                <LuX />
              </button>
            </span>
          ))}
        </div>
      )}
      <div className={styles.tagAddRow}>
        <input
          type="text"
          className={styles.input}
          value={draft}
          placeholder={placeholder ?? 'Add and press Enter'}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              e.preventDefault()
              add()
            }
          }}
        />
        <button type="button" className={styles.mediaPickBtn} onClick={add}>
          Add
        </button>
      </div>
    </div>
  )
}

interface LineListProps {
  value: string[]
  onChange: (next: string[]) => void
  placeholder?: string
}

export function LineList({
  value,
  onChange,
  placeholder,
}: LineListProps): React.ReactElement {
  const setAt = (index: number, text: string): void => {
    const next = [...value]
    next[index] = text
    onChange(next)
  }

  return (
    <div className={styles.lineList}>
      {value.map((line, index) => (
        <div key={index} className={styles.lineRow}>
          <input
            type="text"
            className={styles.input}
            value={line}
            placeholder={placeholder}
            onChange={(e) => setAt(index, e.target.value)}
          />
          <button
            type="button"
            className={styles.iconBtnDanger}
            onClick={() => onChange(value.filter((_, i) => i !== index))}
            aria-label="Remove line"
          >
            <LuX />
          </button>
        </div>
      ))}
      <button
        type="button"
        className={styles.mediaPickBtn}
        onClick={() => onChange([...value, ''])}
      >
        Add line
      </button>
    </div>
  )
}

interface MediaPickerProps {
  value: string | null
  onChange: (id: string | null) => void
  accept?: 'image' | 'any'
}

export function MediaPicker({
  value,
  onChange,
  accept = 'image',
}: MediaPickerProps): React.ReactElement {
  const [open, setOpen] = useState(false)
  const { data: media } = useMediaList()
  const upload = useUploadMedia()
  const preview = mediaUrl(value)

  const items =
    accept === 'image'
      ? (media ?? []).filter((m) => m.content_type.startsWith('image/'))
      : (media ?? [])

  const onFile = (file: File | undefined): void => {
    if (file === undefined) return
    upload.mutate(file, { onSuccess: (created) => onChange(created.id) })
  }

  return (
    <div className={styles.mediaPicker}>
      {preview !== null && (
        <img className={styles.mediaPickPreview} src={preview} alt="Selected" />
      )}
      <button
        type="button"
        className={styles.mediaPickBtn}
        onClick={() => setOpen(true)}
      >
        {value === null ? 'Choose file' : 'Change'}
      </button>
      {value !== null && (
        <button
          type="button"
          className={styles.mediaPickBtn}
          onClick={() => onChange(null)}
        >
          Clear
        </button>
      )}

      {open && (
        <div className={styles.modal}>
          <button
            type="button"
            className={styles.modalOverlay}
            onClick={() => setOpen(false)}
            aria-label="Close"
          />
          <div className={styles.modalContent}>
            <div className={styles.modalHeader}>
              <h2 className={styles.modalTitle}>Select media</h2>
              <button
                type="button"
                className={styles.modalClose}
                onClick={() => setOpen(false)}
              >
                <LuX />
              </button>
            </div>

            <label className={styles.dropzone}>
              <LuUpload />
              <span>
                {upload.isPending ? 'Uploading…' : 'Click to upload a file'}
              </span>
              <input
                type="file"
                hidden
                accept={accept === 'image' ? 'image/*' : undefined}
                onChange={(e) => onFile(e.target.files?.[0])}
              />
            </label>

            {items.length > 0 && (
              <div className={styles.mediaGrid}>
                {items.map((item) => {
                  const src = mediaUrl(item.id)
                  return (
                    <button
                      key={item.id}
                      type="button"
                      className={styles.mediaCard}
                      onClick={() => {
                        onChange(item.id)
                        setOpen(false)
                      }}
                    >
                      {src !== null && item.content_type.startsWith('image/') ? (
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
                      <span className={styles.mediaBody}>
                        <span className={styles.mediaName}>
                          {item.original_filename}
                        </span>
                      </span>
                    </button>
                  )
                })}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
