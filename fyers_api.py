import httpx
from typing import Dict, Any, List, Optional
from urllib.parse import urlencode
import hashlib
from datetime import datetime, timedelta
from logger import logger


class FyersAPI:
    """
    Fyers API integration class for data and trading operations
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
        self.data_url = "https://api-t1.fyers.in/data"

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        return {
            "Authorization": f"{self.app_id}:{self.access_token}",
            "Content-Type": "application/json"
        }

    async def get_historical_data(
        self,
        symbol: str,
        resolution: str,
        date_format: int = 0,
        range_from: Optional[str] = None,
        range_to: Optional[str] = None,
        cont_flag: int = 0,
        oi_flag: int = 0
    ) -> Dict[str, Any]:
        """
        Get historical data for a symbol

        Args:
            symbol: Trading symbol (e.g., NSE:SBIN-EQ)
            resolution: Candle resolution (1, 2, 3, 5, 10, 15, 20, 30, 45, 60, 120, 180, 240, D, 1D)
            date_format: 0 for epoch, 1 for YYYY-MM-DD
            range_from: Start date/epoch
            range_to: End date/epoch
            cont_flag: 1 for continuous data (F&O)
            oi_flag: 1 to include open interest

        Returns:
            Dictionary with historical data
        """
        # Calculate default date range if not provided (last 100 candles worth of data)
        if not range_from or not range_to:
            now = datetime.now()
            # For intraday, get data from 7 days ago to ensure we have enough candles
            range_to = int(now.timestamp())
            range_from = int((now - timedelta(days=7)).timestamp())
            date_format = 0

        url = f"{self.data_url}/history"
        params = {
            "symbol": symbol,
            "resolution": resolution,
            "date_format": date_format,
            "range_from": range_from,
            "range_to": range_to,
            "cont_flag": cont_flag,
        }

        if oi_flag:
            params["oi_flag"] = oi_flag

        async with httpx.AsyncClient() as client:
            try:
                logger.info(f"Fetching historical data for {symbol} with resolution {resolution}")
                response = await client.get(
                    url,
                    params=params,
                    headers=self._get_headers(),
                    timeout=30.0
                )
                data = response.json()

                if data.get("s") == "ok":
                    logger.info(f"Successfully fetched {len(data.get('candles', []))} candles for {symbol}")
                else:
                    logger.error(f"Error fetching historical data for {symbol}: {data}")

                return data
            except httpx.HTTPError as e:
                logger.error(f"HTTP Error fetching historical data for {symbol}: {str(e)}")
                return {
                    "s": "error",
                    "message": f"HTTP Error: {str(e)}"
                }
            except Exception as e:
                logger.error(f"Error fetching historical data for {symbol}: {str(e)}")
                return {
                    "s": "error",
                    "message": f"Error: {str(e)}"
                }

    async def get_quotes(self, symbols: List[str]) -> Dict[str, Any]:
        """
        Get live quotes for symbols

        Args:
            symbols: List of symbols (max 50)

        Returns:
            Dictionary with quote data
        """
        if len(symbols) > 50:
            logger.warning(f"Requested {len(symbols)} symbols, but max is 50. Truncating.")
            symbols = symbols[:50]

        url = f"{self.data_url}/quotes"
        params = {"symbols": ",".join(symbols)}

        async with httpx.AsyncClient() as client:
            try:
                logger.info(f"Fetching quotes for {len(symbols)} symbols")
                response = await client.get(
                    url,
                    params=params,
                    headers=self._get_headers(),
                    timeout=30.0
                )
                data = response.json()

                if data.get("s") == "ok":
                    logger.info(f"Successfully fetched quotes for {len(symbols)} symbols")
                else:
                    logger.error(f"Error fetching quotes: {data}")

                return data
            except httpx.HTTPError as e:
                logger.error(f"HTTP Error fetching quotes: {str(e)}")
                return {
                    "s": "error",
                    "message": f"HTTP Error: {str(e)}"
                }
            except Exception as e:
                logger.error(f"Error fetching quotes: {str(e)}")
                return {
                    "s": "error",
                    "message": f"Error: {str(e)}"
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
                logger.error(f"Error fetching profile: {str(e)}")
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
                logger.info("Exchanging auth code for access token")
                response = await client.post(
                    url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=30.0
                )
                data = response.json()

                if data.get("s") == "ok":
                    logger.info("Successfully obtained access token")
                else:
                    logger.error(f"Error exchanging auth code: {data}")

                return data
            except Exception as e:
                logger.error(f"Error exchanging auth code: {str(e)}")
                return {
                    "s": "error",
                    "message": f"Error exchanging auth code: {str(e)}"
                }
