"""Open-ended GuardFin Copilot chat endpoint."""
import asyncio
import json
import logging
import random

from fastapi import APIRouter, Depends

from database import settings
from models import ChatRequest, User
from security import current_user

router = APIRouter()
logger = logging.getLogger("guardfin.chat")
SYSTEM_PROMPT = """You are GuardFin Copilot, an expert AI financial advisor, market analyst, and fraud detection specialist.

BEHAVIOR RULES:
1. ANSWER ALL USER QUESTIONS FREELY. Whether the user asks about general stock markets, crypto, inflation, gold, tax laws, budgeting, scam red flags, or specific investment claims, provide a complete, clear, and helpful answer.
2. IF AN ACTIVE REPORT CONTEXT IS PROVIDED, use it as background knowledge to enrich your response when relevant, but DO NOT reject or refuse questions that fall outside of this context.
3. Keep responses structured, professional, and easy to read using Markdown formatting, bullet points, and brief clear paragraphs.
4. Never say that you can only answer questions related to a report or refuse general financial inquiries.
5. For personalised financial decisions, explain relevant factors, risks, and questions the user should consider; avoid claiming certainty about future returns.
"""
def fallback_answer(question: str) -> str:
    """Useful, question-specific response if the external model is temporarily unavailable."""
    lower = question.lower()
    if "tsla" in lower and "aapl" in lower:
        return ("**TSLA and AAPL suit different risk profiles.**\n\n"
                "- **Tesla (TSLA):** generally higher-growth and higher-volatility; results are more sensitive to EV demand, pricing, competition, and execution.\n"
                "- **Apple (AAPL):** generally a more mature, diversified business; key drivers include iPhone demand, services growth, margins, and valuation.\n\n"
                "Neither is automatically better. Compare valuation, earnings growth, concentration in your portfolio, time horizon, and how much volatility you can tolerate.")
    if "index fund" in lower or "mutual fund" in lower:
        return ("An **index fund** aims to track a market index, such as the S&P 500, usually with rules-based holdings and lower fees. "
                "A **mutual fund** can be actively managed, where a manager selects holdings in an attempt to beat a benchmark, often at a higher cost. "
                "Check the fund’s expense ratio, benchmark, diversification, tax treatment, and whether it matches your time horizon.")
    if "vix" in lower or "volatility" in lower:
        return ("The **VIX** is a market-implied measure of expected S&P 500 volatility over roughly the next 30 days. "
                "A higher VIX usually signals greater expected uncertainty, not a guaranteed market decline. It is best used as a sentiment and risk indicator alongside fundamentals and diversification.")
    if "gold" in lower:
        return ("Gold is often viewed as a diversifier because it can behave differently from shares and may attract demand during inflation or geopolitical stress. "
                "It is not risk-free: prices can be volatile, it produces no cash flow, and returns depend on market conditions. Consider its role in a diversified portfolio rather than treating it as a guaranteed safe asset.")
    return (f"Your question — **“{question.strip()}”** — deserves a tailored answer. The live AI service is temporarily unavailable, so I cannot reliably expand on it right now. "
            "Please retry shortly; when it reconnects, I’ll provide the detailed analysis rather than a generic claim review.")


def _contents(payload: ChatRequest) -> list[dict]:
    contents = []
    if payload.report_context:
        context = json.dumps(payload.report_context, default=str)[:8000]
        contents.append({"role": "user", "parts": [f"Active report context (use only when relevant):\n{context}"]})
        contents.append({"role": "model", "parts": ["I will use that report context when it helps answer the user's question."]})
    # Gemini requires the first turn to be a user turn. The UI greeting is an
    # assistant turn, so exclude leading assistant messages before forwarding.
    history = list(payload.chat_history)
    while history and history[0].role == "assistant":
        history.pop(0)
    for item in history:
        contents.append({"role": "model" if item.role == "assistant" else "user", "parts": [item.content]})
    contents.append({"role": "user", "parts": [payload.message.strip()]})
    return contents


@router.post("/chat")
async def chat(payload: ChatRequest, _: User = Depends(current_user)):
    """Answer any financial question; Gemini failures return a safe conversational reply."""
    if not settings.gemini_api_key:
        return {"message": fallback_answer(payload.message), "fallback": True}
    try:
        import google.generativeai as genai
        from google.api_core.exceptions import ResourceExhausted

        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=SYSTEM_PROMPT)
        for attempt in range(5):
            try:
                response = await asyncio.to_thread(model.generate_content, _contents(payload))
                answer = (response.text or "").strip()
                if answer:
                    return {"message": answer, "fallback": False}
            except ResourceExhausted:
                pass
            except Exception as exc:
                logger.warning("Gemini request failed on attempt %s: %s", attempt + 1, exc)
                if "429" not in str(exc):
                    return {"message": fallback_answer(payload.message), "fallback": True}
            await asyncio.sleep((2 ** attempt) + random.uniform(0, 0.5))
    except Exception:
        logger.exception("Gemini chat setup failed")
        return {"message": fallback_answer(payload.message), "fallback": True}
    return {"message": fallback_answer(payload.message), "fallback": True}
