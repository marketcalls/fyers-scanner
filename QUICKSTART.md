# Quick Start Guide

Get your Fyers Intraday Scanner running in 5 minutes!

## Prerequisites

- Python 3.12 or higher
- Fyers API credentials (App ID and App Secret)
- Get your credentials from: https://myapi.fyers.in/dashboard

## Installation Steps

### 1. Install Dependencies

```bash
# Remove any conflicting packages
pip uninstall -y jose

# Install required packages
pip install -r requirements.txt
```

### 2. Start the Application

```bash
python run.py
```

The application will start on http://localhost:8000

### 3. Register Your Account

1. Open http://localhost:8000 in your browser
2. Click "Register"
3. Fill in:
   - Username
   - Email
   - Password
   - **Fyers App ID** (from Fyers dashboard)
   - **Fyers App Secret** (from Fyers dashboard)
4. Click "Register"

### 4. Authenticate with Fyers

1. After registration, login with your credentials
2. Click **"Authenticate Fyers"** in the dashboard
3. You'll be redirected to Fyers login page
4. Login with your Fyers credentials
5. After successful authentication, you'll be redirected back to the dashboard

### 5. Create a Watchlist

1. In the dashboard, click **"Create Watchlist"**
2. Give it a name (e.g., "Nifty 50", "Bank Stocks")
3. Click "Create"

### 6. Add Symbols

1. Click **"Manage"** on your watchlist
2. Add symbols in the format: `EXCHANGE:SYMBOL-TYPE`
3. Examples:
   - `NSE:SBIN-EQ` - State Bank of India
   - `NSE:RELIANCE-EQ` - Reliance Industries
   - `NSE:TCS-EQ` - TCS
   - `NSE:INFY-EQ` - Infosys
   - `NSE:NIFTY50-INDEX` - Nifty 50 Index
4. Click **"Add Symbol"** for each

### 7. Run Your First Scan

1. Click **"Scan"** on your watchlist
2. Select a timeframe (5m, 10m, or 15m)
3. Click **"Start Scanning"**
4. View your results with BUY/SELL/NEUTRAL signals!

## Common Symbol Formats

### NSE Stocks (Equity)
```
NSE:SBIN-EQ
NSE:RELIANCE-EQ
NSE:TCS-EQ
NSE:INFY-EQ
NSE:HDFCBANK-EQ
NSE:ICICIBANK-EQ
```

### NSE Indices
```
NSE:NIFTY50-INDEX
NSE:NIFTYBANK-INDEX
NSE:NIFTYIT-INDEX
```

### BSE Stocks
```
BSE:SENSEX-INDEX
BSE:RELIANCE-EQ
```

## Understanding Signals

- **🟢 BUY**: 10 EMA crossed above 20 EMA (Bullish - consider buying)
- **🔴 SELL**: 10 EMA crossed below 20 EMA (Bearish - consider selling)
- **⚪ NEUTRAL**: No crossover detected (Hold/Wait)

## Troubleshooting

### "Access token not set"
→ Click "Authenticate Fyers" in the dashboard

### "No data available for symbol"
→ Check symbol format (must be `EXCHANGE:SYMBOL-TYPE`)

### "Not enough data points"
→ Symbol may not have enough historical data, try a different timeframe

### Application won't start
```bash
# Make sure all dependencies are installed
pip install -r requirements.txt

# Check for conflicting packages
pip uninstall -y jose
pip install PyJWT==2.8.0
```

## Need Help?

- Check the full [README.md](README.md) for detailed documentation
- Review [CLAUDE.md](CLAUDE.md) for architecture details
- Fyers API Docs: https://myapi.fyers.in/docsv3

---

**Ready to scan? Let's go! 🚀**
