"""
Data persistence module for storing portfolio state and trading history.

This module handles saving and loading portfolio data to/from the repository.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional


class DataStore:
    """
    Handles persistent storage of portfolio and trading data.
    
    Stores data in JSON format in the repository for easy version control
    and tracking of trading history.
    """
    
    def __init__(self, data_dir: str = "trading_data"):
        """
        Initialize data store.
        
        Args:
            data_dir: Directory to store data files (relative to repo root)
        """
        self.data_dir = data_dir
        self.portfolio_file = os.path.join(data_dir, "portfolio_state.json")
        self.history_file = os.path.join(data_dir, "trading_history.json")
        self.analysis_dir = os.path.join(data_dir, "analysis")
        
        # Create directories if they don't exist
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.analysis_dir, exist_ok=True)
    
    def save_portfolio_state(self, state: Dict) -> None:
        """
        Save current portfolio state.
        
        Args:
            state: Dictionary containing portfolio information
        """
        state['last_updated'] = datetime.now().isoformat()
        
        with open(self.portfolio_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def load_portfolio_state(self) -> Optional[Dict]:
        """
        Load portfolio state from disk.
        
        Returns:
            Dictionary with portfolio state or None if file doesn't exist
        """
        if not os.path.exists(self.portfolio_file):
            return None
        
        with open(self.portfolio_file, 'r') as f:
            return json.load(f)
    
    def append_trading_history(self, entry: Dict) -> None:
        """
        Append entry to trading history.
        
        Args:
            entry: Dictionary with trading session information
        """
        entry['timestamp'] = datetime.now().isoformat()
        
        # Load existing history
        history = []
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                history = json.load(f)
        
        # Append new entry
        history.append(entry)
        
        # Save updated history
        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=2)
    
    def get_trading_history(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get trading history.
        
        Args:
            limit: Maximum number of entries to return (most recent first)
            
        Returns:
            List of trading history entries
        """
        if not os.path.exists(self.history_file):
            return []
        
        with open(self.history_file, 'r') as f:
            history = json.load(f)
        
        # Return most recent entries
        if limit:
            return history[-limit:]
        return history
    
    def save_daily_analysis(self, date: str, analysis: Dict) -> None:
        """
        Save daily analysis results.
        
        Args:
            date: Date string (YYYY-MM-DD)
            analysis: Analysis results dictionary
        """
        filename = os.path.join(self.analysis_dir, f"analysis_{date}.json")
        
        with open(filename, 'w') as f:
            json.dump(analysis, f, indent=2)
    
    def get_portfolio_summary(self) -> Dict:
        """
        Get summary statistics from portfolio history.
        
        Returns:
            Dictionary with portfolio statistics
        """
        state = self.load_portfolio_state()
        history = self.get_trading_history()
        
        if not state:
            return {
                'status': 'not_initialized',
                'message': 'No portfolio state found'
            }
        
        # Calculate statistics
        total_trades = sum(len(entry.get('orders', [])) for entry in history)
        
        return {
            'status': 'active',
            'current_balance': state.get('cash_balance', 0),
            'total_value': state.get('total_value', 0),
            'positions': len(state.get('positions', [])),
            'total_trades': total_trades,
            'last_updated': state.get('last_updated'),
            'trading_days': len(history)
        }
    
    def initialize_portfolio(self, initial_balance: float) -> None:
        """
        Initialize a new portfolio with given balance.
        
        Args:
            initial_balance: Starting cash balance
        """
        initial_state = {
            'cash_balance': initial_balance,
            'positions': [],
            'total_value': initial_balance,
            'initial_balance': initial_balance,
            'created_at': datetime.now().isoformat()
        }
        
        self.save_portfolio_state(initial_state)
        
        # Create empty history file
        with open(self.history_file, 'w') as f:
            json.dump([], f)
