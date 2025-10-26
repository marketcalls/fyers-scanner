from fastapi import FastAPI, Request, Depends, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
from typing import Optional
import os

from database import get_db, create_tables, User
from models import PlaceOrderRequest
from auth import hash_password, verify_password
from fyers_api import FyersAPI

# Create FastAPI app
app = FastAPI(title="Fyers Trading Dashboard")

# Add session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
)

# Setup templates
templates = Jinja2Templates(directory="templates")

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()


# Dependency to get current user from session
def get_current_user(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    """Get current user from session"""
    user_id = request.session.get("user_id")
    if user_id:
        return db.query(User).filter(User.id == user_id).first()
    return None


# Routes
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

    return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)


@app.get("/logout")
async def logout(request: Request):
    """Handle user logout"""
    request.session.clear()
    return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    user: User = Depends(get_current_user)
):
    """Display dashboard page"""
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    # Check for flash messages
    auth_success = request.session.pop("auth_success", None)
    auth_error = request.session.pop("auth_error", None)

    order_response = None
    if auth_success:
        order_response = {
            "s": "ok",
            "code": 200,
            "message": auth_success,
            "id": None
        }
    elif auth_error:
        order_response = {
            "s": "error",
            "code": 400,
            "message": auth_error,
            "id": None
        }

    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "user": user, "order_response": order_response}
    )


@app.post("/place-order")
async def place_order(
    request: Request,
    symbol: str = Form(...),
    qty: int = Form(...),
    type: int = Form(...),
    side: int = Form(...),
    productType: str = Form(...),
    limitPrice: float = Form(0),
    stopPrice: float = Form(0),
    validity: str = Form("DAY"),
    disclosedQty: int = Form(0),
    offlineOrder: bool = Form(False),
    stopLoss: float = Form(0),
    takeProfit: float = Form(0),
    orderTag: str = Form(""),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Handle place order request"""
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    # Check if user has access token
    if not user.access_token:
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "user": user,
                "order_response": {
                    "s": "error",
                    "code": 400,
                    "message": "Access token not set. Please update your access token first.",
                    "id": None
                }
            }
        )

    # Create order request
    order_request = PlaceOrderRequest(
        symbol=symbol,
        qty=qty,
        type=type,
        side=side,
        productType=productType,
        limitPrice=limitPrice,
        stopPrice=stopPrice,
        validity=validity,
        disclosedQty=disclosedQty,
        offlineOrder=offlineOrder,
        stopLoss=stopLoss,
        takeProfit=takeProfit,
        orderTag=orderTag
    )

    # Initialize Fyers API client
    fyers_client = FyersAPI(app_id=user.fyers_app_id, access_token=user.access_token)

    # Place order
    response = await fyers_client.place_order(order_request)

    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "user": user, "order_response": response}
    )


@app.post("/update-token")
async def update_token(
    request: Request,
    access_token: str = Form(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user's access token"""
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    # Update access token
    user.access_token = access_token
    db.commit()

    return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)


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
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "user": user,
                "order_response": {
                    "s": "error",
                    "code": 400,
                    "message": "Invalid state parameter. Authentication failed.",
                    "id": None
                }
            }
        )

    # Check if authorization code is present
    if not auth_code:
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "user": user,
                "order_response": {
                    "s": "error",
                    "code": 400,
                    "message": "No authorization code received from Fyers.",
                    "id": None
                }
            }
        )

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
        request.session["auth_success"] = "Successfully authenticated with Fyers! You can now place orders."

        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    else:
        error_msg = token_response.get("message", "Failed to get access token from Fyers")

        # Store error message in session
        request.session["auth_error"] = f"Authentication failed: {error_msg}"

        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
