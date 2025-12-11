"""
Abstract base class for data source implementations.

This module defines the interface that all data source implementations must follow,
enabling the bot to fetch market data from various providers.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd


class BaseDataSource(ABC):
    """
    Abstract base class for data source implementations.
    
    This class defines the interface for fetching market data from different
    providers. Implement this class to add support for new data sources.
    """

    def __init__(self, config: Dict):
        """
        Initialize the data source with configuration.
        
        Args:
            config: Dictionary containing data source-specific configuration
        """
        self.config = config

    @abstractmethod
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
        pass

    @abstractmethod
    def get_current_price(self, symbol: str) -> float:
        """
        Get current price for a symbol.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            
        Returns:
            float: Current price
        """
        pass

    @abstractmethod
    def get_quote(self, symbol: str) -> Dict:
        """
        Get detailed quote information for a symbol.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            
        Returns:
            Dictionary containing quote information (bid, ask, volume, etc.)
        """
        pass

    @abstractmethod
    def search_symbols(self, query: str) -> List[Dict]:
        """
        Search for stock symbols.
        
        Args:
            query: Search query
            
        Returns:
            List of dictionaries containing symbol information
        """
        pass

    @abstractmethod
    def get_company_info(self, symbol: str) -> Dict:
        """
        Get company information for a symbol.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            
        Returns:
            Dictionary containing company information
        """
        pass

    @abstractmethod
    def get_market_status(self) -> Dict:
        """
        Get current market status.
        
        Returns:
            Dictionary containing market status (open/closed, next open time, etc.)
        """
        pass
