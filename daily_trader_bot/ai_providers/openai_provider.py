"""
OpenAI provider implementation for AI-powered market analysis.

This module provides AI capabilities using OpenAI's API for sentiment analysis
and market insights.
"""

from typing import Dict, List, Optional
import pandas as pd
from ..ai_providers.base import BaseAIProvider
import json


class OpenAIProvider(BaseAIProvider):
    """
    OpenAI provider for AI-powered market analysis.
    
    Uses OpenAI's GPT models for sentiment analysis, market analysis,
    and generating trading insights.
    """

    def __init__(self, config: Dict):
        """
        Initialize OpenAI provider.
        
        Args:
            config: Configuration dictionary with 'api_key' and optional 'model'
        """
        super().__init__(config)
        
        try:
            import openai
            self.openai = openai
        except ImportError:
            raise ImportError(
                "openai library is required. Install it with: pip install openai"
            )
        
        self.api_key = config.get("api_key")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        self.model = config.get("model", "gpt-3.5-turbo")
        self.client = self.openai.OpenAI(api_key=self.api_key)

    def _call_api(self, messages: List[Dict], temperature: float = 0.7) -> str:
        """
        Internal method to call OpenAI API.
        
        Args:
            messages: List of message dictionaries
            temperature: Temperature for response generation
            
        Returns:
            String response from the API
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error calling OpenAI API: {str(e)}"

    def analyze_sentiment(self, text: str) -> Dict:
        """
        Analyze sentiment of text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment analysis results
        """
        messages = [
            {
                "role": "system",
                "content": "You are a financial sentiment analyzer. Analyze the sentiment of the given text and return a JSON object with 'score' (between -1 and 1), 'label' (positive/negative/neutral), and 'confidence' (between 0 and 1)."
            },
            {
                "role": "user",
                "content": f"Analyze the sentiment of this text: {text}"
            }
        ]
        
        response = self._call_api(messages, temperature=0.3)
        
        try:
            # Try to parse JSON response
            result = json.loads(response)
            return result
        except (json.JSONDecodeError, ValueError):
            # Fallback if not valid JSON
            if "positive" in response.lower():
                return {"score": 0.5, "label": "positive", "confidence": 0.6}
            elif "negative" in response.lower():
                return {"score": -0.5, "label": "negative", "confidence": 0.6}
            else:
                return {"score": 0.0, "label": "neutral", "confidence": 0.5}

    def analyze_market_data(
        self,
        historical_data: pd.DataFrame,
        additional_context: Optional[str] = None
    ) -> Dict:
        """
        Analyze market data and provide insights.
        
        Args:
            historical_data: DataFrame with historical price data
            additional_context: Optional additional context
            
        Returns:
            Dictionary with analysis results
        """
        # Prepare summary statistics
        latest_close = historical_data['Close'].iloc[-1]
        prev_close = historical_data['Close'].iloc[-2] if len(historical_data) > 1 else latest_close
        change_pct = ((latest_close - prev_close) / prev_close) * 100
        
        avg_volume = historical_data['Volume'].mean()
        latest_volume = historical_data['Volume'].iloc[-1]
        
        summary = f"""
        Latest Close: ${latest_close:.2f}
        Daily Change: {change_pct:.2f}%
        Average Volume: {avg_volume:,.0f}
        Latest Volume: {latest_volume:,.0f}
        52-Week High: ${historical_data['Close'].max():.2f}
        52-Week Low: ${historical_data['Close'].min():.2f}
        """
        
        if additional_context:
            summary += f"\n\nAdditional Context: {additional_context}"
        
        messages = [
            {
                "role": "system",
                "content": "You are a financial analyst. Analyze the market data and provide insights about trends, patterns, and potential trading opportunities."
            },
            {
                "role": "user",
                "content": f"Analyze this market data and provide insights:\n{summary}"
            }
        ]
        
        analysis = self._call_api(messages, temperature=0.7)
        
        return {
            "analysis": analysis,
            "summary_stats": {
                "latest_close": latest_close,
                "change_pct": change_pct,
                "avg_volume": avg_volume,
                "latest_volume": latest_volume
            }
        }

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
            news_sentiment: Optional news sentiment
            
        Returns:
            Dictionary with trading signal
        """
        context = f"Symbol: {symbol}\n"
        context += f"Current Price: ${historical_data['Close'].iloc[-1]:.2f}\n"
        context += f"Technical Indicators: {json.dumps(technical_indicators, indent=2)}\n"
        
        if news_sentiment:
            context += f"News Sentiment: {json.dumps(news_sentiment, indent=2)}\n"
        
        messages = [
            {
                "role": "system",
                "content": "You are a trading signal generator. Based on the provided data, generate a trading signal. Return a JSON object with 'action' (buy/sell/hold), 'confidence' (0-1), and 'reasoning'."
            },
            {
                "role": "user",
                "content": f"Generate a trading signal for:\n{context}"
            }
        ]
        
        response = self._call_api(messages, temperature=0.5)
        
        try:
            result = json.loads(response)
            return result
        except (json.JSONDecodeError, ValueError):
            return {
                "action": "hold",
                "confidence": 0.3,
                "reasoning": "Unable to generate clear signal from data"
            }

    def explain_prediction(
        self,
        symbol: str,
        prediction: float,
        current_price: float,
        features: Dict
    ) -> str:
        """
        Generate explanation for price prediction.
        
        Args:
            symbol: Stock symbol
            prediction: Predicted price
            current_price: Current price
            features: Features used in prediction
            
        Returns:
            String explanation
        """
        change_pct = ((prediction - current_price) / current_price) * 100
        
        context = f"""
        Symbol: {symbol}
        Current Price: ${current_price:.2f}
        Predicted Price: ${prediction:.2f}
        Expected Change: {change_pct:.2f}%
        
        Key Features:
        {json.dumps(features, indent=2)}
        """
        
        messages = [
            {
                "role": "system",
                "content": "You are a financial analyst. Explain the price prediction in clear, understandable terms for a trader."
            },
            {
                "role": "user",
                "content": f"Explain this price prediction:\n{context}"
            }
        ]
        
        return self._call_api(messages, temperature=0.7)

    def summarize_market_trends(self, symbols: List[str], timeframe: str = "1d") -> str:
        """
        Summarize overall market trends.
        
        Args:
            symbols: List of stock symbols
            timeframe: Timeframe for analysis
            
        Returns:
            String summary of market trends
        """
        messages = [
            {
                "role": "system",
                "content": "You are a market analyst. Provide a concise summary of market trends for the given symbols."
            },
            {
                "role": "user",
                "content": f"Summarize market trends for these symbols over {timeframe}: {', '.join(symbols)}"
            }
        ]
        
        return self._call_api(messages, temperature=0.7)
