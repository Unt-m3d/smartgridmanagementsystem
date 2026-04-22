import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class EnergyPredictor:
    """Machine learning model for energy prediction"""
    
    def __init__(self):
        self.model = RandomForestRegressor(
            n_estimators=50,
            max_depth=15,
            random_state=42,
            n_jobs=-1
        )
        self.scaler = MinMaxScaler()
        self.is_trained = False
    
    def prepare_features(self, data, lookback=24):
        """Create features from time series data"""
        X, y = [], []
        
        for i in range(len(data) - lookback):
            X.append(data[i:i+lookback])
            y.append(data[i+lookback])
        
        return np.array(X), np.array(y)
    
    def train(self, historical_data):
        """Train the model on historical data"""
        try:
            if len(historical_data) < 100:
                logger.warning("Insufficient data for training")
                return False
            
            data = np.array(historical_data).reshape(-1, 1)
            data_scaled = self.scaler.fit_transform(data).flatten()
            
            X, y = self.prepare_features(data_scaled)
            if len(X) == 0:
                logger.warning("No features created")
                return False
            
            self.model.fit(X, y)
            self.is_trained = True
            logger.info("Model trained successfully")
            return True
        except Exception as e:
            logger.error(f"Training error: {str(e)}")
            return False
    
    def predict(self, recent_data, hours_ahead=24):
        """Make predictions for future hours"""
        try:
            if not self.is_trained:
                logger.warning("Model not trained")
                return []
            
            data = np.array(recent_data).reshape(-1, 1)
            data_scaled = self.scaler.transform(data).flatten()
            
            predictions = []
            current_sequence = data_scaled[-24:].copy() if len(data_scaled) >= 24 else data_scaled
            
            for i in range(hours_ahead):
                next_pred = self.model.predict(
                    current_sequence.reshape(1, -1)
                )[0]
                predictions.append(next_pred)
                
                current_sequence = np.append(
                    current_sequence[1:] if len(current_sequence) > 1 else current_sequence,
                    next_pred
                )
            
            predictions = self.scaler.inverse_transform(
                np.array(predictions).reshape(-1, 1)
            ).flatten()
            
            return predictions
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            return []


def predict_energy_usage(historical_data, hours_ahead=24):
    """Predict future energy usage"""
    predictor = EnergyPredictor()
    predictor.train(historical_data)
    
    predictions_values = predictor.predict(historical_data, hours_ahead)
    
    predictions = []
    for i, pred_value in enumerate(predictions_values):
        pred_time = datetime.now() + timedelta(hours=i+1)
        predictions.append({
            'power': max(0, float(pred_value)),
            'timestamp': pred_time,
            'confidence': 0.85
        })
    
    return predictions


def detect_anomalies(data, threshold=2.5):
    """Detect anomalies using statistical methods"""
    try:
        data = np.array(data)
        mean = np.mean(data)
        std = np.std(data)
        
        if std == 0:
            return []
        
        anomalies = np.where(
            np.abs((data - mean) / std) > threshold
        )[0]
        
        return anomalies.tolist()
    except Exception as e:
        logger.error(f"Anomaly detection error: {str(e)}")
        return []