"""
Main trading bot application.

This module provides the main TradingBot class that orchestrates all components.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

from .brokers.paper_trading import PaperTradingBroker
from .data_sources.yahoo_finance import YahooFinanceDataSource
from .ai_providers.openai_provider import OpenAIProvider
from .models.price_predictor import PricePredictor
from .strategies.daily_trend_strategy import DailyTrendStrategy
from .utils.config import Config
from .utils.logger import setup_logger


class TradingBot:
    """
    Main trading bot that coordinates all components.
    
    This class brings together brokers, data sources, AI providers,
    prediction models, and trading strategies to execute automated trading.
    """

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the trading bot.
        
        Args:
            config: Configuration object (uses defaults if not provided)
        """
        self.config = config or Config()
        self.logger = setup_logger()
        
        # Initialize components
        self.broker = None
        self.data_source = None
        self.ai_provider = None
        self.price_predictor = None
        self.strategy = None
        
        self._initialize_components()

    def _initialize_components(self) -> None:
        """Initialize all bot components based on configuration."""
        self.logger.info("Initializing trading bot components...")
        
        # Initialize broker
        broker_config = self.config.get_broker_config()
        broker_type = broker_config.get('type', 'paper_trading')
        
        if broker_type == 'paper_trading':
            self.broker = PaperTradingBroker(broker_config)
            self.logger.info("Initialized Paper Trading broker")
        else:
            raise ValueError(f"Unsupported broker type: {broker_type}")
        
        # Initialize data source
        data_source_config = self.config.get_data_source_config()
        data_source_type = data_source_config.get('type', 'yahoo_finance')
        
        if data_source_type == 'yahoo_finance':
            self.data_source = YahooFinanceDataSource(data_source_config)
            self.logger.info("Initialized Yahoo Finance data source")
        else:
            raise ValueError(f"Unsupported data source type: {data_source_type}")
        
        # Initialize AI provider (optional)
        ai_config = self.config.get_ai_provider_config()
        if ai_config.get('api_key'):
            try:
                self.ai_provider = OpenAIProvider(ai_config)
                self.logger.info("Initialized OpenAI provider")
            except Exception as e:
                self.logger.warning(f"Could not initialize AI provider: {e}")
        
        # Initialize price predictor
        model_config = self.config.get_model_config()
        self.price_predictor = PricePredictor(model_config)
        self.logger.info("Initialized price predictor")
        
        # Initialize strategy
        strategy_config = self.config.get_strategy_config()
        self.strategy = DailyTrendStrategy(
            data_source=self.data_source,
            ai_provider=self.ai_provider,
            price_predictor=self.price_predictor,
            config=strategy_config
        )
        self.logger.info("Initialized daily trend strategy")

    def connect(self) -> bool:
        """
        Connect to broker.
        
        Returns:
            True if connection successful
        """
        success = self.broker.connect()
        if success:
            self.logger.info("Connected to broker")
        else:
            self.logger.error("Failed to connect to broker")
        return success

    def disconnect(self) -> bool:
        """
        Disconnect from broker.
        
        Returns:
            True if disconnection successful
        """
        success = self.broker.disconnect()
        if success:
            self.logger.info("Disconnected from broker")
        return success

    def train_model(self, symbol: str, lookback_days: int = 365) -> Dict:
        """
        Train price prediction model for a symbol.
        
        Args:
            symbol: Stock symbol
            lookback_days: Number of days of historical data to use
            
        Returns:
            Dictionary with training results
        """
        self.logger.info(f"Training model for {symbol}...")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days)
        
        historical_data = self.data_source.get_historical_data(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date
        )
        
        results = self.price_predictor.train(historical_data)
        
        self.logger.info(f"Model training complete: R² = {results['val_r2']:.4f}, RMSE = {results['val_rmse']:.2f}")
        
        return results

    def analyze_symbol(self, symbol: str) -> Dict:
        """
        Analyze a symbol and generate trading signal.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with analysis and trading signal
        """
        self.logger.info(f"Analyzing {symbol}...")
        
        signal = self.strategy.generate_trading_signal(symbol)
        
        self.logger.info(
            f"{symbol}: {signal['action'].upper()} "
            f"(confidence: {signal['confidence']:.2f})"
        )
        
        return signal

    def execute_signal(
        self,
        signal: Dict,
        quantity: Optional[int] = None
    ) -> Optional[Dict]:
        """
        Execute a trading signal.
        
        Args:
            signal: Trading signal from strategy
            quantity: Number of shares (uses default if not provided)
            
        Returns:
            Order details or None if no action taken
        """
        action = signal['action']
        symbol = signal['symbol']
        current_price = signal['current_price']
        
        if action == 'hold':
            self.logger.info(f"Holding {symbol} - no action taken")
            return None
        
        # Determine quantity
        if quantity is None:
            quantity = self.config.get('trading.default_quantity', 10)
        
        # Place order
        try:
            if action == 'buy':
                order = self.broker.place_order(
                    symbol=symbol,
                    quantity=quantity,
                    order_type='market',
                    side='buy',
                    price=current_price
                )
            elif action == 'sell':
                order = self.broker.place_order(
                    symbol=symbol,
                    quantity=quantity,
                    order_type='market',
                    side='sell',
                    price=current_price
                )
            else:
                return None

            if not order or order.get('status') == 'rejected':
                self.logger.warning(
                    f"{action.upper()} order rejected for {symbol}: {order.get('reason', 'unknown reason')}"
                )
                return None

            self.logger.info(f"{action.upper()} order placed: {symbol} x{quantity} @ ${current_price:.2f}")
            return order
            
        except Exception as e:
            self.logger.error(f"Error placing order: {e}")
            return None

    def run_analysis(self, symbols: List[str]) -> List[Dict]:
        """
        Run analysis on multiple symbols.
        
        Args:
            symbols: List of stock symbols
            
        Returns:
            List of trading signals
        """
        signals = []
        
        for symbol in symbols:
            try:
                signal = self.analyze_symbol(symbol)
                signals.append(signal)
            except Exception as e:
                self.logger.error(f"Error analyzing {symbol}: {e}")
        
        return signals

    def run_trading_session(
        self,
        symbols: List[str],
        execute_trades: bool = False
    ) -> Dict:
        """
        Run a complete trading session.
        
        Args:
            symbols: List of stock symbols to analyze
            execute_trades: Whether to execute trades or just analyze
            
        Returns:
            Dictionary with session results
        """
        self.logger.info(f"Starting trading session with {len(symbols)} symbols...")
        
        session_results = {
            'timestamp': datetime.now().isoformat(),
            'symbols_analyzed': len(symbols),
            'signals': [],
            'orders': [],
            'portfolio': None
        }
        
        # Analyze all symbols
        signals = self.run_analysis(symbols)
        session_results['signals'] = signals
        
        # Execute trades if enabled
        if execute_trades:
            for signal in signals:
                if signal['action'] != 'hold':
                    order = self.execute_signal(signal)
                    if order:
                        session_results['orders'].append(order)
        
        # Get portfolio status
        session_results['portfolio'] = {
            'balance': self.broker.get_account_balance(),
            'positions': self.broker.get_positions()
        }
        
        self.logger.info(
            f"Session complete: {len(session_results['orders'])} orders, "
            f"Balance: ${session_results['portfolio']['balance']:.2f}"
        )
        
        return session_results

    def get_portfolio_status(self) -> Dict:
        """
        Get current portfolio status.
        
        Returns:
            Dictionary with portfolio information
        """
        balance = self.broker.get_account_balance()
        positions = self.broker.get_positions()
        
        # Calculate portfolio value
        total_position_value = 0
        for position in positions:
            try:
                current_price = self.data_source.get_current_price(position['symbol'])
                position['current_price'] = current_price
                position['current_value'] = current_price * position['quantity']
                position['profit_loss'] = position['current_value'] - position['total_cost']
                position['profit_loss_pct'] = (position['profit_loss'] / position['total_cost']) * 100
                total_position_value += position['current_value']
            except Exception as e:
                self.logger.error(f"Error getting price for {position['symbol']}: {e}")
        
        total_value = balance + total_position_value
        
        return {
            'cash_balance': balance,
            'position_value': total_position_value,
            'total_value': total_value,
            'positions': positions,
            'timestamp': datetime.now().isoformat()
        }
