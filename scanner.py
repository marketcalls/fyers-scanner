import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from fyers_api import FyersAPI
from logger import logger


class EMAScanner:
    """
    EMA Crossover Scanner for intraday trading
    Detects 10 EMA and 20 EMA crossovers
    """

    def __init__(self, fyers_client: FyersAPI):
        """
        Initialize EMA Scanner

        Args:
            fyers_client: FyersAPI instance
        """
        self.fyers_client = fyers_client

    def calculate_ema(self, prices: List[float], period: int) -> List[float]:
        """
        Calculate Exponential Moving Average

        Args:
            prices: List of closing prices
            period: EMA period

        Returns:
            List of EMA values
        """
        if len(prices) < period:
            logger.warning(f"Not enough data points ({len(prices)}) for EMA {period}")
            return []

        df = pd.DataFrame({'close': prices})
        ema = df['close'].ewm(span=period, adjust=False).mean()
        return ema.tolist()

    def detect_crossover(
        self,
        ema10: List[float],
        ema20: List[float],
        lookback: int = 3
    ) -> str:
        """
        Detect EMA crossover signal

        Args:
            ema10: 10-period EMA values
            ema20: 20-period EMA values
            lookback: Number of candles to look back for crossover

        Returns:
            Signal: "BUY", "SELL", or "NEUTRAL"
        """
        if len(ema10) < lookback or len(ema20) < lookback:
            return "NEUTRAL"

        # Get recent values
        recent_ema10 = ema10[-lookback:]
        recent_ema20 = ema20[-lookback:]

        # Current values
        current_ema10 = recent_ema10[-1]
        current_ema20 = recent_ema20[-1]

        # Previous values
        prev_ema10 = recent_ema10[-2]
        prev_ema20 = recent_ema20[-2]

        # Bullish crossover: EMA10 crosses above EMA20
        if prev_ema10 <= prev_ema20 and current_ema10 > current_ema20:
            logger.info(f"BUY signal detected: EMA10 ({current_ema10:.2f}) crossed above EMA20 ({current_ema20:.2f})")
            return "BUY"

        # Bearish crossover: EMA10 crosses below EMA20
        elif prev_ema10 >= prev_ema20 and current_ema10 < current_ema20:
            logger.info(f"SELL signal detected: EMA10 ({current_ema10:.2f}) crossed below EMA20 ({current_ema20:.2f})")
            return "SELL"

        else:
            return "NEUTRAL"

    async def scan_symbol(
        self,
        symbol: str,
        timeframe: str,
        display_name: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Scan a single symbol for EMA crossover

        Args:
            symbol: Trading symbol (e.g., NSE:SBIN-EQ)
            timeframe: Timeframe in minutes (5, 10, 15)
            display_name: Display name for the symbol

        Returns:
            Dictionary with scan results or None if error
        """
        try:
            logger.info(f"Scanning {symbol} on {timeframe}m timeframe")

            # Fetch historical data
            hist_data = await self.fyers_client.get_historical_data(
                symbol=symbol,
                resolution=timeframe
            )

            if hist_data.get("s") != "ok" or not hist_data.get("candles"):
                logger.error(f"Failed to fetch data for {symbol}: {hist_data.get('message', 'No candles')}")
                return None

            # Extract closing prices from candles
            # Candle format: [timestamp, open, high, low, close, volume]
            candles = hist_data["candles"]
            closing_prices = [candle[4] for candle in candles]

            # Need at least 20 candles for EMA20
            if len(closing_prices) < 20:
                logger.warning(f"Not enough data for {symbol}: {len(closing_prices)} candles")
                return None

            # Calculate EMAs
            ema10_values = self.calculate_ema(closing_prices, 10)
            ema20_values = self.calculate_ema(closing_prices, 20)

            if not ema10_values or not ema20_values:
                logger.error(f"Failed to calculate EMAs for {symbol}")
                return None

            # Detect crossover
            signal = self.detect_crossover(ema10_values, ema20_values)

            # Get current values
            current_price = closing_prices[-1]
            current_ema10 = ema10_values[-1]
            current_ema20 = ema20_values[-1]

            result = {
                "symbol": symbol,
                "display_name": display_name or symbol.split(":")[-1],
                "signal": signal,
                "ema10": round(current_ema10, 2),
                "ema20": round(current_ema20, 2),
                "current_price": round(current_price, 2),
                "timeframe": f"{timeframe}m"
            }

            logger.info(f"Scan complete for {symbol}: {signal} (EMA10: {current_ema10:.2f}, EMA20: {current_ema20:.2f})")
            return result

        except Exception as e:
            logger.error(f"Error scanning {symbol}: {str(e)}")
            return None

    async def scan_watchlist(
        self,
        symbols: List[Dict[str, str]],
        timeframe: str
    ) -> List[Dict[str, Any]]:
        """
        Scan multiple symbols from a watchlist

        Args:
            symbols: List of dicts with 'symbol' and 'display_name' keys
            timeframe: Timeframe in minutes (5, 10, 15)

        Returns:
            List of scan results
        """
        results = []

        logger.info(f"Starting watchlist scan: {len(symbols)} symbols on {timeframe}m timeframe")

        for sym_info in symbols:
            symbol = sym_info.get("symbol")
            display_name = sym_info.get("display_name")

            if not symbol:
                continue

            result = await self.scan_symbol(symbol, timeframe, display_name)

            if result:
                results.append(result)

        logger.info(f"Watchlist scan complete: {len(results)} results")
        return results
