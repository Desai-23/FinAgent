import React from 'react'
import PDFUpload from './PDFUpload'

export default function Sidebar({ sessions, activeSessionId, onNewChat, onSelectSession, onClearAll, user, onLogout, token }) {
  const [hoveredItem, setHoveredItem] = React.useState(null)
  const [hoveredLogout, setHoveredLogout] = React.useState(false)
  const [hoveredClear, setHoveredClear] = React.useState(false)

  return (
    <aside style={{
      width: 'var(--sidebar-width)', minWidth: 'var(--sidebar-width)',
      height: '100%', background: 'var(--bg-sidebar)',
      borderRight: '1px solid var(--border)',
      display: 'flex', flexDirection: 'column', overflow: 'hidden',
    }}>

      {/* Header — logo + new chat button */}
      <div style={{ padding: '20px 16px 12px', borderBottom: '1px solid var(--border)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '14px' }}>
          <div style={{
            width: '30px', height: '30px', background: 'var(--accent)',
            borderRadius: '8px', display: 'flex', alignItems: 'center',
            justifyContent: 'center', color: 'white', fontSize: '14px', fontWeight: '700',
          }}>F</div>
          <span style={{ fontSize: '16px', fontWeight: '600', letterSpacing: '-0.3px' }}>FinAgent</span>
        </div>
        <button
          onClick={onNewChat}
          onMouseEnter={e => e.currentTarget.style.background = 'var(--accent-light)'}
          onMouseLeave={e => e.currentTarget.style.background = 'white'}
          style={{
            width: '100%', padding: '9px 14px', background: 'white',
            border: '1px solid var(--border)', borderRadius: 'var(--radius-sm)',
            cursor: 'pointer', fontSize: '13.5px', fontWeight: '500',
            color: 'var(--text-primary)', fontFamily: 'var(--font-body)',
            display: 'flex', alignItems: 'center', gap: '8px', transition: 'background 0.15s',
          }}
        >
          <span style={{ fontSize: '16px' }}>+</span> New chat
        </button>
      </div>

      {/* Chats label */}
      {sessions.length > 0 && (
        <div style={{
          padding: '14px 16px 6px', fontSize: '11px', fontWeight: '600',
          color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.8px',
        }}>Chats</div>
      )}

      {/* Sessions list — scrollable, takes remaining space */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '4px 8px' }}>
        {sessions.length === 0 && (
          <div style={{ padding: '16px 10px', fontSize: '13px', color: 'var(--text-muted)', lineHeight: 1.5 }}>
            Your conversations will appear here.
          </div>
        )}
        {sessions.map(session => (
          <div
            key={session.id}
            onClick={() => onSelectSession(session.id)}
            onMouseEnter={() => setHoveredItem(session.id)}
            onMouseLeave={() => setHoveredItem(null)}
            style={{
              padding: '9px 10px', borderRadius: 'var(--radius-sm)', cursor: 'pointer',
              display: 'flex', alignItems: 'center', gap: '9px', marginBottom: '2px',
              background: session.id === activeSessionId
                ? 'rgba(26, 107, 74, 0.1)'
                : hoveredItem === session.id ? 'rgba(0,0,0,0.05)' : 'transparent',
            }}
          >
            <span style={{ fontSize: '13px', color: 'var(--text-muted)' }}>💬</span>
            <span style={{
              fontSize: '13.5px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
              fontWeight: session.id === activeSessionId ? '500' : '400',
              color: session.id === activeSessionId ? 'var(--accent)' : 'var(--text-primary)',
            }}>
              {session.title}
            </span>
          </div>
        ))}
      </div>

      {/* PDF Upload section */}
      <PDFUpload token={token} />

      {/* Clear all chats button */}
      <div style={{ padding: '8px 8px 0', borderTop: '1px solid var(--border)' }}>
        <button
          onClick={onClearAll}
          onMouseEnter={() => setHoveredClear(true)}
          onMouseLeave={() => setHoveredClear(false)}
          style={{
            width: '100%', padding: '9px 14px',
            background: hoveredClear ? 'rgba(0,0,0,0.05)' : 'transparent',
            border: 'none', borderRadius: 'var(--radius-sm)', cursor: 'pointer',
            fontSize: '13.5px', color: 'var(--text-secondary)', fontFamily: 'var(--font-body)',
            display: 'flex', alignItems: 'center', gap: '8px', transition: 'background 0.12s',
          }}
        >
          <span>🗑️</span> Clear all chats
        </button>
      </div>

      {/* User profile + logout — pinned to bottom */}
      <div style={{
        padding: '10px 12px 16px',
        borderTop: '1px solid var(--border)',
        marginTop: '4px',
      }}>
        {/* User info row */}
        <div style={{
          display: 'flex', alignItems: 'center', gap: '10px',
          padding: '8px 10px', borderRadius: 'var(--radius-sm)',
          background: 'rgba(0,0,0,0.03)', marginBottom: '6px',
        }}>
          {/* Avatar circle with initials */}
          <div style={{
            width: '30px', height: '30px', borderRadius: '50%',
            background: 'var(--accent)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            color: 'white', fontSize: '12px', fontWeight: '700', flexShrink: 0,
          }}>
            {(user?.full_name || user?.email || 'U')[0].toUpperCase()}
          </div>
          <div style={{ overflow: 'hidden', flex: 1 }}>
            <div style={{
              fontSize: '13px', fontWeight: '600', color: 'var(--text-primary)',
              overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
            }}>
              {user?.full_name || 'User'}
            </div>
            <div style={{
              fontSize: '11px', color: 'var(--text-muted)',
              overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
            }}>
              {user?.email}
            </div>
          </div>
        </div>

        {/* Logout button */}
        <button
          onClick={onLogout}
          onMouseEnter={() => setHoveredLogout(true)}
          onMouseLeave={() => setHoveredLogout(false)}
          style={{
            width: '100%', padding: '8px 14px',
            background: hoveredLogout ? 'rgba(220, 38, 38, 0.08)' : 'transparent',
            border: hoveredLogout ? '1px solid rgba(220, 38, 38, 0.2)' : '1px solid transparent',
            borderRadius: 'var(--radius-sm)', cursor: 'pointer',
            fontSize: '13px', color: hoveredLogout ? '#dc2626' : 'var(--text-secondary)',
            fontFamily: 'var(--font-body)',
            display: 'flex', alignItems: 'center', gap: '8px',
            transition: 'all 0.15s',
          }}
        >
          <span>→</span> Sign out
        </button>
      </div>

    </aside>
  )
}






