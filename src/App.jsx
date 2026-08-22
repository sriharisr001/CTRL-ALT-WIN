import { useEffect, useState } from 'react'
import { ShieldCheck } from 'lucide-react'
import { useAuth } from './context/AuthContext'
import Analyzer from './components/Analyzer'
import ChatBot from './components/ChatBot'
import History from './components/History'
import Navbar from './components/Navbar'

const tabFromPath = () => ({ '/history': 'history', '/chat': 'chat' }[window.location.pathname] || 'analyze')
function AuthPage() {
  const { authenticate } = useAuth(); const [mode, setMode] = useState('login'); const [email, setEmail] = useState(''); const [username, setUsername] = useState(''); const [password, setPassword] = useState(''); const [error, setError] = useState(''); const register = mode === 'register'
  const submit = async event => { event.preventDefault(); setError(''); try { await authenticate(mode, { username, password, ...(register ? { email } : {}) }) } catch (err) { setError(err.message) } }
  return <main className="auth"><section className="auth-card"><ShieldCheck size={42}/><h1>SatyaFin AI</h1><p>Evidence-led investment risk analysis.</p><form onSubmit={submit}>{register && <input placeholder="Email" type="email" value={email} onChange={e=>setEmail(e.target.value)} required/>}<input placeholder="Username" value={username} onChange={e=>setUsername(e.target.value)} required minLength="3"/><input placeholder={register ? 'Password (8+ characters)' : 'Password'} type="password" value={password} onChange={e=>setPassword(e.target.value)} required minLength="8"/>{error&&<small className="error">{error}</small>}<button>{register ? 'Create account' : 'Sign in'}</button></form><a onClick={()=>{setMode(register?'login':'register');setError('')}}>{register ? 'Already have an account? Sign in' : 'New here? Create an account'}</a></section></main>
}
export default function App() { const { token, logout } = useAuth(); const [tab, setTab] = useState(tabFromPath); useEffect(() => { const update = () => setTab(tabFromPath()); addEventListener('popstate', update); return () => removeEventListener('popstate', update) }, []); if (!token) return <AuthPage/>; const navigate = (next, path) => { history.pushState({}, '', path); setTab(next) }; return <main><Navbar active={tab} onNavigate={navigate} onLogout={logout}/><section className="page">{tab === 'analyze' && <Analyzer/>}{tab === 'history' && <History/>}{tab === 'chat' && <ChatBot/>}</section></main> }
