from beanie import Document
from pydantic import Field
from datetime import datetime

class User(Document):
    email: str
    hashed_password: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users" # MongoDB collection name

class FraudReport(Document):
    user_id: str
    extracted_claims: dict
    market_benchmark: dict = Field(default_factory=dict)
    risk_score: float
    is_sebi_verified: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "fraud_reports"

class SEBIEntity(Document):
    registration_no: str   # INH... = Research Analyst, INA... = Investment Adviser
    entity_name: str
    category: str          # "Research Analyst" or "Investment Adviser"
    status: str            # "ACTIVE" or "SUSPENDED"

    class Settings:
        name = "sebi_directory"
