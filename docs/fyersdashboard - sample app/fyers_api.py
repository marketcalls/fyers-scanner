import httpx
from typing import Dict, Any
from models import PlaceOrderRequest, FyersOrderResponse
from urllib.parse import urlencode
import hashlib


class FyersAPI:
    """
    Fyers API integration class for trading operations
    """

    def __init__(self, app_id: str, access_token: str):
        """
        Initialize Fyers API client

        Args:
            app_id: Fyers App ID (API Key)
            access_token: Fyers Access Token
        """
        self.app_id = app_id
        self.access_token = access_token
        self.base_url = "https://api-t1.fyers.in/api/v3"

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        return {
            "Authorization": f"{self.app_id}:{self.access_token}",
            "Content-Type": "application/json"
        }

    async def place_order(self, order: PlaceOrderRequest) -> Dict[str, Any]:
        """
        Place an order on Fyers

        Args:
            order: PlaceOrderRequest object with order details

        Returns:
            Dictionary containing the response from Fyers API
        """
        url = f"{self.base_url}/orders/sync"

        payload = {
            "symbol": order.symbol,
            "qty": order.qty,
            "type": order.type,
            "side": order.side,
            "productType": order.productType,
            "limitPrice": order.limitPrice,
            "stopPrice": order.stopPrice,
            "validity": order.validity,
            "disclosedQty": order.disclosedQty,
            "offlineOrder": order.offlineOrder,
            "stopLoss": order.stopLoss,
            "takeProfit": order.takeProfit,
        }

        # Add orderTag only if provided
        if order.orderTag:
            payload["orderTag"] = order.orderTag

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self._get_headers(),
                    timeout=30.0
                )
                return response.json()
            except httpx.HTTPError as e:
                return {
                    "s": "error",
                    "code": 500,
                    "message": f"HTTP Error: {str(e)}",
                    "id": None
                }
            except Exception as e:
                return {
                    "s": "error",
                    "code": 500,
                    "message": f"Error: {str(e)}",
                    "id": None
                }

    async def get_profile(self) -> Dict[str, Any]:
        """
        Get user profile from Fyers

        Returns:
            Dictionary containing user profile information
        """
        url = f"{self.base_url}/profile"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    url,
                    headers=self._get_headers(),
                    timeout=30.0
                )
                return response.json()
            except Exception as e:
                return {
                    "s": "error",
                    "message": f"Error fetching profile: {str(e)}"
                }

    @staticmethod
    def get_auth_url(app_id: str, redirect_uri: str, state: str = "sample_state") -> str:
        """
        Generate Fyers OAuth2 authorization URL

        Args:
            app_id: Fyers App ID
            redirect_uri: Redirect URI registered with Fyers
            state: State parameter for CSRF protection

        Returns:
            Authorization URL to redirect user to
        """
        params = {
            "client_id": app_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "state": state
        }
        return f"https://api-t1.fyers.in/api/v3/generate-authcode?{urlencode(params)}"

    @staticmethod
    async def exchange_auth_code(app_id: str, app_secret: str, auth_code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token

        Args:
            app_id: Fyers App ID
            app_secret: Fyers App Secret
            auth_code: Authorization code received from callback

        Returns:
            Dictionary containing access_token or error
        """
        # Generate app_id_hash
        app_id_hash = hashlib.sha256(f"{app_id}:{app_secret}".encode()).hexdigest()

        payload = {
            "grant_type": "authorization_code",
            "appIdHash": app_id_hash,
            "code": auth_code
        }

        url = "https://api-t1.fyers.in/api/v3/validate-authcode"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=30.0
                )
                return response.json()
            except Exception as e:
                return {
                    "s": "error",
                    "message": f"Error exchanging auth code: {str(e)}"
                }
