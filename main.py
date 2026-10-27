import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timezone

ASSETS = {
    "NIFTY 50": "^NSEI",
    "SENSEX": "^BSESN",
    "APPLE": "AAPL",
    "BITCOIN": "BTC-USD",
    "ETHEREUM": "ETH-USD",
}


def analyze_asset(name, symbol):
    print(f"\n{'=' * 45}")
    print(f"ASSET: {name} ({symbol})")

    try:
        df = yf.download(
            symbol,
            period="5d",
            interval="30m",
            progress=False,
            auto_adjust=True,
            threads=False
        )

        if df.empty or len(df) < 30:
            print("Insufficient market data.")
            return

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        close = df["Close"].squeeze().dropna()
        high = df["High"].squeeze()
        low = df["Low"].squeeze()

        if len(close) < 30:
            print("Insufficient closing prices.")
            return

        # Moving averages
        ema20 = close.ewm(span=20, adjust=False).mean()
        ema50 = close.ewm(span=50, adjust=False).mean()

        # RSI (14)
        delta = close.diff()
        gains = delta.clip(lower=0)
        losses = -delta.clip(upper=0)

        avg_gain = gains.ewm(
            alpha=1/14, min_periods=14, adjust=False
        ).mean()

        avg_loss = losses.ewm(
            alpha=1/14, min_periods=14, adjust=False
        ).mean()

        rs = avg_gain / avg_loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))

        # Average True Range (14)
        previous_close = close.shift(1)

        true_range = pd.concat(
            [
                high - low,
                (high - previous_close).abs(),
                (low - previous_close).abs()
            ],
            axis=1
        ).max(axis=1)

        atr = true_range.ewm(
            alpha=1/14, min_periods=14, adjust=False
        ).mean()

        price = float(close.iloc[-1])
        e20 = float(ema20.iloc[-1])
        e50 = float(ema50.iloc[-1])
        current_rsi = float(rsi.iloc[-1])
        current_atr = float(atr.iloc[-1])

        if not all(np.isfinite(x) for x in
                   [price, e20, e50, current_rsi, current_atr]):
            print("Indicator calculation unavailable.")
            return

        if price > e20 > e50:
            trend = "Bullish trend"
        elif price < e20 < e50:
            trend = "Bearish trend"
        else:
            trend = "Mixed / sideways"

        # Recent support and resistance estimates
        recent = df.tail(20)
        support = float(recent["Low"].min())
        resistance = float(recent["High"].max())

        print(f"Latest candle time: {df.index[-1]}")
        print(f"Price: {price:.4f}")
        print(f"EMA 20: {e20:.4f}")
        print(f"EMA 50: {e50:.4f}")
        print(f"RSI 14: {current_rsi:.2f}")
        print(f"ATR 14: {current_atr:.4f}")
        print(f"Trend: {trend}")
        print(f"Recent support estimate: {support:.4f}")
        print(f"Recent resistance estimate: {resistance:.4f}")

        print(
            f"Illustrative 1-ATR range: "
            f"{price-current_atr:.4f} to "
            f"{price+current_atr:.4f}"
        )

        print("Status: Analysis only; no trade executed.")

    except Exception as error:
        print(f"Data/analysis error: {error}")


def main():
    print("AI TRADING ANALYSIS AGENT")
    print("UTC time:", datetime.now(timezone.utc).isoformat())
    print("Mode: Analysis only")

    for name, symbol in ASSETS.items():
        analyze_asset(name, symbol)

    print("\nAnalysis run completed.")


if __name__ == "__main__":
    main()
