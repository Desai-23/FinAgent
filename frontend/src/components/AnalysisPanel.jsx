import React from 'react'
import ReactMarkdown from 'react-markdown'

const STEPS = [
  { key: 'research', label: 'Research Agent', icon: '🔍', desc: 'Fetching stock data & company info' },
  { key: 'sentiment', label: 'Sentiment Agent', icon: '📰', desc: 'Reading news & analyzing sentiment' },
  { key: 'report', label: 'Report Agent', icon: '📝', desc: 'Writing final analysis report' },
]

function SentimentBadge({ sentiment, score }) {
  const colors = {
    Positive: { bg: '#dcfce7', color: '#16a34a', border: '#bbf7d0' },
    Negative: { bg: '#fef2f2', color: '#dc2626', border: '#fecaca' },
    Neutral:  { bg: '#f3f4f6', color: '#6b7280', border: '#e5e7eb' },
  }
  const c = colors[sentiment] || colors.Neutral
  return (
    <span style={{
      padding: '3px 10px', borderRadius: '20px', fontSize: '12px', fontWeight: '600',
      background: c.bg, color: c.color, border: `1px solid ${c.border}`,
    }}>
      {sentiment} {score > 0 ? `+${score}` : score}/10
    </span>
  )
}

export default function AnalysisPanel({ activeStep, result, error, ticker }) {
  if (!result && !error) {
    return (
      <div style={{
        background: 'white', border: '1px solid var(--border)',
        borderRadius: 'var(--radius-md)', padding: '20px', boxShadow: 'var(--shadow-sm)',
      }}>
        <div style={{ fontSize: '13px', fontWeight: '600', color: 'var(--text-secondary)', marginBottom: '16px' }}>
          🤖 Running Multi-Agent Analysis for <strong>{ticker}</strong>
        </div>
        <style>{`
          @keyframes bounce {
            0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
            30% { transform: translateY(-5px); opacity: 1; }
          }
        `}</style>
        {STEPS.map((step, i) => {
          const stepIndex = STEPS.findIndex(s => s.key === activeStep)
          const isDone = stepIndex > i
          const isActive = step.key === activeStep
          return (
            <div key={step.key} style={{
              display: 'flex', alignItems: 'center', gap: '12px', padding: '10px 0',
              borderBottom: i < STEPS.length - 1 ? '1px solid var(--border)' : 'none',
              opacity: isDone ? 0.5 : isActive ? 1 : 0.3, transition: 'opacity 0.3s',
            }}>
              <div style={{
                width: '32px', height: '32px', borderRadius: '50%', flexShrink: 0,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                background: isDone ? 'var(--accent-light)' : isActive ? 'var(--accent)' : 'var(--bg-sidebar)',
                fontSize: isDone ? '13px' : '15px',
                color: isActive ? 'white' : 'inherit',
              }}>
                {isDone ? '✓' : step.icon}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: '13.5px', fontWeight: '600', color: isActive ? 'var(--accent)' : 'var(--text-primary)' }}>
                  {step.label}
                  {isActive && <span style={{ marginLeft: '8px', fontSize: '12px', color: 'var(--text-muted)', fontWeight: '400' }}>working...</span>}
                </div>
                <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '2px' }}>{step.desc}</div>
              </div>
              {isActive && (
                <div style={{ display: 'flex', gap: '3px' }}>
                  {[0, 0.15, 0.3].map((d, i) => (
                    <div key={i} style={{
                      width: '5px', height: '5px', borderRadius: '50%', background: 'var(--accent)',
                      animation: 'bounce 1.2s infinite', animationDelay: `${d}s`,
                    }} />
                  ))}
                </div>
              )}
            </div>
          )
        })}
      </div>
    )
  }

  if (error) {
    return (
      <div style={{
        background: '#fef2f2', border: '1px solid #fecaca',
        borderRadius: 'var(--radius-md)', padding: '16px', fontSize: '13.5px', color: '#dc2626',
      }}>❌ {error}</div>
    )
  }

  return (
    <div style={{
      background: 'white', border: '1px solid var(--border)',
      borderRadius: 'var(--radius-md)', padding: '20px', boxShadow: 'var(--shadow-sm)',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
        <div style={{ fontSize: '14px', fontWeight: '700' }}>📊 {result.ticker} — Analysis Report</div>
        <SentimentBadge sentiment={result.sentiment} score={result.sentiment_score} />
      </div>
      {result.headlines?.length > 0 && (
        <div style={{ marginBottom: '14px' }}>
          <div style={{ fontSize: '11px', fontWeight: '600', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.7px', marginBottom: '6px' }}>
            Recent Headlines
          </div>
          {result.headlines.slice(0, 3).map((h, i) => (
            <div key={i} style={{ fontSize: '12.5px', color: 'var(--text-secondary)', padding: '5px 0', borderBottom: '1px solid var(--border)', lineHeight: 1.4 }}>
              • {h}
            </div>
          ))}
        </div>
      )}
      <div style={{ fontSize: '11px', fontWeight: '600', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.7px', marginBottom: '8px' }}>
        Full Report
      </div>
      <div className="message-content" style={{ fontSize: '13.5px', lineHeight: 1.7 }}>
        <ReactMarkdown>{result.final_report}</ReactMarkdown>
      </div>
    </div>
  )
}

