"""
Paper trading broker implementation for testing and simulation.

This broker simulates trading without real money, useful for testing strategies
and learning how the bot works.
"""

from typing import Dict, List, Optional
from datetime import datetime
from ..brokers.base import BaseBroker
import uuid


class PaperTradingBroker(BaseBroker):
    """
    Paper trading broker for simulation and testing.
    
    This broker maintains an in-memory portfolio and simulates order execution
    without connecting to a real broker.
    """

    def __init__(self, config: Dict):
        """
        Initialize paper trading broker.
        
        Args:
            config: Configuration dictionary with initial_balance
        """
        super().__init__(config)
        self.initial_balance = config.get("initial_balance", 100000.0)
        self.balance = self.initial_balance
        self.positions = {}  # symbol -> {quantity, avg_price, total_cost}
        self.orders = {}  # order_id -> order_details
        self.order_history = []

    def connect(self) -> bool:
        """Establish connection (no-op for paper trading)."""
        self.connected = True
        return True

    def disconnect(self) -> bool:
        """Disconnect (no-op for paper trading)."""
        self.connected = False
        return True

    def get_account_balance(self) -> float:
        """Get current account balance."""
        return self.balance

    def get_positions(self) -> List[Dict]:
        """Get current open positions."""
        return [
            {
                "symbol": symbol,
                "quantity": details["quantity"],
                "avg_price": details["avg_price"],
                "total_cost": details["total_cost"],
            }
            for symbol, details in self.positions.items()
        ]

    def place_order(
        self,
        symbol: str,
        quantity: float,
        order_type: str,
        side: str,
        price: Optional[float] = None
    ) -> Dict:
        """
        Place a trading order (simulated).
        
        Args:
            symbol: Stock symbol
            quantity: Number of shares
            order_type: 'market' or 'limit'
            side: 'buy' or 'sell'
            price: Price for limit orders
            
        Returns:
            Dictionary with order details
        """
        if not self.connected:
            raise RuntimeError("Broker not connected")

        order_id = str(uuid.uuid4())
        
        # For market orders, execute immediately (simplified simulation)
        if order_type == "market":
            if price is None:
                raise ValueError("Price required for market order simulation")
            
            total_cost = price * quantity
            
            if side == "buy":
                if total_cost > self.balance:
                    return {
                        "order_id": order_id,
                        "status": "rejected",
                        "reason": "Insufficient funds"
                    }
                
                self.balance -= total_cost
                
                if symbol in self.positions:
                    # Update existing position
                    old_qty = self.positions[symbol]["quantity"]
                    old_cost = self.positions[symbol]["total_cost"]
                    new_qty = old_qty + quantity
                    new_cost = old_cost + total_cost
                    self.positions[symbol] = {
                        "quantity": new_qty,
                        "avg_price": new_cost / new_qty,
                        "total_cost": new_cost
                    }
                else:
                    # New position
                    self.positions[symbol] = {
                        "quantity": quantity,
                        "avg_price": price,
                        "total_cost": total_cost
                    }
                
                order = {
                    "order_id": order_id,
                    "symbol": symbol,
                    "quantity": quantity,
                    "order_type": order_type,
                    "side": side,
                    "price": price,
                    "status": "filled",
                    "timestamp": datetime.now()
                }
                
            elif side == "sell":
                if symbol not in self.positions or self.positions[symbol]["quantity"] < quantity:
                    return {
                        "order_id": order_id,
                        "status": "rejected",
                        "reason": "Insufficient shares"
                    }
                
                self.balance += total_cost
                self.positions[symbol]["quantity"] -= quantity
                self.positions[symbol]["total_cost"] -= (
                    self.positions[symbol]["avg_price"] * quantity
                )
                
                if self.positions[symbol]["quantity"] == 0:
                    del self.positions[symbol]
                
                order = {
                    "order_id": order_id,
                    "symbol": symbol,
                    "quantity": quantity,
                    "order_type": order_type,
                    "side": side,
                    "price": price,
                    "status": "filled",
                    "timestamp": datetime.now()
                }
            else:
                raise ValueError(f"Invalid side: {side}")
            
            self.orders[order_id] = order
            self.order_history.append(order)
            return order
        
        # For limit orders, just record them (simplified)
        order = {
            "order_id": order_id,
            "symbol": symbol,
            "quantity": quantity,
            "order_type": order_type,
            "side": side,
            "price": price,
            "status": "pending",
            "timestamp": datetime.now()
        }
        self.orders[order_id] = order
        return order

    def cancel_order(self, order_id: str) -> bool:
        """Cancel an existing order."""
        if order_id in self.orders:
            if self.orders[order_id]["status"] == "pending":
                self.orders[order_id]["status"] = "cancelled"
                return True
        return False

    def get_order_status(self, order_id: str) -> Dict:
        """Get the status of an order."""
        if order_id in self.orders:
            return self.orders[order_id]
        return {"error": "Order not found"}

    def get_order_history(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get order history for a date range."""
        return [
            order for order in self.order_history
            if start_date <= order["timestamp"] <= end_date
        ]

    def get_portfolio_value(self, current_prices: Dict[str, float]) -> float:
        """
        Calculate total portfolio value.
        
        Args:
            current_prices: Dictionary mapping symbols to current prices
            
        Returns:
            Total portfolio value (cash + positions)
        """
        position_value = sum(
            details["quantity"] * current_prices.get(symbol, details["avg_price"])
            for symbol, details in self.positions.items()
        )
        return self.balance + position_value
    
    def get_state(self) -> Dict:
        """
        Get current broker state for persistence.
        
        Returns:
            Dictionary with broker state
        """
        return {
            'balance': self.balance,
            'initial_balance': self.initial_balance,
            'positions': dict(self.positions),
            'order_history': [
                {
                    'order_id': o['order_id'],
                    'symbol': o['symbol'],
                    'quantity': o['quantity'],
                    'order_type': o['order_type'],
                    'side': o['side'],
                    'price': o['price'],
                    'status': o['status'],
                    'timestamp': o['timestamp'].isoformat() if isinstance(o['timestamp'], datetime) else o['timestamp']
                }
                for o in self.order_history
            ]
        }
    
    def load_state(self, state: Dict) -> None:
        """
        Load broker state from saved data.
        
        Args:
            state: Dictionary with broker state
        """
        self.balance = state.get('balance', self.initial_balance)
        self.initial_balance = state.get('initial_balance', self.initial_balance)
        self.positions = state.get('positions', {})
        
        # Load order history
        self.order_history = []
        for order_data in state.get('order_history', []):
            order = dict(order_data)
            # Convert timestamp string back to datetime if needed
            if isinstance(order['timestamp'], str):
                order['timestamp'] = datetime.fromisoformat(order['timestamp'])
            self.order_history.append(order)
