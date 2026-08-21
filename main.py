from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from fastapi.security import OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from contextlib import asynccontextmanager
import os
import httpx
from models import User, FraudReport, SEBIEntity
from security import get_password_hash, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from schemas import UserCreate, Token, ReportCreate
from dependencies import get_current_user
from market_data import fetch_benchmark_data
from datetime import timedelta

# Replace with your local or MongoDB Atlas connection string
MONGO_URI = "mongodb://localhost:27017/satyafin_db"

# Teammates' microservices. Defaults point at the in-process mocks below so the
# pipeline is testable before Members 3 and 4 ship. Override via env to go live:
#   AI_VISION_SERVICE_URL=http://localhost:8001/extract
#   ML_RISK_SERVICE_URL=http://localhost:8002/score
AI_VISION_SERVICE_URL = os.getenv(
    "AI_VISION_SERVICE_URL", "http://localhost:8000/mock/extract"
)   # Member 3
ML_RISK_SERVICE_URL = os.getenv(
    "ML_RISK_SERVICE_URL", "http://localhost:8000/mock/score"
)   # Member 4

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_URI)
    
    # Initialize Beanie with your models
    await init_beanie(
        database=client.satyafin_db,
        document_models=[User, FraudReport, SEBIEntity],
    )
    
    yield # App is running
    
    # Shutdown: Close connection
    client.close()

app = FastAPI(lifespan=lifespan)

# Let the React frontend talk to us. allow_credentials + explicit origins:
# a wildcard "*" is rejected by browsers once credentials are involved.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",   # Create React App
        "http://localhost:5173",   # Vite
    ],
    allow_credentials=True,
    allow_methods=["*"],           # GET, POST, OPTIONS, ...
    allow_headers=["*"],           # includes Authorization for the JWT
)

async def verify_sebi_id(reg_no: str | None) -> bool:
    """True only if the registration exists in our directory AND is active."""
    if not reg_no:
        return False

    # Normalise whatever the OCR gave us
    clean_id = reg_no.strip().upper()

    entity = await SEBIEntity.find_one(SEBIEntity.registration_no == clean_id)
    return entity is not None and entity.status == "ACTIVE"

@app.post("/api/analyze")
async def analyze_tip(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    # Only images. content_type can be None, so check that before startswith.
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed")

    file_bytes = await file.read()

    # One client session for both hops
    async with httpx.AsyncClient(timeout=60.0) as client:

        # --- 1. Member 3: AI / Vision extraction ---
        try:
            files = {"file": (file.filename, file_bytes, file.content_type)}
            ai_response = await client.post(AI_VISION_SERVICE_URL, files=files)
            ai_response.raise_for_status()
            extracted_claims = ai_response.json()
            # {"stock_symbol": "SUZLON", "claimed_return_pct": 50,
            #  "timeframe_days": 10, "mentioned_sebi_id": "INH00000XXXX"}
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"AI Vision Service offline: {exc}")
        except httpx.HTTPStatusError as exc:
            # Service answered, but with an error status
            raise HTTPException(
                status_code=502,
                detail=f"AI Vision Service failed: {exc.response.status_code}",
            )

        # --- 2. Live market benchmark (non-blocking) ---
        # Timeframe the scammer claimed; default to 30 days if the AI missed it.
        timeframe = extracted_claims.get("timeframe_days") or 30
        # yfinance is synchronous, so push it to a worker thread rather than
        # blocking the event loop for the duration of the HTTP call.
        market_data = await run_in_threadpool(fetch_benchmark_data, timeframe)

        # Give Member 4's model the claim AND the market reality to judge it against
        combined_ml_payload = {
            **extracted_claims,
            "market_context": market_data,
        }

        # --- 3. Member 4: ML risk classifier ---
        try:
            ml_response = await client.post(ML_RISK_SERVICE_URL, json=combined_ml_payload)
            ml_response.raise_for_status()
            risk_data = ml_response.json()
            # {"risk_score": 85.5}
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"ML Risk Service offline: {exc}")
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=502,
                detail=f"ML Risk Service failed: {exc.response.status_code}",
            )

    # --- 4. SEBI compliance check ---
    sebi_id = extracted_claims.get("mentioned_sebi_id")
    is_verified = await verify_sebi_id(sebi_id)

    # --- 5. Persist the report against the authenticated user ---
    new_report = FraudReport(
        user_id=str(current_user.id),
        extracted_claims=extracted_claims,
        market_benchmark=market_data,
        risk_score=risk_data.get("risk_score", 0.0),
        is_sebi_verified=is_verified
    )
    await new_report.insert()

    # --- 6. Hand the result back to the frontend (Member 1) ---
    return {
        "status": "success",
        "report_id": str(new_report.id),
        "data": {
            "claims": extracted_claims,
            "market_reality": market_data,
            "risk_score": risk_data.get("risk_score"),
            "is_sebi_verified": is_verified,
        },
    }

@app.post("/api/reports/save")
async def save_fraud_report(
    report_data: ReportCreate,
    current_user: User = Depends(get_current_user)
):
    # 1. Create a new document, taking the owner from the verified token
    #    rather than trusting a client-supplied user_id
    new_report = FraudReport(
        user_id=str(current_user.id),
        extracted_claims=report_data.claims,
        risk_score=report_data.risk_score,
        is_sebi_verified=report_data.is_sebi_verified
    )

    # 2. Insert it into the database
    await new_report.insert()
    return {
        "message": "Report saved successfully",
        "report_id": str(new_report.id),
        "saved_for": current_user.email,
    }

@app.get("/api/reports/history")
async def get_my_history(current_user: User = Depends(get_current_user)):
    # 3. Fetch ONLY the reports belonging to the logged-in user
    user_reports = await FraudReport.find(
        FraudReport.user_id == str(current_user.id)
    ).to_list()
    return user_reports

@app.post("/api/auth/register", response_model=dict)
async def register_user(user_data: UserCreate):
    # 1. Check if user already exists
    existing_user = await User.find_one(User.email == user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # 2. Hash the password and save
    hashed_password = get_password_hash(user_data.password)
    new_user = User(email=user_data.email, hashed_password=hashed_password)
    await new_user.insert()
    
    return {"message": "User registered successfully"}

@app.post("/api/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # 1. Find user in the database
    user = await User.find_one(User.email == form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    # 2. Verify password
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    # 3. Generate JWT Token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# =====================================================================
# DEV-ONLY SCAFFOLDING — delete before deploying
# =====================================================================

@app.post("/api/dev/seed-sebi")
async def seed_sebi_data():
    test_entities = [
        SEBIEntity(registration_no="INH000001234", entity_name="Trustworthy Research",
                   category="Research Analyst", status="ACTIVE"),
        SEBIEntity(registration_no="INA000099999", entity_name="Fake Advisors Ltd",
                   category="Investment Adviser", status="SUSPENDED"),
    ]

    # Skip any registration already present, so re-running doesn't pile up
    # duplicate rows that make verify_sebi_id's result depend on insert order.
    existing = await SEBIEntity.find(
        {"registration_no": {"$in": [e.registration_no for e in test_entities]}}
    ).to_list()
    already = {e.registration_no for e in existing}
    to_insert = [e for e in test_entities if e.registration_no not in already]

    if to_insert:
        await SEBIEntity.insert_many(to_insert)

    return {
        "message": "Test SEBI data injected",
        "inserted": [e.registration_no for e in to_insert],
        "skipped_existing": sorted(already),
    }

# --- MOCK FOR MEMBER 3 (AI / VISION) ---
@app.post("/mock/extract")
async def mock_ai_extraction(request: Request):
    # Ignores the uploaded image; returns hardcoded, correctly-shaped JSON
    return {
        "stock_symbol": "SUZLON",
        "claimed_return_pct": 50.0,
        "timeframe_days": 10,
        "mentioned_sebi_id": "INH000001234",  # matches the seeded ACTIVE entity
    }

# --- MOCK FOR MEMBER 4 (ML MODEL) ---
@app.post("/mock/score")
async def mock_ml_scoring(payload: dict):
    # Member 4 will eventually score this against the NIFTY 50 context we pass in.
    claimed_return = payload.get("claimed_return_pct", 0)

    if claimed_return > 20:
        return {"risk_score": 98.5}
    return {"risk_score": 12.0}
