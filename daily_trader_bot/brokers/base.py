"""
Abstract base class for broker implementations.

This module defines the interface that all broker implementations must follow,
enabling the bot to work with different trading platforms.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime


class BaseBroker(ABC):
    """
    Abstract base class for broker implementations.
    
    This class defines the interface for interacting with different trading
    platforms. Implement this class to add support for new brokers.
    """

    def __init__(self, config: Dict):
        """
        Initialize the broker with configuration.
        
        Args:
            config: Dictionary containing broker-specific configuration
        """
        self.config = config
        self.connected = False

    @abstractmethod
    def connect(self) -> bool:
        """
        Establish connection to the broker.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        """
        Disconnect from the broker.
        
        Returns:
            bool: True if disconnection successful, False otherwise
        """
        pass

    @abstractmethod
    def get_account_balance(self) -> float:
        """
        Get current account balance.
        
        Returns:
            float: Current account balance
        """
        pass

    @abstractmethod
    def get_positions(self) -> List[Dict]:
        """
        Get current open positions.
        
        Returns:
            List of dictionaries containing position information
        """
        pass

    @abstractmethod
    def place_order(
        self,
        symbol: str,
        quantity: float,
        order_type: str,
        side: str,
        price: Optional[float] = None
    ) -> Dict:
        """
        Place a trading order.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            quantity: Number of shares
            order_type: Type of order ('market', 'limit', etc.)
            side: Order side ('buy' or 'sell')
            price: Price for limit orders
            
        Returns:
            Dictionary containing order information
        """
        pass

    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an existing order.
        
        Args:
            order_id: ID of the order to cancel
            
        Returns:
            bool: True if cancellation successful, False otherwise
        """
        pass

    @abstractmethod
    def get_order_status(self, order_id: str) -> Dict:
        """
        Get the status of an order.
        
        Args:
            order_id: ID of the order
            
        Returns:
            Dictionary containing order status information
        """
        pass

    @abstractmethod
    def get_order_history(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Get order history for a date range.
        
        Args:
            start_date: Start date for history
            end_date: End date for history
            
        Returns:
            List of dictionaries containing order history
        """
        pass
