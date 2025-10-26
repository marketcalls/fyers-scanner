# Fyers Intraday Scanner

A real-time stock scanner built with Fyers API, FastAPI, SQLAlchemy, Tailwind CSS, and DaisyUI. Detects 10/20 EMA crossover signals for intraday trading.

## Features

- **Multi-user Support**: Secure user authentication and registration
- **Fyers OAuth Integration**: OAuth2 authentication with Fyers API
- **Automatic Token Management**: Daily token cleanup at 3:00 AM IST (tokens expire after 24 hours)
- **Watchlist Management**: Create and manage multiple watchlists with custom symbols
- **Historical Crossover Detection**: Detects ALL 10 EMA and 20 EMA crossovers in the last 5 days
- **Multiple Timeframes**: Scan on 5-minute, 10-minute, or 15-minute charts
- **Real-time Data**: Fetches historical data from Fyers API
- **Dark/Light Theme**: Toggle between dark and light modes with persistent preference
- **Beautiful UI**: Modern, responsive Supabase-inspired interface
- **Centralized Logging**: Comprehensive logging with rotation for debugging and monitoring

## Scanner Strategy

The scanner detects ALL EMA crossover events in the last 5 days:

- **Positive EMA Crossover**: When 10 EMA crosses above 20 EMA (Bullish signal)
- **Negative EMA Crossover**: When 10 EMA crosses below 20 EMA (Bearish signal)

Each crossover event includes:
- Timestamp and date of the crossover
- Symbol ticker
- Close price at crossover
- EMA10 and EMA20 values at crossover

Results are displayed in chronological order with filtering options for positive/negative signals.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/marketcalls/fyers-scanner.git
cd fyers-scanner
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On Linux/Mac
source venv/bin/activate
```

3. Install dependencies:
```bash
# Important: Remove any conflicting jose package first
pip uninstall -y jose

# Install requirements
pip install -r requirements.txt
```

4. Set up environment variables (optional):
```bash
# On Windows (PowerShell)
$env:SECRET_KEY="your-secure-secret-key"
$env:LOG_LEVEL="INFO"

# On Linux/Mac
export SECRET_KEY="your-secure-secret-key"
export LOG_LEVEL="INFO"
```

## Running the Application

Start the FastAPI server:
```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The application will be available at: http://localhost:8000

## First Time Setup

1. **Register**: Create an account with your Fyers API credentials
   - You'll need your Fyers App ID and App Secret
   - Get these from: https://myapi.fyers.in/dashboard

2. **Authenticate with Fyers**: After logging in, click "Authenticate Fyers" to complete OAuth2 flow
   - This will redirect you to Fyers login
   - After successful login, you'll be redirected back with an access token

3. **Create a Watchlist**: Add a watchlist and populate it with symbols
   - Symbol format: `EXCHANGE:SYMBOL-TYPE`
   - Examples: `NSE:SBIN-EQ`, `NSE:RELIANCE-EQ`, `NSE:NIFTY50-INDEX`

4. **Run a Scan**: Select a watchlist, choose a timeframe, and run the scan

## Automatic Token Management

**Important**: Fyers access tokens expire after 24 hours. To handle this automatically:

- The application runs a **scheduled task that clears all user tokens daily at 3:00 AM IST**
- After 3:00 AM, users will need to re-authenticate with Fyers
- A warning message will appear on the dashboard when your token has expired
- Simply click "Connect Fyers" or "Re-authenticate" to get a fresh token

This ensures compliance with Fyers' token expiration policy and maintains security.

**How it works:**
- Uses APScheduler with IST timezone settings
- Scheduled job runs at exactly 3:00 AM IST every day
- Clears `access_token` field for all users in the database
- Users are prompted to re-authenticate on next login
- All scheduled tasks are logged for monitoring

## Project Structure

```
scanner/
├── main.py                 # FastAPI application with all routes
├── database.py            # SQLAlchemy models and database setup
├── models.py              # Pydantic schemas for validation
├── auth.py                # Authentication utilities (password hashing, JWT)
├── fyers_api.py           # Fyers API integration
├── scanner.py             # EMA calculation and crossover detection logic
├── scheduler.py           # Token cleanup scheduler (runs daily at 3 AM IST)
├── logger.py              # Centralized logging configuration
├── requirements.txt       # Python dependencies
├── templates/             # Jinja2 HTML templates
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── watchlist.html
│   ├── scan.html
│   └── scan_results.html
├── static/                # Static files (CSS, JS)
│   └── style.css
└── logs/                  # Application logs (auto-created)
    └── fyers_scanner.log
```

## Database Schema

- **users**: User credentials and Fyers API credentials
- **watchlists**: User-created watchlists
- **watchlist_symbols**: Symbols in each watchlist
- **scan_results**: Historical scan results

## Symbol Format

Symbols must follow Fyers format: `EXCHANGE:SYMBOL-TYPE`

### Common Examples:

**NSE Stocks:**
- `NSE:SBIN-EQ` - State Bank of India
- `NSE:RELIANCE-EQ` - Reliance Industries
- `NSE:TCS-EQ` - Tata Consultancy Services
- `NSE:INFY-EQ` - Infosys

**Indices:**
- `NSE:NIFTY50-INDEX` - Nifty 50
- `NSE:NIFTYBANK-INDEX` - Nifty Bank
- `BSE:SENSEX-INDEX` - BSE Sensex

## API Endpoints

### Authentication
- `GET /register` - Registration page
- `POST /register` - Create new user
- `GET /login` - Login page
- `POST /login` - Authenticate user
- `GET /logout` - Logout user

### Fyers OAuth
- `GET /fyers/auth` - Initiate Fyers OAuth2 flow
- `GET /fyers/callback` - OAuth2 callback handler

### Dashboard & Watchlists
- `GET /dashboard` - Main dashboard
- `POST /watchlist/create` - Create new watchlist
- `GET /watchlist/{id}` - View watchlist details
- `POST /watchlist/{id}/add-symbol` - Add symbol to watchlist
- `POST /watchlist/{id}/remove-symbol/{symbol_id}` - Remove symbol

### Scanner
- `GET /scan/{watchlist_id}` - Scan configuration page
- `POST /scan/{watchlist_id}/run` - Execute scan with selected timeframe

## Logging

Logs are stored in the `logs/` directory with automatic rotation:
- Max file size: 10 MB
- Backup count: 5 files
- Log level: Configurable via `LOG_LEVEL` environment variable (default: INFO)

## Technologies Used

- **Backend**: FastAPI, Python 3.12+
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: Jinja2 templates, CSS (Supabase-inspired theme)
- **API**: Fyers API v3
- **Authentication**: Passlib (bcrypt), PyJWT, OAuth2
- **Scheduling**: APScheduler (for daily token cleanup)
- **HTTP Client**: httpx
- **Data Analysis**: pandas, numpy

## Security Notes

- Change the `SECRET_KEY` in production
- Never commit your Fyers API credentials to version control
- Access tokens are stored securely in the database
- Passwords are hashed using bcrypt

## Troubleshooting

### "Access token not set" or "Your Fyers session has expired"
- This is expected after 3:00 AM IST when tokens are automatically cleared
- Go to Dashboard and click "Connect Fyers" or "Re-authenticate"
- Complete the OAuth2 flow with your Fyers credentials
- You'll need to do this daily due to Fyers' 24-hour token expiration policy

### "No data available for symbol"
- Ensure the symbol format is correct (`EXCHANGE:SYMBOL-TYPE`)
- Check if the symbol is active during market hours
- Verify your Fyers subscription includes historical data access

### "Not enough data points"
- Some symbols may not have sufficient historical data
- Try a different timeframe or check if the symbol is newly listed

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

This project is for educational purposes as part of AI Bootcamp 2025.

## Support

For issues or questions, please refer to:
- Fyers API Documentation: https://myapi.fyers.in/docsv3
- FastAPI Documentation: https://fastapi.tiangolo.com/
