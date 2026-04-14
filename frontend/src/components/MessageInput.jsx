import React, { useState, useRef, useEffect } from 'react'

const MODES = [
  { key: 'auto',    label: '⚡ Auto',    desc: 'System decides intelligently' },
  { key: 'llm',     label: '💬 LLM',     desc: 'Direct chat with tools' },
  { key: 'rag',     label: '📚 RAG',     desc: 'Search knowledge base & PDFs' },
  { key: 'agentic', label: '🤖 Agentic', desc: 'Full multi-agent pipeline' },
]

export default function MessageInput({ onSend, disabled, inputRef: externalRef }) {
  const [value, setValue] = useState('')
  const [mode, setMode] = useState('auto')
  const internalRef = useRef(null)
  const ref = externalRef || internalRef

  useEffect(() => {
    if (ref.current) {
      ref.current.style.height = 'auto'
      ref.current.style.height = Math.min(ref.current.scrollHeight, 160) + 'px'
    }
  }, [value])

  const handleSend = () => {
    const trimmed = value.trim()
    if (!trimmed || disabled) return
    onSend(trimmed, mode)
    setValue('')
    if (ref.current) ref.current.style.height = 'auto'
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const canSend = value.trim() && !disabled

  const placeholders = {
    auto: 'Ask anything — system chooses the best approach...',
    llm: 'Ask any finance question with live data...',
    rag: 'Ask about finance concepts, definitions, or your uploaded PDFs...',
    agentic: 'Enter a ticker for deep analysis e.g. AAPL, TSLA, MSFT...',
  }

  const hints = {
    auto: 'Auto mode — routes to LLM, RAG, or Agent Pipeline intelligently',
    llm: 'LLM mode — Groq + Finnhub tools for live data',
    rag: 'RAG mode — searches ChromaDB knowledge base + uploaded PDFs',
    agentic: 'Agentic mode — Research → Sentiment → Report via LangGraph',
  }

  return (
    <div style={{ padding: '12px 24px 20px', background: 'var(--bg-main)' }}>
      <div style={{ maxWidth: '820px', margin: '0 auto' }}>

        {/* Mode pills */}
        <div style={{ display: 'flex', gap: '6px', marginBottom: '8px', alignItems: 'center' }}>
          <span style={{ fontSize: '11px', color: 'var(--text-muted)', marginRight: '2px' }}>Mode:</span>
          {MODES.map(m => (
            <button
              key={m.key}
              onClick={() => setMode(m.key)}
              title={m.desc}
              style={{
                padding: '4px 12px', borderRadius: '20px', fontSize: '12px',
                fontWeight: mode === m.key ? '600' : '400',
                cursor: 'pointer', fontFamily: 'var(--font-body)',
                border: '1px solid var(--border)',
                background: mode === m.key ? 'var(--accent)' : 'white',
                color: mode === m.key ? 'white' : 'var(--text-secondary)',
                transition: 'all 0.15s',
              }}
            >
              {m.label}
            </button>
          ))}
        </div>

        {/* Input box */}
        <div style={{
          display: 'flex', alignItems: 'flex-end', background: 'var(--bg-input)',
          border: `1px solid ${mode !== 'auto' && mode !== 'llm' ? 'var(--accent)' : 'var(--border)'}`,
          borderRadius: 'var(--radius-md)',
          boxShadow: mode !== 'auto' && mode !== 'llm' ? '0 0 0 3px rgba(26,107,74,0.1)' : 'var(--shadow-md)',
          padding: '10px 14px', gap: '10px', transition: 'all 0.2s',
        }}>
          <textarea
            ref={ref}
            value={value}
            onChange={e => setValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholders[mode]}
            rows={1}
            disabled={disabled}
            style={{
              flex: 1, background: 'transparent', border: 'none', outline: 'none',
              resize: 'none', fontSize: '14.5px', fontFamily: 'var(--font-body)',
              color: 'var(--text-primary)', lineHeight: 1.6,
              padding: '2px 0', maxHeight: '160px', overflowY: 'auto',
            }}
          />
          <button
            onClick={handleSend}
            disabled={!canSend}
            style={{
              width: '34px', height: '34px',
              background: canSend ? 'var(--accent)' : 'var(--border)',
              border: 'none', borderRadius: '8px',
              cursor: canSend ? 'pointer' : 'not-allowed',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              flexShrink: 0, color: 'white', fontSize: '15px', transition: 'background 0.15s',
            }}
          >
            {mode === 'agentic' ? '→' : '↑'}
          </button>
        </div>

        <div style={{ textAlign: 'center', fontSize: '11.5px', color: 'var(--text-muted)', marginTop: '8px' }}>
          {hints[mode]}
        </div>
      </div>
    </div>
  )
}