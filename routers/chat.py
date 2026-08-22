"""SatyaFin AI Chatbot endpoint with Gemini rate-limit handling."""
import asyncio
import random

from fastapi import APIRouter, Depends, HTTPException

from database import settings
from models import ChatRequest, User
from security import current_user

router = APIRouter()
SYSTEM_PROMPT = (
    "You are SatyaFin AI Chatbot, an expert AI financial analyst and fraud investigator. "
    "Provide concise, clear, and professional explanations on financial markets, ROI claims, "
    "stock metrics, and investment scam indicators. Do not give personalised investment advice."
)


def offline_answer(message: str) -> str:
    """Keep common chatbot questions useful when the external model is unavailable."""
    question = message.lower()
    if "cagr" in question:
        return "CAGR is the compound annual growth rate: (ending value / starting value)^(1 / years) - 1. It normalizes a return across time."
    if "vix" in question or "volatility" in question:
        return "VIX estimates expected S&P 500 volatility. A higher VIX generally means more uncertainty and risk in the market."
    if "gold" in question and "risk" in question:
        return "Gold is often treated as lower risk than speculative investments because it is liquid and diversified, but its price can still fall."
    if "red flag" in question or "scam" in question:
        return "Red flags include guaranteed returns, unusually high short-term profits, pressure to act quickly, missing SEBI registration details, and requests to send money to personal accounts."
    return "Review the claim for guaranteed returns, unrealistic timeframes, missing registration details, and whether the promised performance is supported by comparable market data."


@router.post("/chat")
async def chat(payload: ChatRequest, _: User = Depends(current_user)):
    if not settings.gemini_api_key:
        return {"message": offline_answer(payload.message)}
    try:
        import google.generativeai as genai
        from google.api_core.exceptions import ResourceExhausted

        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=SYSTEM_PROMPT)
        for attempt in range(5):
            try:
                response = await asyncio.to_thread(model.generate_content, payload.message.strip())
                answer = (response.text or "").strip()
                if answer:
                    return {"message": answer}
                raise ValueError("Gemini returned an empty response")
            except ResourceExhausted:
                pass
            except Exception as exc:
                if "429" not in str(exc):
                    return {"message": offline_answer(payload.message)}
            await asyncio.sleep((2 ** attempt) + random.uniform(0, 0.5))
    except HTTPException:
        raise
    except Exception:
        return {"message": offline_answer(payload.message)}
    return {"message": offline_answer(payload.message)}
