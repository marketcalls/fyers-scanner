from fastapi import FastAPI, Request, Depends, Form, status, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
from typing import Optional, List
import os
from datetime import datetime

from database import get_db, create_tables, User, Watchlist, WatchlistSymbol, ScanResult
from models import (
    WatchlistCreate, WatchlistResponse, SymbolAdd, SymbolResponse,
    ScanRequest, ScanResultResponse, ScanSummaryResponse
)
from auth import hash_password, verify_password
from fyers_api import FyersAPI
from scanner import EMAScanner
from logger import logger

# Create FastAPI app
app = FastAPI(title="Fyers Intraday Scanner", version="1.0.0")

# Add session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
)

# Setup templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()
    logger.info("Application started - database tables created")


# Dependency to get current user from session
def get_current_user(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    """Get current user from session"""
    user_id = request.session.get("user_id")
    if user_id:
        return db.query(User).filter(User.id == user_id).first()
    return None


# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Redirect to dashboard if logged in, else to login"""
    user_id = request.session.get("user_id")
    if user_id:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Display registration page"""
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
async def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    fyers_app_id: str = Form(...),
    fyers_app_secret: str = Form(...),
    db: Session = Depends(get_db)
):
    """Handle user registration"""
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Username already exists"}
        )

    # Check if email already exists
    existing_email = db.query(User).filter(User.email == email).first()
    if existing_email:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Email already exists"}
        )

    # Create new user
    hashed_password = hash_password(password)
    new_user = User(
        username=username,
        email=email,
        password_hash=hashed_password,
        fyers_app_id=fyers_app_id,
        fyers_app_secret=fyers_app_secret,
        access_token=None
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create a default watchlist for the user
    default_watchlist = Watchlist(
        name="My Watchlist",
        user_id=new_user.id,
        is_default=True
    )
    db.add(default_watchlist)
    db.commit()

    logger.info(f"New user registered: {username}")
    return RedirectResponse(url="/login?registered=true", status_code=status.HTTP_302_FOUND)


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Display login page"""
    success = None
    if request.query_params.get("registered"):
        success = "Registration successful! Please login."

    return templates.TemplateResponse(
        "login.html",
        {"request": request, "success": success}
    )


@app.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Handle user login"""
    # Find user
    user = db.query(User).filter(User.username == username).first()

    # Verify password
    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid username or password"}
        )

    # Set session
    request.session["user_id"] = user.id
    logger.info(f"User logged in: {username}")

    return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)


@app.get("/logout")
async def logout(request: Request):
    """Handle user logout"""
    request.session.clear()
    return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)


# ============================================================================
# FYERS AUTHENTICATION ROUTES
# ============================================================================

@app.get("/fyers/auth")
async def fyers_auth(
    request: Request,
    user: User = Depends(get_current_user)
):
    """Initiate Fyers OAuth2 authentication"""
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    # Store state in session for verification
    import secrets
    state = secrets.token_urlsafe(32)
    request.session["oauth_state"] = state

    # Get authorization URL
    redirect_uri = "http://127.0.0.1:8000/fyers/callback"
    auth_url = FyersAPI.get_auth_url(user.fyers_app_id, redirect_uri, state)

    logger.info(f"Initiating Fyers auth for user: {user.username}")
    return RedirectResponse(url=auth_url, status_code=status.HTTP_302_FOUND)


@app.get("/fyers/callback")
async def fyers_callback(
    request: Request,
    auth_code: str = None,
    state: str = None,
    s: str = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Handle Fyers OAuth2 callback"""
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    # Verify state parameter
    stored_state = request.session.get("oauth_state")
    if not state or state != stored_state:
        request.session["error"] = "Invalid state parameter. Authentication failed."
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)

    # Check if authorization code is present
    if not auth_code:
        request.session["error"] = "No authorization code received from Fyers."
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)

    # Exchange authorization code for access token
    token_response = await FyersAPI.exchange_auth_code(
        user.fyers_app_id,
        user.fyers_app_secret,
        auth_code
    )

    # Check if token exchange was successful
    if token_response.get("s") == "ok" and token_response.get("access_token"):
        # Update user's access token
        user.access_token = token_response["access_token"]
        db.commit()

        # Clear oauth state from session
        request.session.pop("oauth_state", None)

        # Store success message in session
        request.session["success"] = "Successfully authenticated with Fyers!"
        logger.info(f"Fyers auth successful for user: {user.username}")

        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    else:
        error_msg = token_response.get("message", "Failed to get access token from Fyers")
        request.session["error"] = f"Authentication failed: {error_msg}"
        logger.error(f"Fyers auth failed for user {user.username}: {error_msg}")

        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)


# ============================================================================
# DASHBOARD ROUTE
# ============================================================================

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Display dashboard page"""
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    # Get user's watchlists
    watchlists = db.query(Watchlist).filter(Watchlist.user_id == user.id).all()

    # Get flash messages
    success = request.session.pop("success", None)
    error = request.session.pop("error", None)

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": user,
            "watchlists": watchlists,
            "success": success,
            "error": error
        }
    )


# ============================================================================
# WATCHLIST MANAGEMENT ROUTES
# ============================================================================

@app.post("/watchlist/create")
async def create_watchlist(
    request: Request,
    name: str = Form(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new watchlist"""
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    # Check if watchlist with same name exists
    existing = db.query(Watchlist).filter(
        Watchlist.user_id == user.id,
        Watchlist.name == name
    ).first()

    if existing:
        request.session["error"] = f"Watchlist '{name}' already exists"
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)

    # Create new watchlist
    new_watchlist = Watchlist(
        name=name,
        user_id=user.id,
        is_default=False
    )

    db.add(new_watchlist)
    db.commit()

    logger.info(f"Watchlist created: {name} by user {user.username}")
    request.session["success"] = f"Watchlist '{name}' created successfully"
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)


@app.get("/watchlist/{watchlist_id}", response_class=HTMLResponse)
async def view_watchlist(
    request: Request,
    watchlist_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """View watchlist details"""
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    # Get watchlist
    watchlist = db.query(Watchlist).filter(
        Watchlist.id == watchlist_id,
        Watchlist.user_id == user.id
    ).first()

    if not watchlist:
        request.session["error"] = "Watchlist not found"
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)

    # Get flash messages
    success = request.session.pop("success", None)
    error = request.session.pop("error", None)

    return templates.TemplateResponse(
        "watchlist.html",
        {
            "request": request,
            "user": user,
            "watchlist": watchlist,
            "success": success,
            "error": error
        }
    )


@app.post("/watchlist/{watchlist_id}/add-symbol")
async def add_symbol_to_watchlist(
    request: Request,
    watchlist_id: int,
    symbol: str = Form(...),
    display_name: str = Form(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a symbol to watchlist"""
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    # Get watchlist
    watchlist = db.query(Watchlist).filter(
        Watchlist.id == watchlist_id,
        Watchlist.user_id == user.id
    ).first()

    if not watchlist:
        request.session["error"] = "Watchlist not found"
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)

    # Check if symbol already exists in watchlist
    existing = db.query(WatchlistSymbol).filter(
        WatchlistSymbol.watchlist_id == watchlist_id,
        WatchlistSymbol.symbol == symbol
    ).first()

    if existing:
        request.session["error"] = f"Symbol '{symbol}' already exists in this watchlist"
        return RedirectResponse(url=f"/watchlist/{watchlist_id}", status_code=status.HTTP_302_FOUND)

    # Add symbol to watchlist
    new_symbol = WatchlistSymbol(
        watchlist_id=watchlist_id,
        symbol=symbol,
        display_name=display_name or symbol.split(":")[-1]
    )

    db.add(new_symbol)
    db.commit()

    logger.info(f"Symbol {symbol} added to watchlist {watchlist.name} by user {user.username}")
    request.session["success"] = f"Symbol '{symbol}' added successfully"
    return RedirectResponse(url=f"/watchlist/{watchlist_id}", status_code=status.HTTP_302_FOUND)


@app.post("/watchlist/{watchlist_id}/remove-symbol/{symbol_id}")
async def remove_symbol_from_watchlist(
    request: Request,
    watchlist_id: int,
    symbol_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a symbol from watchlist"""
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    # Get watchlist
    watchlist = db.query(Watchlist).filter(
        Watchlist.id == watchlist_id,
        Watchlist.user_id == user.id
    ).first()

    if not watchlist:
        request.session["error"] = "Watchlist not found"
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)

    # Get and delete symbol
    symbol = db.query(WatchlistSymbol).filter(
        WatchlistSymbol.id == symbol_id,
        WatchlistSymbol.watchlist_id == watchlist_id
    ).first()

    if symbol:
        db.delete(symbol)
        db.commit()
        logger.info(f"Symbol {symbol.symbol} removed from watchlist {watchlist.name}")
        request.session["success"] = "Symbol removed successfully"
    else:
        request.session["error"] = "Symbol not found"

    return RedirectResponse(url=f"/watchlist/{watchlist_id}", status_code=status.HTTP_302_FOUND)


# ============================================================================
# SCANNER ROUTES
# ============================================================================

@app.get("/scan/{watchlist_id}", response_class=HTMLResponse)
async def scan_page(
    request: Request,
    watchlist_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Display scan configuration page"""
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    # Get watchlist
    watchlist = db.query(Watchlist).filter(
        Watchlist.id == watchlist_id,
        Watchlist.user_id == user.id
    ).first()

    if not watchlist:
        request.session["error"] = "Watchlist not found"
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse(
        "scan.html",
        {
            "request": request,
            "user": user,
            "watchlist": watchlist
        }
    )


@app.post("/scan/{watchlist_id}/run")
async def run_scan(
    request: Request,
    watchlist_id: int,
    timeframe: str = Form(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Run EMA crossover scan on watchlist"""
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    # Check if user has access token
    if not user.access_token:
        request.session["error"] = "Please authenticate with Fyers first"
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)

    # Validate timeframe
    if timeframe not in ["5", "10", "15"]:
        request.session["error"] = "Invalid timeframe. Choose 5, 10, or 15 minutes"
        return RedirectResponse(url=f"/scan/{watchlist_id}", status_code=status.HTTP_302_FOUND)

    # Get watchlist with symbols
    watchlist = db.query(Watchlist).filter(
        Watchlist.id == watchlist_id,
        Watchlist.user_id == user.id
    ).first()

    if not watchlist:
        request.session["error"] = "Watchlist not found"
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)

    if not watchlist.symbols:
        request.session["error"] = "Watchlist is empty. Please add symbols first."
        return RedirectResponse(url=f"/watchlist/{watchlist_id}", status_code=status.HTTP_302_FOUND)

    # Initialize Fyers API and Scanner
    fyers_client = FyersAPI(app_id=user.fyers_app_id, access_token=user.access_token)
    scanner = EMAScanner(fyers_client)

    # Prepare symbols for scanning
    symbols_to_scan = [
        {"symbol": sym.symbol, "display_name": sym.display_name}
        for sym in watchlist.symbols
    ]

    # Run the scan
    logger.info(f"Starting scan for watchlist {watchlist.name} with {len(symbols_to_scan)} symbols on {timeframe}m")
    scan_results = await scanner.scan_watchlist(symbols_to_scan, timeframe)

    # Flatten all crossover events from all symbols
    all_crossovers = []
    for result in scan_results:
        symbol_name = result["display_name"]
        for crossover in result.get("crossovers", []):
            crossover_event = {
                "datetime": crossover["datetime"],
                "timestamp": crossover["timestamp"],
                "ticker": symbol_name,
                "crossover_type": crossover["crossover_type"],
                "close": crossover["close"],
                "ema10": crossover["ema10"],
                "ema20": crossover["ema20"]
            }
            all_crossovers.append(crossover_event)

    # Sort all crossovers by timestamp (most recent first)
    all_crossovers.sort(key=lambda x: x["timestamp"], reverse=True)

    # Calculate summary statistics
    total_symbols_scanned = len(scan_results)
    total_crossovers = len(all_crossovers)
    positive_crossovers = len([c for c in all_crossovers if c["crossover_type"] == "Positive EMA Crossover"])
    negative_crossovers = len([c for c in all_crossovers if c["crossover_type"] == "Negative EMA Crossover"])

    logger.info(f"Scan complete: {total_symbols_scanned} symbols, {total_crossovers} total crossovers ({positive_crossovers} positive, {negative_crossovers} negative)")

    # Render results page
    return templates.TemplateResponse(
        "scan_results.html",
        {
            "request": request,
            "user": user,
            "watchlist": watchlist,
            "timeframe": timeframe,
            "scan_results": scan_results,
            "all_crossovers": all_crossovers,
            "total_symbols_scanned": total_symbols_scanned,
            "total_crossovers": total_crossovers,
            "positive_crossovers": positive_crossovers,
            "negative_crossovers": negative_crossovers,
            "scan_time": datetime.now()
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
