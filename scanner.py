import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime
from fyers_api import FyersAPI
from logger import logger


class EMAScanner:
    """
    EMA Crossover Scanner for intraday trading
    Detects ALL 10 EMA and 20 EMA crossovers in the last 5 days
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

    def detect_all_crossovers(
        self,
        candles: List[List],
        ema10: List[float],
        ema20: List[float]
    ) -> List[Dict[str, Any]]:
        """
        Detect ALL EMA crossover events in the historical data

        Args:
            candles: List of candles [timestamp, open, high, low, close, volume]
            ema10: 10-period EMA values
            ema20: 20-period EMA values

        Returns:
            List of crossover events with details
        """
        crossovers = []

        # Start from index 20 (need 20 candles for EMA20 to stabilize)
        for i in range(20, len(candles)):
            # Get current and previous EMA values
            current_ema10 = ema10[i]
            current_ema20 = ema20[i]
            prev_ema10 = ema10[i - 1]
            prev_ema20 = ema20[i - 1]

            crossover_type = None

            # Positive (Bullish) Crossover: EMA10 crosses above EMA20
            if prev_ema10 <= prev_ema20 and current_ema10 > current_ema20:
                crossover_type = "Positive EMA Crossover"

            # Negative (Bearish) Crossover: EMA10 crosses below EMA20
            elif prev_ema10 >= prev_ema20 and current_ema10 < current_ema20:
                crossover_type = "Negative EMA Crossover"

            # If crossover detected, record it
            if crossover_type:
                timestamp = candles[i][0]  # Epoch timestamp
                close_price = candles[i][4]

                crossover_event = {
                    "timestamp": timestamp,
                    "datetime": datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'),
                    "crossover_type": crossover_type,
                    "close": round(close_price, 2),
                    "ema10": round(current_ema10, 2),
                    "ema20": round(current_ema20, 2)
                }

                crossovers.append(crossover_event)
                logger.info(f"{crossover_type} at {crossover_event['datetime']} - Close: {close_price:.2f}, EMA10: {current_ema10:.2f}, EMA20: {current_ema20:.2f}")

        return crossovers

    async def scan_symbol(
        self,
        symbol: str,
        timeframe: str,
        display_name: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Scan a single symbol for ALL EMA crossovers in last 5 days

        Args:
            symbol: Trading symbol (e.g., NSE:SBIN-EQ)
            timeframe: Timeframe in minutes (5, 10, 15)
            display_name: Display name for the symbol

        Returns:
            Dictionary with all crossover events or None if error
        """
        try:
            logger.info(f"Scanning {symbol} on {timeframe}m timeframe for last 5 days")

            # Fetch historical data for last 5 days
            hist_data = await self.fyers_client.get_historical_data(
                symbol=symbol,
                resolution=timeframe
            )

            if hist_data.get("s") != "ok" or not hist_data.get("candles"):
                logger.error(f"Failed to fetch data for {symbol}: {hist_data.get('message', 'No candles')}")
                return None

            candles = hist_data["candles"]

            # Need at least 20 candles for EMA20
            if len(candles) < 20:
                logger.warning(f"Not enough data for {symbol}: {len(candles)} candles")
                return None

            # Extract closing prices
            closing_prices = [candle[4] for candle in candles]

            # Calculate EMAs
            ema10_values = self.calculate_ema(closing_prices, 10)
            ema20_values = self.calculate_ema(closing_prices, 20)

            if not ema10_values or not ema20_values:
                logger.error(f"Failed to calculate EMAs for {symbol}")
                return None

            # Detect ALL crossovers in the historical data
            all_crossovers = self.detect_all_crossovers(candles, ema10_values, ema20_values)

            # Get current (latest) values for reference
            current_price = closing_prices[-1]
            current_ema10 = ema10_values[-1]
            current_ema20 = ema20_values[-1]

            # Determine current signal based on EMA positions
            if current_ema10 > current_ema20:
                current_signal = "Bullish"
            elif current_ema10 < current_ema20:
                current_signal = "Bearish"
            else:
                current_signal = "Neutral"

            result = {
                "symbol": symbol,
                "display_name": display_name or symbol.split(":")[-1],
                "timeframe": f"{timeframe}m",
                "current_price": round(current_price, 2),
                "current_ema10": round(current_ema10, 2),
                "current_ema20": round(current_ema20, 2),
                "current_signal": current_signal,
                "total_crossovers": len(all_crossovers),
                "crossovers": all_crossovers  # List of all crossover events
            }

            logger.info(f"Scan complete for {symbol}: Found {len(all_crossovers)} crossovers in last 5 days")
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
            List of scan results with all crossover events
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

        total_crossovers = sum(r['total_crossovers'] for r in results)
        logger.info(f"Watchlist scan complete: {len(results)} symbols scanned, {total_crossovers} total crossovers found")
        return results
