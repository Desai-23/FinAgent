import React, { useState, useRef, useEffect } from 'react'
import Sidebar from './components/Sidebar'
import ChatWindow from './components/ChatWindow'
import MessageInput from './components/MessageInput'
import AnalysisPanel from './components/AnalysisPanel'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import { sendMessage, clearHistory } from './api/finagent'
import { useAuth } from './context/AuthContext'

let messageIdCounter = 0
const nextId = () => ++messageIdCounter

function createSession(firstMessage = null) {
  return {
    id: Date.now(),
    title: firstMessage
      ? firstMessage.slice(0, 36) + (firstMessage.length > 36 ? '...' : '')
      : 'New chat',
    messages: [],
  }
}

function ModeTag({ mode }) {
  const labels = {
    LLM:     { text: 'Answered by: LLM',            color: '#6b7280', bg: '#f3f4f6' },
    RAG:     { text: 'Answered by: RAG',            color: '#7c3aed', bg: '#ede9fe' },
    AGENTIC: { text: 'Answered by: Agent Pipeline', color: '#16a34a', bg: '#dcfce7' },
  }
  const l = labels[mode]
  if (!l) return null
  return (
    <span style={{
      fontSize: '11px', padding: '2px 8px', borderRadius: '10px',
      background: l.bg, color: l.color, fontWeight: '500',
      display: 'inline-block', marginTop: '4px',
    }}>
      {l.text}
    </span>
  )
}

// ─── Main App (shown when logged in) ─────────────────────────────────────────
function MainApp() {
  const { token, user, logout } = useAuth()

  const [sessions, setSessions] = useState([])
  const [activeSessionId, setActiveSessionId] = useState(null)
  const [isTyping, setIsTyping] = useState(false)
  const [error, setError] = useState(null)
  const inputRef = useRef(null)

  const [isAnalysing, setIsAnalysing] = useState(false)
  const [analysisStep, setAnalysisStep] = useState(null)
  const [analysisResult, setAnalysisResult] = useState(null)
  const [analysisError, setAnalysisError] = useState(null)
  const [analysisTicker, setAnalysisTicker] = useState(null)

  const activeSession = sessions.find(s => s.id === activeSessionId) || null
  const messages = activeSession?.messages || []

  useEffect(() => { inputRef.current?.focus() }, [activeSessionId])

  const resetAnalysis = () => {
    setIsAnalysing(false)
    setAnalysisStep(null)
    setAnalysisResult(null)
    setAnalysisError(null)
    setAnalysisTicker(null)
  }

  const ensureSession = (text) => {
    if (activeSessionId) return activeSessionId
    const session = createSession(text)
    setSessions(prev => [session, ...prev])
    setActiveSessionId(session.id)
    return session.id
  }

  const handleNewChat = async () => {
    try { await clearHistory(token) } catch {}
    const session = createSession()
    setSessions(prev => [session, ...prev])
    setActiveSessionId(session.id)
    setError(null)
    resetAnalysis()
  }

  const handleSelectSession = (id) => {
    setActiveSessionId(id)
    setError(null)
    resetAnalysis()
  }

  const handleClearAll = async () => {
    try { await clearHistory(token) } catch {}
    setSessions([])
    setActiveSessionId(null)
    setError(null)
    resetAnalysis()
  }

  const handleLogout = async () => {
    try { await clearHistory(token) } catch {}
    logout()
  }

  const handleSend = async (text, mode = 'auto') => {
    setError(null)
    resetAnalysis()

    const sessionId = ensureSession(text)
    const userMsg = { id: nextId(), role: 'user', content: text }

    setSessions(prev => prev.map(s =>
      s.id === sessionId ? {
        ...s,
        messages: [...s.messages, userMsg],
        title: s.messages.length === 0
          ? text.slice(0, 36) + (text.length > 36 ? '...' : '')
          : s.title,
      } : s
    ))

    setIsTyping(true)

    try {
      await sendMessage(text, mode, token, {
        onStep: (event) => {
          setIsAnalysing(true)
          setAnalysisTicker(event.ticker || analysisTicker)
          setAnalysisStep(event.step)
          setIsTyping(false)
        },

        onDone: (event) => {
          if (event.mode_used === 'AGENTIC') {
            setAnalysisResult(event.data)
            setAnalysisTicker(event.data.ticker)
            setIsAnalysing(false)
            const agentMsg = {
              id: nextId(),
              role: 'agent',
              mode_used: 'AGENTIC',
              content: event.data.final_report,
              agenticData: event.data,
            }
            setSessions(prev => prev.map(s =>
              s.id === sessionId ? { ...s, messages: [...s.messages, agentMsg] } : s
            ))
          } else {
            const agentMsg = {
              id: nextId(),
              role: 'agent',
              content: event.data.final_report,
              mode_used: event.mode_used || 'LLM',
            }
            setSessions(prev => prev.map(s =>
              s.id === sessionId ? { ...s, messages: [...s.messages, agentMsg] } : s
            ))
            resetAnalysis()
          }
        },

        onError: (msg) => {
          setAnalysisError(msg)
          setIsAnalysing(false)
          setError(`Error: ${msg}`)
        },
      })
    } catch (err) {
      setError(`Error: ${err.message}. Make sure the backend is running on port 8006.`)
      resetAnalysis()
    } finally {
      setIsTyping(false)
    }
  }

  const showAnalysis = isAnalysing || analysisResult || analysisError

  return (
    <div style={{ display: 'flex', height: '100vh', overflow: 'hidden', background: 'var(--bg-main)' }}>
      <Sidebar
        sessions={sessions}
        activeSessionId={activeSessionId}
        onNewChat={handleNewChat}
        onSelectSession={handleSelectSession}
        onClearAll={handleClearAll}
        user={user}
        onLogout={handleLogout}
        token={token}
      />
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', minWidth: 0 }}>

        {/* Header */}
        <div style={{
          padding: '14px 24px', borderBottom: '1px solid var(--border)',
          background: 'var(--bg-main)', display: 'flex',
          alignItems: 'center', justifyContent: 'space-between', flexShrink: 0,
        }}>
          <span style={{ fontSize: '14.5px', fontWeight: '500', color: 'var(--text-secondary)' }}>
            {activeSession ? activeSession.title : 'FinAgent — AI Financial Assistant'}
          </span>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            {/* Logged in user */}
            <span style={{ fontSize: '12.5px', color: 'var(--text-muted)' }}>
              👤 {user?.full_name || user?.email}
            </span>
            <span style={{ fontSize: '12.5px', color: 'var(--text-muted)', display: 'flex', alignItems: 'center' }}>
              <span style={{
                width: '7px', height: '7px', borderRadius: '50%',
                background: '#22c55e', display: 'inline-block', marginRight: '6px',
              }} />
              Connected
            </span>
          </div>
        </div>

        {/* Error banner */}
        {error && (
          <div style={{
            padding: '10px 24px', background: '#fef2f2',
            borderBottom: '1px solid #fecaca', fontSize: '13px', color: '#dc2626',
            display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          }}>
            <span>{error}</span>
            <button
              onClick={() => setError(null)}
              style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '16px', color: '#dc2626' }}
            >×</button>
          </div>
        )}

        {/* Chat + Analysis area */}
        <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column' }}>
          <ChatWindow
            messages={messages}
            isTyping={isTyping && !isAnalysing}
            onSuggestionClick={(text) => handleSend(text, 'auto')}
            ModeTag={ModeTag}
          />

          {/* Analysis panel anchored below the last message */}
          {showAnalysis && (
            <div style={{
              padding: '0 24px 24px',
              maxWidth: '820px',
              width: '100%',
              alignSelf: 'center',
              boxSizing: 'border-box',
            }}>
              <div style={{
                display: 'flex', alignItems: 'center', gap: '8px',
                marginBottom: '8px', padding: '4px 0',
              }}>
                <div style={{
                  width: '28px', height: '28px', borderRadius: '50%',
                  background: 'var(--accent)', color: 'white',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: '12px', fontWeight: '600', flexShrink: 0,
                }}>FA</div>
                <span style={{ fontSize: '13px', fontWeight: '600', color: 'var(--text-secondary)' }}>
                  FinAgent
                </span>
                <span style={{
                  fontSize: '11px', padding: '2px 8px', borderRadius: '10px',
                  background: '#dcfce7', color: '#16a34a', fontWeight: '500',
                }}>
                  Answered by: Agent Pipeline
                </span>
              </div>

              <AnalysisPanel
                activeStep={analysisStep}
                result={analysisResult}
                error={analysisError}
                ticker={analysisTicker}
              />
            </div>
          )}
        </div>

        <MessageInput
          onSend={handleSend}
          disabled={isTyping || isAnalysing}
          inputRef={inputRef}
        />
      </main>
    </div>
  )
}

// ─── Root — shows login/register or main app ──────────────────────────────────
export default function App() {
  const { isLoggedIn } = useAuth()
  const [authPage, setAuthPage] = useState('login') // 'login' | 'register'

  if (!isLoggedIn) {
    if (authPage === 'register') {
      return <RegisterPage onSwitchToLogin={() => setAuthPage('login')} />
    }
    return <LoginPage onSwitchToRegister={() => setAuthPage('register')} />
  }

  return <MainApp />
}
