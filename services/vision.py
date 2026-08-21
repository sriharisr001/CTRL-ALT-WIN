import asyncio
import random
import re
from typing import Any
from database import settings


def _fallback(text: str) -> dict[str, Any]:
    percent = re.search(r"(?:return|profit|roi)?\s*[:+]?\s*(\d+(?:\.\d+)?)\s*%", text, re.I)
    days = re.search(r"(\d+)\s*(?:days?|d)\b", text, re.I)
    ticker = re.search(r"\b(?:NYSE|NASDAQ)\s*[:\-]?\s*([A-Z]{1,5})\b|\$([A-Z]{1,5})\b", text)
    return {
        "claimed_return_pct": float(percent.group(1)) if percent else 0.0,
        "timeframe_days": int(days.group(1)) if days else 365,
        "ticker_symbol": (ticker.group(1) or ticker.group(2)) if ticker else "^GSPC",
    }


async def extract_claim(media: bytes | None, filename: str | None, notes: str = "") -> dict[str, Any]:
    """Ask Gemini Vision for strict financial claim fields with 429-aware fallbacks."""
    fallback = _fallback(notes)
    if not media or not settings.gemini_api_key:
        return fallback
    try:
        import google.generativeai as genai
        from google.api_core.exceptions import ResourceExhausted
        genai.configure(api_key=settings.gemini_api_key)
        prompt = ("Read this investment promotion. Return ONLY JSON with claimed_return_pct (number), "
                  "timeframe_days (integer), ticker_symbol (string). Use ^GSPC when unknown.")
        mime = "image/jpeg" if (filename or "").lower().endswith((".jpg", ".jpeg")) else "image/png"
        for attempt in range(5):
            model_name = "gemini-1.5-pro" if attempt == 0 else "gemini-1.5-flash"
            try:
                model = genai.GenerativeModel(model_name)
                response = await asyncio.to_thread(model.generate_content, [prompt, {"mime_type": mime, "data": media}])
                cleaned = response.text.strip().removeprefix("```json").removesuffix("```").strip()
                import json
                result = json.loads(cleaned)
                return {**fallback, **{k: result[k] for k in fallback if k in result}}
            except ResourceExhausted:
                pass
            except Exception as exc:
                if "429" not in str(exc):
                    break
            await asyncio.sleep((2 ** attempt) + random.uniform(0, 0.6))
    except Exception:
        pass
    return fallback
