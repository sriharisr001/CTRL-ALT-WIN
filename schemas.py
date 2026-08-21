from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class ReportCreate(BaseModel):
    claims: dict
    risk_score: float
    is_sebi_verified: bool