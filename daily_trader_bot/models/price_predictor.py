"""
Machine learning price prediction model.

This module provides price prediction capabilities using Random Forest
with technical indicators as features.
"""

from typing import Dict, Optional
import pandas as pd
import numpy as np
from datetime import datetime
import joblib
import os


class PricePredictor:
    """
    Price prediction model using machine learning.
    
    Uses Random Forest regressor with technical indicators as features
    to predict future stock prices.
    """

    def __init__(self, config: Dict):
        """
        Initialize price predictor.
        
        Args:
            config: Configuration dictionary with model parameters
        """
        self.config = config
        self.model = None
        self.feature_names = []
        self.is_trained = False
        self.scaler = None
        
        # Model parameters
        self.n_estimators = config.get('n_estimators', 100)
        self.max_depth = config.get('max_depth', 10)
        self.random_state = config.get('random_state', 42)

    def _engineer_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Create technical indicator features from price data.
        
        Args:
            data: DataFrame with OHLCV columns
            
        Returns:
            DataFrame with engineered features
        """
        df = data.copy()
        
        # Price-based features
        df['returns'] = df['Close'].pct_change()
        df['log_returns'] = np.log(df['Close'] / df['Close'].shift(1))
        
        # Moving averages
        for period in [5, 10, 20, 50]:
            df[f'sma_{period}'] = df['Close'].rolling(window=period).mean()
            df[f'ema_{period}'] = df['Close'].ewm(span=period, adjust=False).mean()
            df[f'price_to_sma_{period}'] = df['Close'] / df[f'sma_{period}']
        
        # Momentum indicators
        df['momentum_5'] = df['Close'] - df['Close'].shift(5)
        df['momentum_10'] = df['Close'] - df['Close'].shift(10)
        df['roc_5'] = ((df['Close'] - df['Close'].shift(5)) / df['Close'].shift(5)) * 100
        
        # Volatility
        df['volatility_10'] = df['returns'].rolling(window=10).std()
        df['volatility_20'] = df['returns'].rolling(window=20).std()
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        df['macd'] = exp1 - exp2
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['macd_diff'] = df['macd'] - df['macd_signal']
        
        # Bollinger Bands
        df['bb_middle'] = df['Close'].rolling(window=20).mean()
        bb_std = df['Close'].rolling(window=20).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
        df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
        df['bb_position'] = (df['Close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        # Volume features
        df['volume_sma_20'] = df['Volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['Volume'] / df['volume_sma_20']
        
        # Price range
        df['high_low_ratio'] = df['High'] / df['Low']
        df['close_open_ratio'] = df['Close'] / df['Open']
        
        return df

    def train(self, data: pd.DataFrame) -> Dict:
        """
        Train the prediction model on historical data.
        
        Args:
            data: DataFrame with OHLCV columns
            
        Returns:
            Dictionary with training results
        """
        try:
            from sklearn.ensemble import RandomForestRegressor
            from sklearn.preprocessing import StandardScaler
            from sklearn.model_selection import train_test_split
        except ImportError:
            raise ImportError("scikit-learn is required for price prediction. Install dependencies with: pip install -r requirements.txt")
        
        # Engineer features
        df = self._engineer_features(data)
        
        # Create target (next day's close price)
        df['target'] = df['Close'].shift(-1)
        
        # Drop NaN values
        df = df.dropna()
        
        if len(df) < 50:
            raise ValueError("Insufficient data for training (need at least 50 samples)")
        
        # Select features
        feature_columns = [col for col in df.columns 
                          if col not in ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'target']]
        
        X = df[feature_columns].values
        y = df['target'].values
        
        self.feature_names = feature_columns
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=self.random_state, shuffle=False
        )
        
        # Scale features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model = RandomForestRegressor(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            random_state=self.random_state,
            n_jobs=-1
        )
        
        self.model.fit(X_train_scaled, y_train)
        self.is_trained = True
        
        # Evaluate
        train_score = self.model.score(X_train_scaled, y_train)
        test_score = self.model.score(X_test_scaled, y_test)
        
        # Calculate RMSE
        train_pred = self.model.predict(X_train_scaled)
        test_pred = self.model.predict(X_test_scaled)
        
        train_rmse = np.sqrt(np.mean((train_pred - y_train) ** 2))
        test_rmse = np.sqrt(np.mean((test_pred - y_test) ** 2))
        
        return {
            'train_r2': train_score,
            'val_r2': test_score,
            'train_rmse': train_rmse,
            'val_rmse': test_rmse,
            'n_features': len(feature_columns),
            'n_samples': len(df)
        }

    def predict(self, data: pd.DataFrame) -> Dict:
        """
        Predict future price for the given data.
        
        Args:
            data: DataFrame with OHLCV columns
            
        Returns:
            Dictionary with prediction results
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        # Engineer features
        df = self._engineer_features(data)
        
        # Get latest row
        latest = df.iloc[-1:][self.feature_names].values
        
        # Scale features
        latest_scaled = self.scaler.transform(latest)
        
        # Predict
        predicted_price = self.model.predict(latest_scaled)[0]
        current_price = data['Close'].iloc[-1]
        
        # Calculate prediction metrics
        predicted_change = predicted_price - current_price
        predicted_change_pct = (predicted_change / current_price) * 100
        
        return {
            'predicted_price': float(predicted_price),
            'current_price': float(current_price),
            'predicted_change': float(predicted_change),
            'predicted_change_pct': float(predicted_change_pct),
            'timestamp': datetime.now().isoformat()
        }

    def get_feature_importance(self) -> Dict[str, float]:
        """
        Get feature importance scores.
        
        Returns:
            Dictionary mapping feature names to importance scores
        """
        if not self.is_trained:
            return {}
        
        importances = self.model.feature_importances_
        return dict(zip(self.feature_names, importances))

    def save(self, filepath: str) -> None:
        """
        Save trained model to disk.
        
        Args:
            filepath: Path to save model
        """
        if not self.is_trained:
            raise ValueError("Cannot save untrained model")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'config': self.config
        }
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump(model_data, filepath)

    def load(self, filepath: str) -> None:
        """
        Load trained model from disk.
        
        Args:
            filepath: Path to saved model
        """
        model_data = joblib.load(filepath)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_names = model_data['feature_names']
        self.config = model_data.get('config', self.config)
        self.is_trained = True
