import pandas as pd
import yfinance as yf


def fetch_benchmark_data(timeframe_days: int) -> dict:
    """
    Synchronous NIFTY 50 fetch. Called via run_in_threadpool so the blocking
    network I/O inside yfinance doesn't stall the FastAPI event loop.
    """
    try:
        # ^NSEI is the Yahoo Finance ticker for NIFTY 50
        nifty = yf.Ticker("^NSEI")

        # Fetch a window comfortably wider than the claim's timeframe so the
        # lookback below has real trading days to land on.
        if timeframe_days <= 20:
            period = "1mo"
        elif timeframe_days <= 75:
            period = "3mo"
        elif timeframe_days <= 150:
            period = "6mo"
        elif timeframe_days <= 300:
            period = "1y"
        else:
            period = "2y"

        hist = nifty.history(period=period)

        if hist.empty or len(hist) < 2:
            return {"error": "Could not fetch market data"}

        closes = hist["Close"]
        latest_date = hist.index[-1]
        current_price = closes.iloc[-1]

        # Walk back by CALENDAR days, not row count. hist has one row per
        # trading day (~21/month), so indexing back `timeframe_days` rows
        # would reach ~1.45x further into the past than the claim covers.
        target_date = latest_date - pd.Timedelta(days=timeframe_days)
        past_index = int(closes.index.searchsorted(target_date, side="right")) - 1
        truncated = past_index < 0
        past_index = max(0, past_index)
        past_price = closes.iloc[past_index]

        actual_return_pct = ((current_price - past_price) / past_price) * 100

        # Daily volatility: std deviation of day-over-day returns, in percent
        daily_returns = closes.pct_change().dropna()
        volatility = daily_returns.std() * 100

        result = {
            "benchmark_symbol": "NIFTY_50",
            "actual_return_pct": round(float(actual_return_pct), 2),
            "market_volatility_index": round(float(volatility), 2),
            "requested_timeframe_days": timeframe_days,
            "actual_days_covered": int((latest_date - closes.index[past_index]).days),
        }
        if truncated:
            # Not enough history for the requested window; we compared against
            # the oldest bar we have. Downstream should know the span is short.
            result["truncated"] = True
        return result

    except Exception as e:
        print(f"Market Data Error: {e}")
        return {"error": str(e)}
