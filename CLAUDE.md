# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

A real-time stock scanner built with Fyers API, FastAPI, SQLAlchemy, Tailwind CSS, and DaisyUI with centralized logging capabilities.

## Project Overview

This is a simple intraday scanner project using Fyers API to fetch historical data and scan for buy/sell signals based on 10/20 EMA crossover strategy. It's a multi-user web application with OAuth2 integration for Fyers authentication.

## Tech Stack

- **Backend**: FastAPI (Python 3.12+)
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: Jinja2 Templates, Tailwind CSS, DaisyUI
- **API Integration**: Fyers API v3
- **Authentication**: Passlib (bcrypt), python-jose (JWT), OAuth2
- **Logging**: Python logging with rotation and centralized management
- **Data Processing**: pandas, numpy for EMA calculations
- **HTTP Client**: httpx for async API calls

## Development Commands

### Setup and Installation
```bash
# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Using main.py
python main.py

# Using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# With custom log level
LOG_LEVEL=DEBUG python main.py
```

### Database Operations
The database is automatically created on first run. To reset the database, simply delete `fyers_scanner.db`.

## Project Architecture

### Core Modules

1. **main.py** (FastAPI Application)
   - All route handlers for authentication, watchlist management, and scanning
   - Session-based authentication using SessionMiddleware
   - Jinja2 template rendering
   - Entry point: `uvicorn main:app`

2. **database.py** (SQLAlchemy Models)
   - `User`: Stores user credentials and Fyers API keys
   - `Watchlist`: User-created watchlists
   - `WatchlistSymbol`: Symbols in each watchlist
   - `ScanResult`: Historical scan results for tracking
   - Database URL: `sqlite:///./fyers_scanner.db`

3. **models.py** (Pydantic Schemas)
   - Request/response validation schemas
   - UserRegistration, UserLogin, WatchlistCreate, SymbolAdd, ScanRequest
   - ScanResultResponse, ScanSummaryResponse

4. **auth.py** (Authentication Utilities)
   - Password hashing using bcrypt via passlib
   - JWT token creation/validation using python-jose
   - Functions: `hash_password()`, `verify_password()`, `create_access_token()`, `decode_token()`

5. **fyers_api.py** (Fyers API Integration)
   - `FyersAPI` class with methods for:
     - `get_historical_data()`: Fetch OHLCV candles
     - `get_quotes()`: Get live market quotes
     - `get_auth_url()`: Generate OAuth2 authorization URL
     - `exchange_auth_code()`: Exchange auth code for access token
   - Base URL: `https://api-t1.fyers.in` (test environment)

6. **scanner.py** (EMA Scanner Logic)
   - `EMAScanner` class implementing:
     - `calculate_ema()`: Compute EMA using pandas
     - `detect_crossover()`: Identify bullish/bearish crossovers
     - `scan_symbol()`: Scan single symbol
     - `scan_watchlist()`: Scan multiple symbols
   - Strategy: 10 EMA crosses 20 EMA for BUY/SELL signals

7. **logger.py** (Centralized Logging)
   - RotatingFileHandler with 10 MB max size, 5 backup files
   - Logs to both console and file (`logs/fyers_scanner.log`)
   - Configurable log level via `LOG_LEVEL` environment variable

### Frontend Structure

**Templates** (`templates/` directory):
- `base.html`: Base template with navbar, DaisyUI theme
- `register.html`: User registration with Fyers credentials
- `login.html`: User login
- `dashboard.html`: Main dashboard showing watchlists and auth status
- `watchlist.html`: Manage symbols in a watchlist
- `scan.html`: Configure scan parameters (timeframe selection)
- `scan_results.html`: Display scan results with filtering

**Static Files** (`static/` directory):
- `style.css`: Custom CSS (minimal, as Tailwind handles most styling)

### Authentication Flow

1. **User Registration** (`/register`):
   - User provides username, email, password, Fyers App ID, and App Secret
   - Password hashed with bcrypt
   - Default watchlist created automatically

2. **User Login** (`/login`):
   - Credentials verified against database
   - Session created with user_id

3. **Fyers OAuth2** (`/fyers/auth` → `/fyers/callback`):
   - Generate auth URL with state parameter (CSRF protection)
   - User redirects to Fyers for authentication
   - Callback receives auth_code
   - Exchange auth_code for access_token using appIdHash (SHA-256 of app_id:app_secret)
   - Access token stored in user record

### Scanning Workflow

1. User selects a watchlist and timeframe (5/10/15 minutes)
2. System fetches historical data from Fyers API for each symbol
3. Calculate 10-period and 20-period EMAs using pandas
4. Detect crossovers by comparing current and previous EMA values
5. Generate BUY/SELL/NEUTRAL signals
6. Store results in `scan_results` table
7. Display results with summary statistics

### Important Implementation Notes

- **Symbol Format**: Must be `EXCHANGE:SYMBOL-TYPE` (e.g., `NSE:SBIN-EQ`)
- **Timeframes**: Only 5, 10, 15 minutes supported (configurable in scan.html)
- **OAuth Redirect URI**: Hardcoded to `http://127.0.0.1:8000/fyers/callback` (update for production)
- **Session Secret**: Uses environment variable `SECRET_KEY` or default (change in production!)
- **Data Requirements**: Need minimum 20 candles for EMA20 calculation

### Common Development Tasks

**Adding a new timeframe option**:
1. Update `scan.html` radio buttons
2. Ensure Fyers API supports the resolution
3. No backend changes needed

**Modifying EMA periods**:
- Edit `scanner.py` → `scan_symbol()` method
- Change periods in `calculate_ema()` calls
- Update UI labels in templates

**Adding new technical indicators**:
1. Extend `EMAScanner` class in `scanner.py`
2. Add new columns to `ScanResult` model in `database.py`
3. Update Pydantic schemas in `models.py`
4. Modify scan results template to display new data

**Logging and Debugging**:
- Check `logs/fyers_scanner.log` for detailed logs
- Set `LOG_LEVEL=DEBUG` for verbose output
- All Fyers API calls are logged with request/response info

## Database Schema Relationships

```
User (1) ──── (Many) Watchlist
Watchlist (1) ──── (Many) WatchlistSymbol
User (1) ──── (Many) ScanResult
Watchlist (1) ──── (Many) ScanResult
```

## Environment Variables

- `SECRET_KEY`: Session secret key (default: "your-secret-key-change-this-in-production")
- `LOG_LEVEL`: Logging level (default: "INFO", options: DEBUG, INFO, WARNING, ERROR)

## Known Limitations

- OAuth redirect URI is localhost (needs HTTPS for production)
- No WebSocket support for real-time updates (uses REST API only)
- Historical data limited to Fyers API quotas
- No Ta-Lib integration yet (using pandas for EMA calculations)
