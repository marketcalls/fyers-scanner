# Fyers Intraday Scanner

A real-time stock scanner built with Fyers API, FastAPI, SQLAlchemy, Tailwind CSS, and DaisyUI. Detects 10/20 EMA crossover signals for intraday trading.

## Features

- **Multi-user Support**: Secure user authentication and registration
- **Fyers OAuth Integration**: OAuth2 authentication with Fyers API
- **Watchlist Management**: Create and manage multiple watchlists with custom symbols
- **EMA Crossover Scanner**: Detects 10 EMA and 20 EMA crossovers
- **Multiple Timeframes**: Scan on 5-minute, 10-minute, or 15-minute charts
- **Real-time Data**: Fetches historical data from Fyers API
- **Beautiful UI**: Modern, responsive interface using Tailwind CSS and DaisyUI
- **Centralized Logging**: Comprehensive logging with rotation for debugging and monitoring

## Scanner Strategy

The scanner uses the following logic:

- **BUY Signal**: When 10 EMA crosses above 20 EMA (Bullish crossover)
- **SELL Signal**: When 10 EMA crosses below 20 EMA (Bearish crossover)
- **NEUTRAL**: No crossover detected

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd scanner
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables (optional):
```bash
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

## Project Structure

```
scanner/
├── main.py                 # FastAPI application with all routes
├── database.py            # SQLAlchemy models and database setup
├── models.py              # Pydantic schemas for validation
├── auth.py                # Authentication utilities (password hashing, JWT)
├── fyers_api.py           # Fyers API integration
├── scanner.py             # EMA calculation and crossover detection logic
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
- **Frontend**: Jinja2 templates, Tailwind CSS, DaisyUI
- **API**: Fyers API v3
- **Authentication**: Passlib (bcrypt), python-jose (JWT), OAuth2
- **HTTP Client**: httpx
- **Data Analysis**: pandas, numpy

## Security Notes

- Change the `SECRET_KEY` in production
- Never commit your Fyers API credentials to version control
- Access tokens are stored securely in the database
- Passwords are hashed using bcrypt

## Troubleshooting

### "Access token not set"
- Go to Dashboard and click "Authenticate Fyers"
- Complete the OAuth2 flow with your Fyers credentials

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
