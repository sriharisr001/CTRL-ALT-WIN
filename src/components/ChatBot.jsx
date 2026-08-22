import { useEffect, useRef, useState } from 'react'
import { Loader2, Send, Sparkles } from 'lucide-react' 
import { useAuth } from '../context/AuthContext'
import { readApiResponse } from '../api'

const prompts = ['Why is gold low risk?', 'How is CAGR calculated?', 'What is VIX volatility?', 'Explain Red Flag indicators']

export default function ChatBot() {
  const { token } = useAuth(); 
  const [messages, setMessages] = useState([{ role: 'assistant', content: 'I’m SatyaFin AI Chatbot. Ask me about market metrics, risk signals, or suspicious investment claims.' }]); 
  const [input, setInput] = useState(''); 
  const [loading, setLoading] = useState(false); 
  const endRef = useRef(null)

  // FIX: Added curly braces to prevent returning a non-function value
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading])

  const send = async (text = input) => { 
    const message = text.trim(); 
    if (!message || loading) return; 
    setMessages(items => [...items, { role: 'user', content: message }]); 
    setInput(''); 
    setLoading(true); 
    
    try { 
      const response = await fetch('/api/chat', { 
        method: 'POST', 
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` }, 
        body: JSON.stringify({ message }) 
      }); 
      const data = await readApiResponse(response); 
      setMessages(items => [...items, { role: 'assistant', content: data.message }]) 
    } catch (error) { 
      setMessages(items => [...items, { role: 'assistant', content: `I couldn’t respond right now: ${error.message}` }]) 
    } finally { 
      setLoading(false) 
    } 
  }

  return (
    <section className="copilot">
      <div className="intro">
        <p className="eyebrow">SATYAFIN INTELLIGENCE</p>
        <h1><Sparkles size={30} /> AI Chatbot</h1>
        <p>Clear explanations for market data, risk claims, and scam indicators.</p>
      </div>
      <div className="card chat-card">
        <div className="quick-prompts">
          {prompts.map(prompt => (
            <button key={prompt} onClick={() => send(prompt)} disabled={loading}>{prompt}</button>
          ))}
        </div>
        
        <div className="messages" aria-live="polite">
          {messages.map((message, index) => (
            <div key={index} className={`message ${message.role}`}>{message.content}</div>
          ))}
          
          {loading && (
            <div className="message assistant typing">
              <Loader2 className="spin" size={16} /> SatyaFin AI Chatbot is reviewing…
            </div>
          )}
          <div ref={endRef} />
        </div>
        
        <form className="chat-input" onSubmit={event => { event.preventDefault(); send() }}>
          <input value={input} onChange={event => setInput(event.target.value)} placeholder="Ask SatyaFin AI Chatbot…" disabled={loading} maxLength="2000"/>
          <button className="primary" disabled={loading || !input.trim()}>
            <Send size={17} /> Send
          </button>
        </form>
      </div>
    </section>
  )
}