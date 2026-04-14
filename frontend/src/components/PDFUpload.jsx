import React, { useState, useEffect, useRef } from 'react'

export default function PDFUpload({ onUploadSuccess, token }) {
  const [documents, setDocuments] = useState([])
  const [uploading, setUploading] = useState(false)
  const [uploadStatus, setUploadStatus] = useState(null)
  const [isDragging, setIsDragging] = useState(false)
  const fileInputRef = useRef(null)

  useEffect(() => {
    if (token) fetchDocuments()
  }, [token])

  const fetchDocuments = async () => {
    try {
      const res = await fetch('/api/documents', {
        headers: { Authorization: `Bearer ${token}` },
      })
      const data = await res.json()
      // Strip the user{id}_ prefix when displaying filenames
      const clean = (data.documents || []).map(f => ({
        raw: f,
        display: f.replace(/^user\d+_/, ''),
      }))
      setDocuments(clean)
    } catch {
      setDocuments([])
    }
  }

  const handleUpload = async (file) => {
    if (!file) return
    if (!file.name.endsWith('.pdf')) {
      setUploadStatus({ type: 'error', message: 'Only PDF files are supported.' })
      return
    }

    setUploading(true)
    setUploadStatus(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await fetch('/api/upload', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      })
      const data = await res.json()

      if (!res.ok) throw new Error(data.detail || 'Upload failed')

      const displayName = data.filename.replace(/^user\d+_/, '')
      setUploadStatus({
        type: 'success',
        message: `✓ "${displayName}" loaded — ${data.chunks_loaded} chunks indexed`,
      })
      await fetchDocuments()
      if (onUploadSuccess) onUploadSuccess(data.filename)

    } catch (err) {
      setUploadStatus({ type: 'error', message: err.message })
    } finally {
      setUploading(false)
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  const handleDelete = async (rawFilename) => {
    try {
      await fetch(`/api/documents/${encodeURIComponent(rawFilename)}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      })
      await fetchDocuments()
      const displayName = rawFilename.replace(/^user\d+_/, '')
      setUploadStatus({ type: 'success', message: `✓ "${displayName}" removed from knowledge base` })
    } catch {
      setUploadStatus({ type: 'error', message: 'Failed to delete document.' })
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) handleUpload(file)
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => setIsDragging(false)

  return (
    <div style={{ padding: '16px', borderTop: '1px solid var(--border)' }}>

      {/* Section title */}
      <div style={{
        fontSize: '11px', fontWeight: '600', color: 'var(--text-muted)',
        textTransform: 'uppercase', letterSpacing: '0.7px', marginBottom: '10px',
      }}>
        📄 PDF Knowledge Base
      </div>

      {/* Drop zone */}
      <div
        onClick={() => fileInputRef.current?.click()}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        style={{
          border: `2px dashed ${isDragging ? 'var(--accent)' : 'var(--border)'}`,
          borderRadius: 'var(--radius-md)',
          padding: '14px 10px',
          textAlign: 'center',
          cursor: uploading ? 'not-allowed' : 'pointer',
          background: isDragging ? 'var(--accent-light)' : 'transparent',
          transition: 'all 0.2s',
          marginBottom: '10px',
        }}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          style={{ display: 'none' }}
          onChange={(e) => handleUpload(e.target.files[0])}
          disabled={uploading}
        />
        {uploading ? (
          <div style={{ fontSize: '12px', color: 'var(--accent)', fontWeight: '500' }}>
            ⏳ Uploading & indexing...
          </div>
        ) : (
          <>
            <div style={{ fontSize: '20px', marginBottom: '4px' }}>📂</div>
            <div style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: '500' }}>
              Drop PDF here or click to browse
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>
              Annual reports, filings, research papers
            </div>
          </>
        )}
      </div>

      {/* Status message */}
      {uploadStatus && (
        <div style={{
          fontSize: '11.5px', padding: '7px 10px', borderRadius: '6px', marginBottom: '10px',
          background: uploadStatus.type === 'success' ? '#dcfce7' : '#fef2f2',
          color: uploadStatus.type === 'success' ? '#16a34a' : '#dc2626',
          border: `1px solid ${uploadStatus.type === 'success' ? '#bbf7d0' : '#fecaca'}`,
        }}>
          {uploadStatus.message}
        </div>
      )}

      {/* Uploaded documents list */}
      {documents.length > 0 && (
        <div>
          <div style={{
            fontSize: '11px', color: 'var(--text-muted)', marginBottom: '6px', fontWeight: '500',
          }}>
            Indexed documents ({documents.length})
          </div>
          {documents.map(doc => (
            <div key={doc.raw} style={{
              display: 'flex', alignItems: 'center', justifyContent: 'space-between',
              padding: '6px 8px', borderRadius: '6px', marginBottom: '4px',
              background: 'var(--bg-main)', border: '1px solid var(--border)',
            }}>
              <div style={{
                fontSize: '12px', color: 'var(--text-secondary)',
                overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
                maxWidth: '140px',
              }}>
                📄 {doc.display}
              </div>
              <button
                onClick={() => handleDelete(doc.raw)}
                onMouseEnter={e => { e.currentTarget.style.background = '#fef2f2'; e.currentTarget.style.color = '#dc2626' }}
                onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = 'var(--text-muted)' }}
                style={{
                  background: 'transparent', border: 'none', cursor: 'pointer',
                  fontSize: '13px', color: 'var(--text-muted)', padding: '2px 6px',
                  borderRadius: '4px', transition: 'all 0.15s', flexShrink: 0,
                }}
                title="Remove from knowledge base"
              >
                ✕
              </button>
            </div>
          ))}
        </div>
      )}

      {documents.length === 0 && !uploading && (
        <div style={{ fontSize: '11.5px', color: 'var(--text-muted)', textAlign: 'center', padding: '4px 0' }}>
          No documents uploaded yet
        </div>
      )}
    </div>
  )
}
