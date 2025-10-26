# Quick Start Guide

Get your Fyers Trading Dashboard up and running in 5 minutes!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Configure Fyers Developer Portal

1. Go to [Fyers Developer Portal](https://myapi.fyers.in/dashboard)
2. Login with your Fyers credentials
3. Create a new app or select existing app
4. Add this redirect URL: `http://127.0.0.1:8000/fyers/callback`
5. Note down your **App ID** and **App Secret**

## Step 3: Run the Application

```bash
python main.py
```

Or using uvicorn:

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

## Step 4: Access the Application

Open your browser and go to: `http://127.0.0.1:8000`

## Step 5: Register

1. Click on "Register Here"
2. Fill in your details:
   - Username
   - Email
   - Password
   - Fyers App ID (from Step 2)
   - Fyers App Secret (from Step 2)
3. Click "Register"

## Step 6: Login

1. Enter your username and password
2. Click "Login"

## Step 7: Authenticate with Fyers

1. Click the **"Authenticate with Fyers"** button
2. You'll be redirected to Fyers login page
3. Login with your Fyers credentials
4. Authorize the application
5. You'll be redirected back with an active access token

## Step 8: Place Your First Order

1. Fill in the order form:
   - **Symbol**: e.g., `NSE:SBIN-EQ`
   - **Quantity**: e.g., `1`
   - **Order Type**: Select from dropdown (Market, Limit, etc.)
   - **Side**: Buy or Sell
   - **Product Type**: e.g., `INTRADAY`
2. Click "Place Order"

## Common Issues

### "Invalid redirect URI" error
- Make sure you've added `http://127.0.0.1:8000/fyers/callback` exactly in Fyers Developer Portal
- Note: Use `127.0.0.1` not `localhost`

### "Access token not set" error
- Click "Authenticate with Fyers" button to get a valid access token
- Or manually update token using "Update Token" button

### Order placement fails
- Verify your symbol format is correct
- Check market hours
- Ensure you have sufficient balance in your Fyers account

## What's Next?

- Explore different order types (Limit, Stop, etc.)
- Try different product types (CNC, MARGIN, CO, BO)
- Check the `docs/` folder for detailed API documentation

## Need Help?

Refer to the main [README.md](README.md) for detailed documentation.
