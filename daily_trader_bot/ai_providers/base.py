"""
Abstract base class for AI provider implementations.

This module defines the interface that all AI provider implementations must follow,
enabling the bot to use different AI services for market analysis.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import pandas as pd


class BaseAIProvider(ABC):
    """
    Abstract base class for AI provider implementations.
    
    This class defines the interface for interacting with different AI services
    for market analysis and predictions. Implement this class to add support
    for new AI providers.
    """

    def __init__(self, config: Dict):
        """
        Initialize the AI provider with configuration.
        
        Args:
            config: Dictionary containing AI provider-specific configuration
        """
        self.config = config

    @abstractmethod
    def analyze_sentiment(self, text: str) -> Dict:
        """
        Analyze sentiment of text (news, social media, etc.).
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary containing sentiment analysis (score, label, confidence)
        """
        pass

    @abstractmethod
    def analyze_market_data(
        self,
        historical_data: pd.DataFrame,
        additional_context: Optional[str] = None
    ) -> Dict:
        """
        Analyze market data and provide insights.
        
        Args:
            historical_data: DataFrame with historical price data
            additional_context: Optional additional context for analysis
            
        Returns:
            Dictionary containing analysis results and recommendations
        """
        pass

    @abstractmethod
    def generate_trading_signal(
        self,
        symbol: str,
        historical_data: pd.DataFrame,
        technical_indicators: Dict,
        news_sentiment: Optional[Dict] = None
    ) -> Dict:
        """
        Generate trading signal based on multiple factors.
        
        Args:
            symbol: Stock symbol
            historical_data: DataFrame with historical price data
            technical_indicators: Dictionary of technical indicators
            news_sentiment: Optional news sentiment analysis
            
        Returns:
            Dictionary containing trading signal (action, confidence, reasoning)
        """
        pass

    @abstractmethod
    def explain_prediction(
        self,
        symbol: str,
        prediction: float,
        current_price: float,
        features: Dict
    ) -> str:
        """
        Generate human-readable explanation for a price prediction.
        
        Args:
            symbol: Stock symbol
            prediction: Predicted price
            current_price: Current price
            features: Dictionary of features used in prediction
            
        Returns:
            String containing explanation
        """
        pass

    @abstractmethod
    def summarize_market_trends(self, symbols: List[str], timeframe: str = "1d") -> str:
        """
        Summarize overall market trends for given symbols.
        
        Args:
            symbols: List of stock symbols
            timeframe: Timeframe for analysis
            
        Returns:
            String containing market trend summary
        """
        pass
