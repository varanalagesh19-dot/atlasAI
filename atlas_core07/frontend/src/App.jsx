import { useState, useEffect } from 'react'
import './App.css'

export default function App() {
  const [conversations, setConversations] = useState([])
  const [currentChat, setCurrentChat] = useState(null)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [theme, setTheme] = useState('dark')

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

  useEffect(() => {
    loadConversations()
    const savedTheme = localStorage.getItem('atlas_theme') || 'dark'
    setTheme(savedTheme)
    document.documentElement.setAttribute('data-theme', savedTheme)
  }, [])

  const loadConversations = async () => {
    try {
      const res = await fetch(`${API_URL}/conversations`)
      const data = await res.json()
      setConversations(data || [])
    } catch (err) {
      console.error('Error loading conversations:', err)
    }
  }

  const newChat = async () => {
    try {
      const res = await fetch(`${API_URL}/conversations`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: 'New Chat', model: 'atlas_smart' })
      })
      const conv = await res.json()
      setCurrentChat(conv)
      setMessages(conv.messages || [])
      loadConversations()
    } catch (err) {
      console.error('Error creating chat:', err)
    }
  }

  const sendMessage = async () => {
    if (!input.trim() || !currentChat || loading) return

    const userMsg = { role: 'user', content: input }
    const newMessages = [...messages, userMsg]
    setMessages(newMessages)
    setInput('')
    setLoading(true)

    try {
      // Add user message to backend
      await fetch(`${API_URL}/conversations/${currentChat.id}/messages`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userMsg)
      })

      // Get AI response
      const res = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: newMessages,
          model: currentChat.model
        })
      })

      const { content } = await res.json()
      const aiMsg = { role: 'assistant', content }
      
      setMessages([...newMessages, aiMsg])
      
      // Add AI response to backend
      await fetch(`${API_URL}/conversations/${currentChat.id}/messages`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(aiMsg)
      })
    } catch (err) {
      console.error('Error sending message:', err)
    } finally {
      setLoading(false)
    }
  }

  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark'
    setTheme(newTheme)
    localStorage.setItem('atlas_theme', newTheme)
    document.documentElement.setAttribute('data-theme', newTheme)
  }

  return (
    <div className="app">
      <div className="sidebar">
        <div className="sidebar-header">
          <h1>atlas_core07</h1>
          <button onClick={toggleTheme} className="theme-btn">
            {theme === 'dark' ? '☀️' : '🌙'}
          </button>
        </div>
        <button onClick={newChat} className="new-chat-btn">
          + New Chat
        </button>
        <div className="conversations-list">
          {conversations.map(conv => (
            <div
              key={conv.id}
              className={`conversation-item ${currentChat?.id === conv.id ? 'active' : ''}`}
              onClick={() => {
                setCurrentChat(conv)
                setMessages(conv.messages || [])
              }}
            >
              {conv.title}
            </div>
          ))}
        </div>
      </div>

      <div className="main-content">
        {!currentChat ? (
          <div className="welcome">
            <h2>Welcome to atlas_core07</h2>
            <p>Click "New Chat" to start a conversation</p>
          </div>
        ) : (
          <>
            <div className="messages">
              {messages.map((msg, idx) => (
                <div key={idx} className={`message ${msg.role}`}>
                  <div className="message-content">{msg.content}</div>
                </div>
              ))}
              {loading && <div className="message assistant">typing...</div>}
            </div>

            <div className="input-area">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                placeholder="Type your message..."
                disabled={loading}
              />
              <button onClick={sendMessage} disabled={loading}>
                {loading ? '...' : 'Send'}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
