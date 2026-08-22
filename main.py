from contextlib import asynccontextmanager
from datetime import datetime, timezone
import logging
import math
from pathlib import Path
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from database import close_database, connect_database
from models import AnalysisInput, LoginRequest, RegisterRequest, RiskReport, TokenResponse, User
from routers.chat import router as chat_router
from security import create_access_token, current_user, hash_password, verify_password
from services.scoring import level, score
from services.stock import get_market_data, promised_trajectory
from services.vision import extract_claim


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.database_ready = False
    try:
        await connect_database()
        app.state.database_ready = True
    except Exception as exc:
        print(f"Database unavailable; persistence disabled: {exc}")
    yield
    await close_database()


app = FastAPI(title="SatyaFin AI", version="1.1.0", lifespan=lifespan)
app.include_router(chat_router, prefix="/api", tags=["AI Chatbot"])
logger = logging.getLogger("satyafin")


@app.exception_handler(Exception)
async def unhandled_exception_handler(_, exc: Exception):
    """Log unexpected failures without returning HTML/plain-text to the SPA."""
    logger.exception("Unhandled API error", exc_info=exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error. Check the server log and retry."})


def require_database() -> None:
    if not app.state.database_ready:
        raise HTTPException(503, "Database is currently unavailable. Check MONGODB_URL and retry.")


@app.post("/api/auth/register", response_model=TokenResponse)
async def register(payload: RegisterRequest):
    require_database()
    if await User.find_one(User.email == payload.email):
        raise HTTPException(409, "An account already exists for this email")
    if await User.find_one(User.username == payload.username):
        raise HTTPException(409, "That username is already taken")
    user = User(email=payload.email, username=payload.username, password_hash=hash_password(payload.password))
    await user.insert()
    return TokenResponse(access_token=create_access_token(str(user.id)))


@app.post("/api/auth/login", response_model=TokenResponse)
async def login(payload: LoginRequest):
    require_database()
    user = await User.find_one(User.username == payload.username)
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(401, "Incorrect username or password")
    return TokenResponse(access_token=create_access_token(str(user.id)))


async def run_analysis(claim: AnalysisInput, user: User) -> dict:
    market = await get_market_data(claim.ticker_symbol, claim.timeframe_days)
    annual = ((1 + claim.claimed_return_pct / 100) ** (365 / max(claim.timeframe_days, 1))) - 1
    excess = annual - market["real_stock_cagr"]
    adjusted = excess / max(market["vix"], .01)
    features = {"annualized_return": annual, "excess_over_benchmark": excess, "volatility_adjusted_claim": adjusted}
    risk_score = score(features)
    payload = {
        **claim.model_dump(), "ticker_symbol": market["ticker_symbol"], **features,
        "real_stock_cagr": market["real_stock_cagr"], "market_volatility_index": market["vix"],
        "risk_score": risk_score, "risk_level": level(risk_score),
        "rationale": f"Claim is {excess * 100:.1f}% annualized above live {market['ticker_symbol']} performance; VIX is {market['vix']:.1f}.",
        "promised_trajectory": promised_trajectory(claim.claimed_return_pct), "live_trajectory": market["live_trajectory"],
    }
    if app.state.database_ready:
        report = RiskReport(user_id=user.id, **payload)
        await report.insert()
        payload["id"] = str(report.id)
    return payload


@app.post("/api/analyze")
async def analyze(
    notes: str = Form(""), media: UploadFile | None = File(None), user: User = Depends(current_user)
):
    content = await media.read() if media else None
    extracted = await extract_claim(content, media.filename if media else None, notes)
    try:
        claim = AnalysisInput(**extracted)
    except Exception:
        raise HTTPException(422, "Could not extract a valid return claim. Include return percentage and timeframe in notes.")
    return await run_analysis(claim, user)


@app.post("/api/score")
async def score_claim(payload: AnalysisInput, user: User = Depends(current_user)):
    """Structured scoring endpoint for integrations that do not upload media."""
    return await run_analysis(payload, user)


@app.get("/api/reports/history")
async def report_history(user: User = Depends(current_user)):
    require_database()
    reports = await RiskReport.find(RiskReport.user_id == user.id).sort(-RiskReport.created_at).limit(50).to_list()
    return [{**report.model_dump(), "id": str(report.id), "user_id": str(report.user_id)} for report in reports]


@app.get("/api/health")
async def health():
    return {"status": "ok", "database": app.state.database_ready}


DIST = Path(__file__).parent / "dist"
if DIST.exists():
    app.mount("/assets", StaticFiles(directory=DIST / "assets"), name="assets")


@app.get("/{path:path}", include_in_schema=False)
async def spa(path: str):
    index = DIST / "index.html"
    requested = DIST / path
    if path and requested.is_file():
        return FileResponse(requested)
    if index.is_file():
        return FileResponse(index)
    raise HTTPException(404, "Frontend has not been built. Run: npm run build")
