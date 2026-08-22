import { History, LogOut, MessageCircle, SearchCheck, ShieldCheck } from 'lucide-react'

const tabs = [
  { id: 'analyze', path: '/', label: 'Risk Analyzer', Icon: SearchCheck },
  { id: 'history', path: '/history', label: 'Audit History', Icon: History },
  { id: 'chat', path: '/chat', label: 'AI Chatbot', Icon: MessageCircle },
]

export default function Navbar({ active, onNavigate, onLogout }) {
  return <header><div className="brand"><ShieldCheck /> SatyaFin AI</div><nav aria-label="Main navigation">{tabs.map(({ id, path, label, Icon }) => <button key={id} className={active === id ? 'active' : ''} onClick={() => onNavigate(id, path)}><Icon size={16} /> {label}</button>)}<button className="logout" onClick={onLogout} title="Sign out" aria-label="Sign out"><LogOut size={17} /> Logout</button></nav></header>
}
