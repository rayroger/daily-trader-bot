"""
Daily trend following strategy implementation.

This module implements a trading strategy that follows daily market trends
using technical indicators, AI analysis, and price predictions.
"""

from typing import Dict, List, Optional, TYPE_CHECKING
import pandas as pd
from datetime import datetime, timedelta

if TYPE_CHECKING:
    from ..data_sources.base import BaseDataSource
    from ..ai_providers.base import BaseAIProvider
    from ..models.price_predictor import PricePredictor


class DailyTrendStrategy:
    """
    Daily trend following strategy.
    
    This strategy analyzes daily trends using:
    - Technical indicators
    - AI-powered sentiment and market analysis
    - Price prediction models
    - Volume and momentum indicators
    """

    def __init__(
        self,
        data_source: Optional['BaseDataSource'],
        ai_provider: Optional['BaseAIProvider'] = None,
        price_predictor: Optional['PricePredictor'] = None,
        config: Optional[Dict] = None
    ):
        """
        Initialize the daily trend strategy.
        
        Args:
            data_source: Data source instance for fetching market data
            ai_provider: Optional AI provider for analysis
            price_predictor: Optional price predictor model
            config: Strategy configuration
        """
        self.data_source = data_source
        self.ai_provider = ai_provider
        self.price_predictor = price_predictor
        self.config = config or {}
        
        # Strategy parameters
        self.trend_period = self.config.get('trend_period', 20)
        self.volume_threshold = self.config.get('volume_threshold', 1.5)
        self.min_confidence = self.config.get('min_confidence', 0.6)
        self.stop_loss_pct = self.config.get('stop_loss_pct', 0.05)
        self.take_profit_pct = self.config.get('take_profit_pct', 0.10)

    def calculate_technical_indicators(self, data: pd.DataFrame) -> Dict:
        """
        Calculate technical indicators.
        
        Args:
            data: DataFrame with historical price data
            
        Returns:
            Dictionary of technical indicators
        """
        df = data.copy()
        
        # Moving averages
        sma_short = df['Close'].rolling(window=10).mean().iloc[-1]
        sma_long = df['Close'].rolling(window=self.trend_period).mean().iloc[-1]
        ema_short = df['Close'].ewm(span=10, adjust=False).mean().iloc[-1]
        
        # Momentum
        current_price = df['Close'].iloc[-1]
        prev_price = df['Close'].iloc[-self.trend_period] if len(df) >= self.trend_period else df['Close'].iloc[0]
        momentum = ((current_price - prev_price) / prev_price) * 100
        
        # Volume analysis
        avg_volume = df['Volume'].rolling(window=20).mean().iloc[-1]
        current_volume = df['Volume'].iloc[-1]
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
        
        # Volatility
        returns = df['Close'].pct_change()
        volatility = returns.std() * 100
        
        # RSI (Relative Strength Index)
        rsi = self._calculate_rsi(df['Close'])
        
        # MACD
        macd, signal = self._calculate_macd(df['Close'])
        
        # Bollinger Bands
        bb_upper, bb_middle, bb_lower = self._calculate_bollinger_bands(df['Close'])
        
        # Trend strength
        trend_strength = abs(momentum) / volatility if volatility > 0 else 0
        
        return {
            'sma_short': float(sma_short),
            'sma_long': float(sma_long),
            'ema_short': float(ema_short),
            'current_price': float(current_price),
            'momentum': float(momentum),
            'volume_ratio': float(volume_ratio),
            'volatility': float(volatility),
            'rsi': float(rsi),
            'macd': float(macd),
            'macd_signal': float(signal),
            'bb_upper': float(bb_upper),
            'bb_middle': float(bb_middle),
            'bb_lower': float(bb_lower),
            'trend_strength': float(trend_strength)
        }

    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """Calculate Relative Strength Index."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1] if not rsi.empty else 50.0

    def _calculate_macd(self, prices: pd.Series) -> tuple:
        """Calculate MACD and signal line."""
        ema_12 = prices.ewm(span=12, adjust=False).mean()
        ema_26 = prices.ewm(span=26, adjust=False).mean()
        macd = ema_12 - ema_26
        signal = macd.ewm(span=9, adjust=False).mean()
        
        return macd.iloc[-1], signal.iloc[-1]

    def _calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, std_dev: int = 2) -> tuple:
        """Calculate Bollinger Bands."""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)
        
        return upper.iloc[-1], sma.iloc[-1], lower.iloc[-1]

    def analyze_trend(self, symbol: str, lookback_days: int = 60) -> Dict:
        """
        Analyze the trend for a symbol.
        
        Args:
            symbol: Stock symbol
            lookback_days: Number of days to look back
            
        Returns:
            Dictionary with trend analysis
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days)
        
        # Fetch historical data
        historical_data = self.data_source.get_historical_data(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date
        )
        
        # Calculate technical indicators
        indicators = self.calculate_technical_indicators(historical_data)
        
        # Determine trend direction
        trend_direction = self._determine_trend_direction(indicators)
        
        # Calculate trend strength
        trend_strength = indicators['trend_strength']
        
        # Use AI for analysis if available
        ai_analysis = None
        if self.ai_provider:
            try:
                ai_analysis = self.ai_provider.analyze_market_data(
                    historical_data=historical_data,
                    additional_context=f"Symbol: {symbol}, Trend Direction: {trend_direction}"
                )
            except Exception as e:
                ai_analysis = {"error": str(e)}
        
        # Use price predictor if available
        prediction = None
        if self.price_predictor and self.price_predictor.is_trained:
            try:
                prediction = self.price_predictor.predict(historical_data)
            except Exception as e:
                prediction = {"error": str(e)}
        
        return {
            'symbol': symbol,
            'trend_direction': trend_direction,
            'trend_strength': trend_strength,
            'indicators': indicators,
            'ai_analysis': ai_analysis,
            'price_prediction': prediction,
            'timestamp': datetime.now().isoformat()
        }

    def _determine_trend_direction(self, indicators: Dict) -> str:
        """
        Determine trend direction from indicators.
        
        Args:
            indicators: Dictionary of technical indicators
            
        Returns:
            String: 'bullish', 'bearish', or 'neutral'
        """
        bullish_signals = 0
        bearish_signals = 0
        
        # Moving average crossover
        if indicators['sma_short'] > indicators['sma_long']:
            bullish_signals += 1
        else:
            bearish_signals += 1
        
        # RSI
        if indicators['rsi'] < 30:
            bullish_signals += 1  # Oversold
        elif indicators['rsi'] > 70:
            bearish_signals += 1  # Overbought
        
        # MACD
        if indicators['macd'] > indicators['macd_signal']:
            bullish_signals += 1
        else:
            bearish_signals += 1
        
        # Momentum
        if indicators['momentum'] > 0:
            bullish_signals += 1
        else:
            bearish_signals += 1
        
        # Bollinger Bands
        if indicators['current_price'] < indicators['bb_lower']:
            bullish_signals += 1
        elif indicators['current_price'] > indicators['bb_upper']:
            bearish_signals += 1
        
        if bullish_signals > bearish_signals + 1:
            return 'bullish'
        elif bearish_signals > bullish_signals + 1:
            return 'bearish'
        else:
            return 'neutral'

    def generate_trading_signal(self, symbol: str) -> Dict:
        """
        Generate a trading signal for a symbol.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with trading signal and reasoning
        """
        # Analyze trend
        analysis = self.analyze_trend(symbol)
        
        trend_direction = analysis['trend_direction']
        indicators = analysis['indicators']
        
        # Initialize signal
        action = 'hold'
        confidence = 0.5
        reasoning = []
        
        # Check volume
        volume_check = indicators['volume_ratio'] >= self.volume_threshold
        
        # Determine action based on trend and indicators
        if trend_direction == 'bullish':
            if volume_check and indicators['rsi'] < 70:
                action = 'buy'
                confidence = 0.7
                reasoning.append(f"Bullish trend with strong volume (ratio: {indicators['volume_ratio']:.2f})")
                reasoning.append(f"RSI at {indicators['rsi']:.2f} shows room for growth")
        
        elif trend_direction == 'bearish':
            if volume_check and indicators['rsi'] > 30:
                action = 'sell'
                confidence = 0.7
                reasoning.append(f"Bearish trend with strong volume (ratio: {indicators['volume_ratio']:.2f})")
                reasoning.append(f"RSI at {indicators['rsi']:.2f} suggests downward pressure")
        
        # Adjust confidence based on volatility
        if indicators['volatility'] > 5:
            confidence *= 0.8
            reasoning.append(f"High volatility ({indicators['volatility']:.2f}%) reduces confidence")
        
        # Use AI signal if available
        if self.ai_provider and confidence < 0.9:
            try:
                ai_signal = self.ai_provider.generate_trading_signal(
                    symbol=symbol,
                    historical_data=self.data_source.get_historical_data(
                        symbol, 
                        datetime.now() - timedelta(days=30), 
                        datetime.now()
                    ),
                    technical_indicators=indicators
                )
                
                if 'action' in ai_signal:
                    # Combine signals
                    if ai_signal['action'] == action:
                        confidence = min(0.95, confidence + 0.15)
                        reasoning.append(f"AI confirms signal with {ai_signal.get('confidence', 0.5):.2f} confidence")
                    else:
                        reasoning.append(f"AI suggests {ai_signal['action']} instead")
            except Exception as e:
                reasoning.append(f"AI analysis unavailable: {str(e)}")
        
        # Use price prediction if available
        if analysis.get('price_prediction') and 'predicted_price' in analysis['price_prediction']:
            pred = analysis['price_prediction']
            pred_change = pred['predicted_change_pct']
            
            if abs(pred_change) > 2:  # Significant predicted change
                if pred_change > 0 and action == 'buy':
                    confidence = min(0.95, confidence + 0.1)
                    reasoning.append(f"Price model predicts {pred_change:.2f}% increase")
                elif pred_change < 0 and action == 'sell':
                    confidence = min(0.95, confidence + 0.1)
                    reasoning.append(f"Price model predicts {pred_change:.2f}% decrease")
        
        # Apply minimum confidence threshold
        if confidence < self.min_confidence:
            action = 'hold'
            reasoning.append(f"Confidence {confidence:.2f} below threshold {self.min_confidence}")
        
        return {
            'symbol': symbol,
            'action': action,
            'confidence': confidence,
            'reasoning': reasoning,
            'current_price': indicators['current_price'],
            'stop_loss': indicators['current_price'] * (1 - self.stop_loss_pct) if action == 'buy' else None,
            'take_profit': indicators['current_price'] * (1 + self.take_profit_pct) if action == 'buy' else None,
            'analysis': analysis,
            'timestamp': datetime.now().isoformat()
        }
