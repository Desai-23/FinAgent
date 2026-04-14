import React, { useEffect, useRef, useState } from 'react'
import ReactMarkdown from 'react-markdown'

const SUGGESTIONS = [
  "💵 What's the price of Apple stock?",
  "🏢 Tell me about Microsoft",
  "📊 What is Tesla's market cap?",
  "💡 What is a P/E ratio?",
]

function CopyButton({ text }) {
  const [copied, setCopied] = useState(false)
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {}
  }
  return (
    <button
      onClick={handleCopy}
      onMouseEnter={e => { e.currentTarget.style.background = 'var(--bg-sidebar)'; e.currentTarget.style.color = 'var(--text-primary)' }}
      onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = 'var(--text-muted)' }}
      style={{
        padding: '4px 10px', background: 'transparent', border: '1px solid var(--border)',
        borderRadius: '6px', cursor: 'pointer', fontSize: '11.5px', color: 'var(--text-muted)',
        fontFamily: 'var(--font-body)', display: 'flex', alignItems: 'center', gap: '4px',
        transition: 'all 0.15s', alignSelf: 'flex-start', marginTop: '2px',
      }}
    >
      {copied ? '✓ Copied' : '⎘ Copy'}
    </button>
  )
}

function TypingIndicator() {
  return (
    <div style={{ display: 'flex', padding: '4px 24px', maxWidth: '820px', width: '100%', alignSelf: 'center' }}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', width: '100%' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{
            width: '28px', height: '28px', borderRadius: '50%', background: 'var(--accent)',
            color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '12px', fontWeight: '600',
          }}>FA</div>
          <span style={{ fontSize: '13px', fontWeight: '600', color: 'var(--text-secondary)' }}>FinAgent</span>
        </div>
        <div style={{
          padding: '14px 18px', background: 'white', borderRadius: 'var(--radius-md)',
          boxShadow: 'var(--shadow-sm)', border: '1px solid var(--border)',
          display: 'flex', alignItems: 'center', gap: '5px',
        }}>
          <style>{`
            @keyframes bounce {
              0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
              30% { transform: translateY(-5px); opacity: 1; }
            }
          `}</style>
          {[0, 0.2, 0.4].map((delay, i) => (
            <div key={i} style={{
              width: '7px', height: '7px', borderRadius: '50%', background: 'var(--text-muted)',
              animation: 'bounce 1.2s infinite', animationDelay: `${delay}s`,
            }} />
          ))}
        </div>
      </div>
    </div>
  )
}

function AgenticReportCard({ data }) {
  const sentimentColors = {
    Positive: { bg: '#dcfce7', color: '#16a34a', border: '#bbf7d0' },
    Negative: { bg: '#fef2f2', color: '#dc2626', border: '#fecaca' },
    Neutral:  { bg: '#f3f4f6', color: '#6b7280', border: '#e5e7eb' },
  }
  const c = sentimentColors[data.sentiment] || sentimentColors.Neutral

  return (
    <div style={{
      border: '1px solid var(--border)', borderRadius: 'var(--radius-md)',
      background: 'white', padding: '20px', boxShadow: 'var(--shadow-sm)',
    }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
        <div style={{ fontSize: '14px', fontWeight: '700' }}>
          📊 {data.ticker} — Analysis Report
        </div>
        <span style={{
          padding: '3px 10px', borderRadius: '20px', fontSize: '12px', fontWeight: '600',
          background: c.bg, color: c.color, border: `1px solid ${c.border}`,
        }}>
          {data.sentiment} {data.sentiment_score > 0 ? `+${data.sentiment_score}` : data.sentiment_score}/10
        </span>
      </div>

      {/* Headlines */}
      {data.headlines?.length > 0 && (
        <div style={{ marginBottom: '14px' }}>
          <div style={{
            fontSize: '11px', fontWeight: '600', color: 'var(--text-muted)',
            textTransform: 'uppercase', letterSpacing: '0.7px', marginBottom: '6px',
          }}>
            Recent Headlines
          </div>
          {data.headlines.slice(0, 3).map((h, i) => (
            <div key={i} style={{
              fontSize: '12.5px', color: 'var(--text-secondary)',
              padding: '5px 0', borderBottom: '1px solid var(--border)', lineHeight: 1.4,
            }}>
              • {h}
            </div>
          ))}
        </div>
      )}

      {/* Full report */}
      <div style={{
        fontSize: '11px', fontWeight: '600', color: 'var(--text-muted)',
        textTransform: 'uppercase', letterSpacing: '0.7px', marginBottom: '8px',
      }}>
        Full Report
      </div>
      <div className="message-content" style={{ fontSize: '13.5px', lineHeight: 1.7 }}>
        <ReactMarkdown>{data.final_report}</ReactMarkdown>
      </div>
    </div>
  )
}

export default function ChatWindow({ messages, isTyping, onSuggestionClick, ModeTag }) {
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isTyping])

  if (messages.length === 0 && !isTyping) {
    return (
      <div style={{
        flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center',
        justifyContent: 'center', padding: '40px 20px', gap: '12px',
        color: 'var(--text-muted)', overflowY: 'auto',
      }}>
        <div style={{ fontSize: '40px' }}>🏦</div>
        <div style={{ fontSize: '20px', fontWeight: '600', color: 'var(--text-secondary)', letterSpacing: '-0.3px' }}>
          Ask FinAgent anything
        </div>
        <div style={{ fontSize: '14px', textAlign: 'center', lineHeight: 1.6, maxWidth: '300px' }}>
          Get real-time stock prices, company info, market caps, and finance explanations.
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', justifyContent: 'center', marginTop: '8px', maxWidth: '500px' }}>
          {SUGGESTIONS.map(s => (
            <button key={s} onClick={() => onSuggestionClick(s)}
              onMouseEnter={e => {
                e.currentTarget.style.background = 'var(--accent-light)'
                e.currentTarget.style.borderColor = 'var(--accent)'
                e.currentTarget.style.color = 'var(--accent)'
              }}
              onMouseLeave={e => {
                e.currentTarget.style.background = 'white'
                e.currentTarget.style.borderColor = 'var(--border)'
                e.currentTarget.style.color = 'var(--text-secondary)'
              }}
              style={{
                padding: '8px 14px', background: 'white', border: '1px solid var(--border)',
                borderRadius: '20px', fontSize: '13px', cursor: 'pointer',
                color: 'var(--text-secondary)', transition: 'all 0.15s', fontFamily: 'var(--font-body)',
              }}
            >{s}</button>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div style={{ flexShrink: 0, padding: '24px 0', display: 'flex', flexDirection: 'column', gap: '4px' }}>
      {messages.map(msg => {
        const isUser = msg.role === 'user'
        const isAgentic = msg.mode_used === 'AGENTIC' && msg.agenticData

        return (
          <div key={msg.id} style={{ display: 'flex', padding: '4px 24px', maxWidth: '820px', width: '100%', alignSelf: 'center' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', width: '100%' }}>

              {/* Avatar + name row */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <div style={{
                  width: '28px', height: '28px', borderRadius: '50%',
                  background: isUser ? '#e8e8ea' : 'var(--accent)',
                  color: isUser ? 'var(--text-secondary)' : 'white',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: '12px', fontWeight: '600', flexShrink: 0,
                }}>
                  {isUser ? 'U' : 'FA'}
                </div>
                <span style={{ fontSize: '13px', fontWeight: '600', color: 'var(--text-secondary)' }}>
                  {isUser ? 'You' : 'FinAgent'}
                </span>
              </div>

              {/* Message body */}
              {isAgentic ? (
                <AgenticReportCard data={msg.agenticData} />
              ) : (
                <div style={{
                  padding: '12px 16px', borderRadius: 'var(--radius-md)',
                  fontSize: '14.5px', lineHeight: 1.65, boxShadow: 'var(--shadow-sm)',
                  background: isUser ? 'var(--bg-message-user)' : 'var(--bg-message-agent)',
                  border: isUser ? 'none' : '1px solid var(--border)',
                }}>
                  {isUser ? (
                    <span>{msg.content}</span>
                  ) : (
                    <div className="message-content">
                      <ReactMarkdown>{msg.content}</ReactMarkdown>
                    </div>
                  )}
                </div>
              )}

              {/* Copy + mode tag row */}
              {!isUser && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <CopyButton text={msg.content} />
                  {ModeTag && msg.mode_used && <ModeTag mode={msg.mode_used} />}
                </div>
              )}

            </div>
          </div>
        )
      })}

      {isTyping && <TypingIndicator />}
      <div ref={bottomRef} />
    </div>
  )
}



