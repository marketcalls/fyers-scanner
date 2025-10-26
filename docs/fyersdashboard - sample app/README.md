# Fyers Trading Dashboard

A simple web-based trading dashboard for Fyers API built with FastAPI, SQLite, Tailwind CSS, and DaisyUI.

## Features

- User registration and authentication
- Secure storage of Fyers API credentials (App ID, App Secret, Access Token)
- Place orders on Fyers with a user-friendly interface
- Support for all order types (Market, Limit, Stop, Stoplimit)
- Support for multiple product types (INTRADAY, CNC, MARGIN, CO, BO, MTF)
- Responsive design with Tailwind CSS and DaisyUI

## Tech Stack

- **Backend**: Python FastAPI
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: Jinja2 templates with Tailwind CSS and DaisyUI
- **Authentication**: Session-based with password hashing (bcrypt)

## Prerequisites

- Python 3.8 or higher
- Fyers API credentials (App ID and App Secret)
- **Important**: You must register `http://127.0.0.1:8000/fyers/callback` as your redirect URL in the Fyers Developer Portal

## Installation

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file (optional):
```bash
cp .env.example .env
```
Edit `.env` and set your SECRET_KEY (recommended for production)

## Running the Application

Start the FastAPI server:

```bash
python main.py
```

Or use uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The application will be available at: `http://localhost:8000`

## Usage

### 1. Setup Fyers API Redirect URL

Before registering, make sure you have configured your redirect URL in Fyers Developer Portal:
1. Go to Fyers Developer Portal
2. Navigate to your app settings
3. Add `http://127.0.0.1:8000/fyers/callback` as a redirect URL
4. Save the settings

### 2. Register a New Account

1. Navigate to `http://localhost:8000`
2. Click on "Register Here"
3. Fill in:
   - **Personal Information**: Username, Email, Password
   - **Fyers API Credentials**:
     - App ID (API Key) - Get from Fyers Developer Portal
     - App Secret (API Secret) - Get from Fyers Developer Portal
4. Click "Register"

### 3. Login

1. Enter your username and password
2. Click "Login"

### 4. Authenticate with Fyers (OAuth2)

1. On the dashboard, click "Authenticate with Fyers" button
2. You will be redirected to Fyers login page
3. Enter your Fyers credentials and authorize the application
4. You will be redirected back to the dashboard with an active access token

**Note**: The OAuth2 flow automatically obtains and stores your access token securely. You can also manually update the token using the "Update Token" button if needed.

### 5. Place an Order

Fill in the order details:

- **Symbol**: Trading symbol (e.g., `NSE:SBIN-EQ`, `MCX:GOLD20DECFUT`)
- **Quantity**: Number of shares/lots
- **Order Type**: Limit, Market, Stop, or Stoplimit
- **Side**: Buy or Sell
- **Product Type**: INTRADAY, CNC, MARGIN, CO, BO, or MTF
- **Validity**: DAY or IOC
- **Limit Price**: For Limit/Stoplimit orders
- **Stop Price**: For Stop/Stoplimit orders
- **Other fields**: As needed

Click "Place Order" to submit.

## Symbol Format Examples

| Segment | Format | Example |
|---------|--------|---------|
| Equity | `{Ex}:{Symbol}-{Series}` | `NSE:SBIN-EQ` |
| Futures | `{Ex}:{Symbol}{YY}{MMM}FUT` | `NSE:NIFTY20OCTFUT` |
| Options | `{Ex}:{Symbol}{YY}{MMM}{Strike}{CE/PE}` | `NSE:NIFTY20OCT11000CE` |
| Commodity | `{Ex}:{Symbol}{YY}{MMM}FUT` | `MCX:GOLD20DECFUT` |

## Project Structure

```
fyersdashboard/
├── main.py                 # FastAPI application with routes
├── database.py            # Database models and setup
├── models.py              # Pydantic models for validation
├── auth.py                # Authentication logic
├── fyers_api.py           # Fyers API integration
├── requirements.txt       # Python dependencies
├── templates/             # Jinja2 templates
│   ├── base.html         # Base template
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   └── dashboard.html    # Dashboard with place order form
├── static/               # Static files
│   └── css/
├── docs/                 # API documentation
│   ├── authentication.md
│   ├── placeorder.md
│   └── appendix.md
└── fyers_dashboard.db    # SQLite database (created automatically)
```

## Security Notes

1. **Never commit your `.env` file** - It contains sensitive keys
2. **Change the SECRET_KEY** in production
3. **Use HTTPS** in production to protect credentials
4. **Never share your Fyers API credentials** with anyone
5. **Access tokens should be kept secure** and regenerated regularly

## API Documentation

Refer to the `docs/` folder for detailed Fyers API documentation:
- `authentication.md` - Authentication flow
- `placeorder.md` - Place order API details
- `appendix.md` - Symbol formats, codes, and reference tables

## Troubleshooting

### Database errors
If you encounter database errors, delete `fyers_dashboard.db` and restart the application. The database will be recreated automatically.

### Access Token errors
Make sure you have a valid access token. Access tokens expire and need to be regenerated through the Fyers authentication flow.

### Order placement errors
- Check if your symbol format is correct
- Verify your access token is valid
- Ensure you have sufficient balance in your Fyers account
- Check if the market is open for the instrument you're trading

## License

This project is for educational purposes. Use at your own risk. Always test with paper trading before using real money.

## Disclaimer

This is a sample application for demonstration purposes. The developers are not responsible for any financial losses incurred through the use of this application. Always verify orders before placing them and trade responsibly.
