from datetime import datetime, timezone
from beanie import Document, PydanticObjectId
from pydantic import BaseModel, EmailStr, Field


class User(Document):
    email: EmailStr
    username: str = Field(min_length=3, max_length=32)
    password_hash: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "users"
        indexes = ["email", "username"]


class RiskReport(Document):
    user_id: PydanticObjectId
    ticker_symbol: str
    claimed_return_pct: float
    timeframe_days: int
    annualized_return: float
    real_stock_cagr: float
    market_volatility_index: float
    excess_over_benchmark: float
    volatility_adjusted_claim: float
    risk_score: int
    risk_level: str
    rationale: str
    promised_trajectory: list[float] = []
    live_trajectory: list[float] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "risk_reports"


class RegisterRequest(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=32, pattern=r"^[A-Za-z0-9_.-]+$")
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=32)
    password: str = Field(min_length=8, max_length=128)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AnalysisInput(BaseModel):
    claimed_return_pct: float
    timeframe_days: int = Field(gt=0, le=36500)
    ticker_symbol: str = "^GSPC"
