import math
from datetime import datetime, timezone

import pandas as pd
import yfinance as yf

# Starter watchlist: Yahoo Finance symbols. Data availability and delay vary.
ASSETS = {
    "NIFTY 50": "^NSEI",
    "SENSEX": "^BSESN",
    "Apple (US)": "AAPL",
    "Bitcoin": "BTC-USD",
    "Ethereum": "ETH-USD",
}


def download_data(symbol: str) -> pd.DataFrame:
    data = yf.download(
        symbol,
        period="5d",
        interval="30m",
        auto_adjust=True,
        progress=False,
        threads=False,
    )
    if data is None or data.empty:
        return pd.DataFrame()

    # Recent yfinance versions can return MultiIndex columns for one ticker.
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    required = {"Close", "High", "Low"}
    if not required.issubset(set(data.columns)):
        return pd.DataFrame()

    data = data.dropna(subset=["Close", "High", "Low"])
    return data


def analyze(name: str, symbol: str) -> None:
    print("\n" + "=" * 58)
    print(f"{name} ({symbol})")

    try:
        df = download_data(symbol)
        if len(df) < 30:
            print("No usable data / insufficient candles. Try again later.")
            return

        close = df["Close"].astype(float)
        high = df["High"].astype(float)
        low = df["Low"].astype(float)

        ema20 = close.ewm(span=20, adjust=False).mean()
        ema50 = close.ewm(span=50, adjust=False).mean()

        delta = close.diff()
        gains = delta.clip(lower=0)
        losses = -delta.clip(upper=0)
        avg_gain = gains.ewm(alpha=1 / 14, min_periods=14, adjust=False).mean()
        avg_loss = losses.ewm(alpha=1 / 14, min_periods=14, adjust=False).mean()
        rs = avg_gain / avg_loss.replace(0, float("nan"))
        rsi = 100 - (100 / (1 + rs))

        previous_close = close.shift(1)
        true_range = pd.concat(
            [
                high - low,
                (high - previous_close).abs(),
                (low - previous_close).abs(),
            ],
            axis=1,
        ).max(axis=1)
        atr = true_range.ewm(alpha=1 / 14, min_periods=14, adjust=False).mean()

        price = float(close.iloc[-1])
        e20 = float(ema20.iloc[-1])
        e50 = float(ema50.iloc[-1])
        current_rsi = float(rsi.iloc[-1])
        current_atr = float(atr.iloc[-1])

        if not all(math.isfinite(v) for v in [price, e20, e50, current_rsi, current_atr]):
            print("Indicators not ready for this asset.")
            return

        if price > e20 > e50:
            trend = "Bullish alignment"
        elif price < e20 < e50:
            trend = "Bearish alignment"
        else:
            trend = "Mixed / sideways"

        recent = df.tail(20)
        support = float(recent["Low"].min())
        resistance = float(recent["High"].max())

        print(f"Latest candle timestamp: {df.index[-1]}")
        print(f"Latest close: {price:.4f}")
        print(f"EMA 20: {e20:.4f}")
        print(f"EMA 50: {e50:.4f}")
        print(f"RSI 14: {current_rsi:.2f}")
        print(f"ATR 14: {current_atr:.4f}")
        print(f"Trend: {trend}")
        print(f"Recent support estimate: {support:.4f}")
        print(f"Recent resistance estimate: {resistance:.4f}")
        print(f"Illustrative +/- 1 ATR range: {price-current_atr:.4f} to {price+current_atr:.4f}")
        print("Mode: analysis only; no orders placed.")
    except Exception as exc:
        print(f"Analysis failed for {symbol}: {type(exc).__name__}: {exc}")


def main() -> None:
    print("AI TRADING ANALYSIS — STARTER")
    print("Run time (UTC):", datetime.now(timezone.utc).isoformat())
    print("Data note: Yahoo Finance may be delayed, limited, or unavailable.")
    print("This report is informational, not a trading recommendation.")
    for name, symbol in ASSETS.items():
        analyze(name, symbol)
    print("\nRun finished.")


if __name__ == "__main__":
    main()
