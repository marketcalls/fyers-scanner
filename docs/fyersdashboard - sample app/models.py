from pydantic import BaseModel, EmailStr, Field
from typing import Optional
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


class PlaceOrderRequest(BaseModel):
    """Schema for placing an order on Fyers"""
    symbol: str = Field(..., description="Trading symbol, e.g., MCX:SILVERMIC20NOVFUT")
    qty: int = Field(..., gt=0, description="Quantity to trade")
    type: int = Field(..., ge=1, le=4, description="Order type: 1=Limit, 2=Market, 3=Stop(SL-M), 4=Stoplimit(SL-L)")
    side: int = Field(..., description="Order side: 1=Buy, -1=Sell")
    productType: str = Field(..., description="Product type: CNC, INTRADAY, MARGIN, CO, BO, MTF")
    limitPrice: float = Field(default=0, description="Limit price for Limit/Stoplimit orders")
    stopPrice: float = Field(default=0, description="Stop price for Stop/Stoplimit orders")
    validity: str = Field(default="DAY", description="Validity: DAY or IOC")
    disclosedQty: int = Field(default=0, description="Disclosed quantity (equity only)")
    offlineOrder: bool = Field(default=False, description="After Market Order (AMO)")
    stopLoss: float = Field(default=0, description="Stop loss for CO/BO orders")
    takeProfit: float = Field(default=0, description="Take profit for BO orders")
    orderTag: str = Field(default="", description="Optional order tag")


class FyersOrderResponse(BaseModel):
    """Schema for Fyers order response"""
    s: str  # "ok" or "error"
    code: int
    message: str
    id: Optional[str] = None
