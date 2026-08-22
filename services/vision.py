"""Gemini Vision fallback for financial-claim extraction."""
import asyncio
import json
import mimetypes
import random
import re
from typing import Any
from database import settings


def _fallback(text: str) -> dict[str, Any]:
    percent = re.search(r"(?:return|profit|roi)?\s*[:+]?\s*(\d+(?:\.\d+)?)\s*%", text, re.I)
    days = re.search(r"(\d+)\s*(?:days?|d)\b", text, re.I)
    ticker = re.search(r"\b(?:NYSE|NASDAQ)\s*[:\-]?\s*([A-Z]{1,5})\b|\$([A-Z]{1,5})\b", text)
    return {"claimed_return_pct": float(percent.group(1)) if percent else 0.0, "timeframe_days": int(days.group(1)) if days else 365, "ticker_symbol": (ticker.group(1) or ticker.group(2)) if ticker else "^GSPC"}


async def extract_claim(media: bytes | None, filename: str | None, notes: str = "") -> dict[str, Any]:
    """Use reviewed Tesseract OCR text first, then Gemini Vision as image fallback."""
    fallback = _fallback(notes)
    if notes.strip() or not media or not settings.gemini_api_key:
        return fallback
    mime_type = mimetypes.guess_type(filename or "")[0]
    if mime_type not in {"image/jpeg", "image/png", "image/webp"}:
        return fallback
    try:
        import google.generativeai as genai
        from google.api_core.exceptions import ResourceExhausted
        genai.configure(api_key=settings.gemini_api_key)
        prompt = ("Read this investment promotion carefully. Return only JSON containing claimed_return_pct "
                  "(number), timeframe_days (integer), and ticker_symbol (string). Use 0, 365, and ^GSPC if absent.")
        for attempt in range(5):
            try:
                model = genai.GenerativeModel("gemini-1.5-pro" if attempt == 0 else "gemini-1.5-flash")
                response = await asyncio.to_thread(model.generate_content, [prompt, {"mime_type": mime_type, "data": media}])
                match = re.search(r"\{.*\}", (response.text or "").strip().removeprefix("```json").removesuffix("```"), re.S)
                if not match:
                    raise ValueError("Gemini returned no structured claim")
                result = json.loads(match.group(0))
                return {**fallback, **{key: result[key] for key in fallback if key in result}}
            except ResourceExhausted:
                pass
            except Exception as exc:
                if "429" not in str(exc):
                    break
            await asyncio.sleep((2 ** attempt) + random.uniform(0, 0.5))
    except Exception:
        pass
    return fallback
