"""
Configuration management for the trading bot.

This module handles loading and validating configuration from files or environment.
"""

import os
import json
from typing import Dict, Any, Optional


class Config:
    """
    Configuration manager for the trading bot.
    
    Loads configuration from JSON files or environment variables.
    """

    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_file: Path to JSON configuration file
        """
        self.config = {}
        
        if config_file and os.path.exists(config_file):
            self.load_from_file(config_file)
        else:
            self.load_defaults()

    def load_from_file(self, filepath: str) -> None:
        """
        Load configuration from JSON file.
        
        Args:
            filepath: Path to configuration file
        """
        with open(filepath, 'r') as f:
            self.config = json.load(f)

    def load_defaults(self) -> None:
        """Load default configuration."""
        self.config = {
            'broker': {
                'type': 'paper_trading',
                'initial_balance': 100000.0
            },
            'data_source': {
                'type': 'yahoo_finance'
            },
            'ai_provider': {
                'type': 'openai',
                'api_key': os.environ.get('OPENAI_API_KEY', ''),
                'model': 'gpt-3.5-turbo'
            },
            'strategy': {
                'trend_period': 20,
                'volume_threshold': 1.5,
                'min_confidence': 0.6,
                'stop_loss_pct': 0.05,
                'take_profit_pct': 0.10
            },
            'model': {
                'n_estimators': 100,
                'max_depth': 10
            },
            'trading': {
                'max_position_size': 0.1,  # Max 10% of portfolio per position
                'max_positions': 5,
                'default_quantity': 10
            }
        }

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Configuration key (supports dot notation, e.g., 'broker.type')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value

    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value.
        
        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value

    def save_to_file(self, filepath: str) -> None:
        """
        Save configuration to JSON file.
        
        Args:
            filepath: Path to save configuration
        """
        with open(filepath, 'w') as f:
            json.dump(self.config, f, indent=2)

    def validate(self) -> bool:
        """
        Validate configuration.
        
        Returns:
            True if valid, False otherwise
        """
        required_keys = [
            'broker.type',
            'data_source.type',
            'strategy.trend_period'
        ]
        
        for key in required_keys:
            if self.get(key) is None:
                return False
        
        return True

    def get_broker_config(self) -> Dict:
        """Get broker configuration."""
        return self.get('broker', {})

    def get_data_source_config(self) -> Dict:
        """Get data source configuration."""
        return self.get('data_source', {})

    def get_ai_provider_config(self) -> Dict:
        """Get AI provider configuration."""
        return self.get('ai_provider', {})

    def get_strategy_config(self) -> Dict:
        """Get strategy configuration."""
        return self.get('strategy', {})

    def get_model_config(self) -> Dict:
        """Get model configuration."""
        return self.get('model', {})

    def get_trading_config(self) -> Dict:
        """Get trading configuration."""
        return self.get('trading', {})
