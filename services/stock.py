import asyncio
import math
import yfinance as yf


def _market_data(symbol: str, timeframe_days: int) -> dict:
    symbol = (symbol or "^GSPC").upper().strip()
    try:
        history = yf.Ticker(symbol).history(period="2y", auto_adjust=True)
        if len(history) < 2:
            symbol, history = "^GSPC", yf.Ticker("^GSPC").history(period="2y", auto_adjust=True)
        closes = history["Close"].dropna()
        days = min(timeframe_days, len(closes) - 1)
        start, end = float(closes.iloc[-days - 1]), float(closes.iloc[-1])
        cagr = (end / start) ** (365 / max(days, 1)) - 1
        trajectory = (closes.iloc[-min(60, len(closes)): ] / closes.iloc[-min(60, len(closes))]) .tolist()
        vix = yf.Ticker("^VIX").history(period="5d", auto_adjust=True)["Close"].dropna()
        return {"ticker_symbol": symbol, "real_stock_cagr": float(cagr), "vix": float(vix.iloc[-1]) if not vix.empty else 20.0,
                "live_trajectory": [round(float(x), 4) for x in trajectory]}
    except Exception:
        return {"ticker_symbol": "^GSPC", "real_stock_cagr": 0.08, "vix": 20.0, "live_trajectory": [1 + i * 0.001 for i in range(60)]}


async def get_market_data(symbol: str, timeframe_days: int) -> dict:
    return await asyncio.to_thread(_market_data, symbol, timeframe_days)


def promised_trajectory(claimed_return_pct: float, points: int = 60) -> list[float]:
    return [round((1 + claimed_return_pct / 100) ** (i / (points - 1)), 4) for i in range(points)]
