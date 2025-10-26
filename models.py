from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class UserRegistration(BaseModel):
    """Schema for user registration"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    fyers_app_id: str = Field(..., min_length=1, description="Fyers API Key (app_id)")
    fyers_app_secret: str = Field(..., min_length=1, description="Fyers API Secret (app_secret)")


class UserLogin(BaseModel):
    """Schema for user login"""
    username: str
    password: str


class UserResponse(BaseModel):
    """Schema for user response"""
    id: int
    username: str
    email: str
    fyers_app_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class WatchlistCreate(BaseModel):
    """Schema for creating a watchlist"""
    name: str = Field(..., min_length=1, max_length=100)
    is_default: bool = False


class WatchlistResponse(BaseModel):
    """Schema for watchlist response"""
    id: int
    name: str
    user_id: int
    is_default: bool
    created_at: datetime
    symbols: List['SymbolResponse'] = []

    class Config:
        from_attributes = True


class SymbolAdd(BaseModel):
    """Schema for adding a symbol to watchlist"""
    symbol: str = Field(..., description="Trading symbol, e.g., NSE:SBIN-EQ")
    display_name: Optional[str] = Field(None, description="Display name, e.g., SBIN")


class SymbolResponse(BaseModel):
    """Schema for symbol response"""
    id: int
    symbol: str
    display_name: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ScanRequest(BaseModel):
    """Schema for scan request"""
    watchlist_id: int = Field(..., description="Watchlist ID to scan")
    timeframe: str = Field(..., description="Timeframe: 5, 10, 15 (minutes)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "watchlist_id": 1,
                "timeframe": "5"
            }
        }
    }


class ScanResultResponse(BaseModel):
    """Schema for scan result response"""
    symbol: str
    display_name: Optional[str]
    signal: str  # BUY, SELL, NEUTRAL
    ema10: float
    ema20: float
    current_price: float
    timeframe: str

    class Config:
        from_attributes = True


class ScanSummaryResponse(BaseModel):
    """Schema for scan summary response"""
    watchlist_name: str
    timeframe: str
    total_symbols: int
    buy_signals: int
    sell_signals: int
    neutral_signals: int
    results: List[ScanResultResponse]
    scan_time: datetime


# Update forward references
WatchlistResponse.model_rebuild()
