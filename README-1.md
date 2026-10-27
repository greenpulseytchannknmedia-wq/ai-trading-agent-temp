# AI Trading Analysis (starter)

## Files
- `main.py`: downloads available candles and reports EMA 20/50, RSI, ATR, and recent support/resistance estimates.
- `.github/workflows/analysis.yml`: manually runnable workflow plus scheduled runs at minutes 17 and 47 each hour (UTC).
- `requirements.txt`: Python dependencies.

## Install / run on GitHub
1. Create the `.github/workflows/` folders in your repository if they do not exist.
2. Upload `main.py` and `requirements.txt` to the repository root.
3. Upload `analysis.yml` to `.github/workflows/analysis.yml`.
4. Open **Actions** → **AI Trading Analysis** → **Run workflow**.
5. Open the run and inspect the **Run market analysis** logs.

## Limitations
- GitHub Actions is scheduled automation, not a guaranteed always-on 24/7 process.
- Yahoo Finance data availability, delay, symbol coverage, and rate limits vary.
- Support/resistance are simple recent-candle estimates. The ATR range is illustrative, not a probability forecast.
- This starter does not yet fetch news, modify TradingView charts, send Telegram messages, or place orders.
- No live trading is performed.
