# CTRL-ALT-WIN
SatyaFin - SEBI Fraud & Unregistered Finfluencer Inspector 🛡️🇮🇳
SatyaFin is an AI-powered, SEBI-focused fraud detection tool designed for identifying illegal financial scams, guaranteed return promises, and unregistered finfluencers across Indian social media, Telegram, WhatsApp, and financial web posts.

                       ┌──────────────────────────────┐
                       │       React + Tailwind       │
                       │   Frontend Dashboard (3000)  │
                       └──────────────┬───────────────┘
                                      │
                                      │ POST /api/analyze
                                      ▼
                       ┌──────────────────────────────┐
                       │     Node.js + Express        │
                       │    Main Backend (5000)       │
                       └──────────────┬───────────────┘
                                      │
                                      │ Forward Payload
                                      ▼
                       ┌──────────────────────────────┐
                       │    Python FastAPI Micro      │
                       │    AI & Risk Engine (8000)   │
                       └──────────────────────────────┘
The system comprises 4 core modules matching team workflows:

**Frontend (frontend/):** React (Vite) + Tailwind CSS dashboard with an interactive SVG Scam Risk Meter gauge, input tabs (Screenshot upload, Paste text, Link input), preset sample scam buttons for quick hackathon demos, SEBI intermediary verification badges, and market benchmark comparison graphs.

**Main Backend (backend/):** Node.js Express server listening on port 5000. Manages API orchestration (POST /api/analyze), saves scan reports to MongoDB (with zero-config in-memory fallback store if MongoDB is offline), and serves scan history.

**AI Vision Module (ai-service/):** Python FastAPI microservice on port 8000. Integrates Google Gemini 2.5 / 1.5 Vision API with strict Pydantic schema parsing to extract stock_symbol, claimed_return_pct, timeframe_days, and mentioned_sebi_id from screenshots or text. Includes offline heuristic fallback.

**Risk / ML Engine (ai-service/app/engine/risk_calculator.py):** Rule-based & market volatility heuristic scoring algorithm that calculates annualized returns, compares them against Nifty 50 historical benchmarks (~12.5% CAGR), evaluates SEBI compliance rules (guaranteed return prohibitions, unregistered finfluencers), and yields a final 0 to 100 Fraud Score.
