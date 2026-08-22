import { useState } from 'react'
import Tesseract from 'tesseract.js'
import { FileScan, LoaderCircle, Upload } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import StockChart from './StockChart'
import { readApiResponse } from '../api'

export default function Analyzer() {
  const { token } = useAuth(); const [notes, setNotes] = useState(''); const [file, setFile] = useState(); const [result, setResult] = useState(); const [loading, setLoading] = useState(false); const [ocrLoading, setOcrLoading] = useState(false); const [ocrStatus, setOcrStatus] = useState(''); const [error, setError] = useState('')
  const readImage = async image => {
    setFile(image); setError(''); setOcrLoading(true); setOcrStatus('Reading image…')
    try {
      if (!image.type.startsWith('image/')) throw new Error('Please upload a readable image file (PNG, JPEG, or WebP).')
      const { data } = await Tesseract.recognize(image, 'eng', { logger: item => item.status === 'recognizing text' && setOcrStatus(`OCR ${Math.round(item.progress * 100)}%`) })
      const text = data.text.trim(); if (text.length < 3) throw new Error('No readable text was found. Use a sharper, well-lit image with larger text.')
      setNotes(text); setOcrStatus('Text extracted — review it before analysis.')
    } catch (err) { setOcrStatus(''); setError(`OCR failed: ${err.message}`) } finally { setOcrLoading(false) }
  }
  const submit = async event => { event.preventDefault(); setLoading(true); setError(''); const body = new FormData(); body.append('notes', notes); if (file) body.append('media', file); try { const response = await fetch('/api/analyze', { method: 'POST', headers: { Authorization: `Bearer ${token}` }, body }); const data = await readApiResponse(response); setResult(data) } catch (err) { setError(err.message) } finally { setLoading(false) } }
  return <><div className="intro"><p className="eyebrow">DUE DILIGENCE, ACCELERATED</p><h1>Test the investment claim against reality.</h1><p>Use local OCR to read a promotion, review its extracted text, then compare it with live market data.</p></div><div className="workspace"><form className="card form" onSubmit={submit}><h2>New analysis</h2><label>Promotion, screenshot, or text claim</label><textarea value={notes} onChange={event => setNotes(event.target.value)} placeholder="Example: Earn 25% in 30 days with NASDAQ: AAPL"/><label className="drop"><Upload size={20}/><span>{file?.name || 'Attach an image to extract its text'}</span><input type="file" accept="image/png,image/jpeg,image/webp" onChange={event => event.target.files?.[0] && readImage(event.target.files[0])}/></label>{ocrLoading && <p className="ocr-status"><LoaderCircle className="spin" size={15}/> {ocrStatus}</p>}{!ocrLoading && ocrStatus && <p className="ocr-status"><FileScan size={15}/> {ocrStatus}</p>}{error && <p className="error">{error}</p>}<button className="primary" disabled={loading || ocrLoading}>{loading ? <><LoaderCircle className="spin"/> Analyzing claim…</> : 'Run risk analysis'}</button></form>{result ? <Results result={result}/> : <div className="card empty">Your result will include a risk score, market comparison, and saved audit record.</div>}</div></>
}
function Results({ result: r }) { return <section className="results"><div className="card score-card"><div><p className="eyebrow">RISK ASSESSMENT</p><h2>{r.ticker_symbol}</h2><p>{r.rationale}</p></div><div className={`ring ${r.risk_level.toLowerCase()}`} style={{ '--score': `${r.risk_score * 3.6}deg` }}><b>{r.risk_score}</b><small>/100</small></div><span className={`badge ${r.risk_level.toLowerCase()}`}>{r.risk_level} RISK</span></div><div className="metrics"><Metric label="Claimed return" value={`${r.claimed_return_pct}%`}/><Metric label="Annualized claim" value={`${(r.annualized_return * 100).toFixed(1)}%`}/><Metric label="Live CAGR" value={`${(r.real_stock_cagr * 100).toFixed(1)}%`}/><Metric label="VIX" value={r.market_volatility_index.toFixed(1)}/></div><div className="card"><StockChart promised={r.promised_trajectory} live={r.live_trajectory}/></div></section> }
function Metric({ label, value }) { return <div className="metric"><small>{label}</small><strong>{value}</strong></div> }
