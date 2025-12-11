"""
Yahoo Finance data source implementation.

This module provides market data fetching capabilities using Yahoo Finance API.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import pandas as pd
from ..data_sources.base import BaseDataSource


class YahooFinanceDataSource(BaseDataSource):
    """
    Yahoo Finance data source implementation.
    
    Fetches market data from Yahoo Finance using yfinance library.
    """

    def __init__(self, config: Dict):
        """
        Initialize Yahoo Finance data source.
        
        Args:
            config: Configuration dictionary
        """
        super().__init__(config)
        try:
            import yfinance as yf
            self.yf = yf
        except ImportError:
            raise ImportError(
                "yfinance library is required. Install it with: pip install yfinance"
            )

    def get_historical_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        interval: str = "1d"
    ) -> pd.DataFrame:
        """
        Fetch historical price data for a symbol.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            start_date: Start date for historical data
            end_date: End date for historical data
            interval: Data interval ('1d', '1h', '5m', etc.)
            
        Returns:
            DataFrame with columns: Date, Open, High, Low, Close, Volume
        """
        ticker = self.yf.Ticker(symbol)
        df = ticker.history(
            start=start_date,
            end=end_date,
            interval=interval
        )
        
        if df.empty:
            raise ValueError(f"No data available for {symbol}")
        
        # Standardize column names
        df = df.reset_index()
        df.columns = [col.lower().capitalize() for col in df.columns]
        
        return df

    def get_current_price(self, symbol: str) -> float:
        """
        Get current price for a symbol.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            
        Returns:
            float: Current price
        """
        ticker = self.yf.Ticker(symbol)
        data = ticker.history(period="1d")
        
        if data.empty:
            raise ValueError(f"No data available for {symbol}")
        
        return float(data['Close'].iloc[-1])

    def get_quote(self, symbol: str) -> Dict:
        """
        Get detailed quote information for a symbol.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            
        Returns:
            Dictionary containing quote information
        """
        ticker = self.yf.Ticker(symbol)
        info = ticker.info
        
        # Get latest price data
        hist = ticker.history(period="1d")
        
        return {
            "symbol": symbol,
            "current_price": float(hist['Close'].iloc[-1]) if not hist.empty else None,
            "open": float(hist['Open'].iloc[-1]) if not hist.empty else None,
            "high": float(hist['High'].iloc[-1]) if not hist.empty else None,
            "low": float(hist['Low'].iloc[-1]) if not hist.empty else None,
            "volume": int(hist['Volume'].iloc[-1]) if not hist.empty else None,
            "previous_close": info.get("previousClose"),
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
        }

    def search_symbols(self, query: str) -> List[Dict]:
        """
        Search for stock symbols.
        
        Note: Yahoo Finance doesn't provide a direct search API,
        so this is a simplified implementation.
        
        Args:
            query: Search query
            
        Returns:
            List of dictionaries containing symbol information
        """
        # This is a basic implementation
        # In a production system, you'd use a proper search API
        try:
            ticker = self.yf.Ticker(query.upper())
            info = ticker.info
            return [{
                "symbol": query.upper(),
                "name": info.get("longName", "Unknown"),
                "exchange": info.get("exchange", "Unknown"),
            }]
        except:
            return []

    def get_company_info(self, symbol: str) -> Dict:
        """
        Get company information for a symbol.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            
        Returns:
            Dictionary containing company information
        """
        ticker = self.yf.Ticker(symbol)
        info = ticker.info
        
        return {
            "symbol": symbol,
            "name": info.get("longName"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "description": info.get("longBusinessSummary"),
            "website": info.get("website"),
            "employees": info.get("fullTimeEmployees"),
            "market_cap": info.get("marketCap"),
            "country": info.get("country"),
        }

    def get_market_status(self) -> Dict:
        """
        Get current market status.
        
        Returns:
            Dictionary containing market status
        """
        # Use SPY as a proxy for market hours
        spy = self.yf.Ticker("SPY")
        
        try:
            # Try to get today's data
            today_data = spy.history(period="1d", interval="1m")
            
            if not today_data.empty:
                last_update = today_data.index[-1]
                now = datetime.now()
                
                # Market is likely open if we got data in the last hour
                time_diff = now - last_update.to_pydatetime().replace(tzinfo=None)
                is_open = time_diff.total_seconds() < 3600
                
                return {
                    "is_open": is_open,
                    "last_update": last_update.isoformat(),
                    "status": "open" if is_open else "closed",
                }
            else:
                return {
                    "is_open": False,
                    "status": "closed",
                    "last_update": None,
                }
        except:
            return {
                "is_open": False,
                "status": "unknown",
                "last_update": None,
            }
