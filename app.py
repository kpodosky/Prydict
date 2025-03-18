import logging
import pandas as pd
import numpy as np
import requests
from flask import Flask, render_template, request, flash
from flask_wtf.csrf import CSRFProtect
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
csrf = CSRFProtect(app)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class FeePredictor:
    def __init__(self):
        self.data = pd.DataFrame()
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.features = ['hour', 'day_of_week', 'day_of_month', 'month', 'rolling_avg_24h']

    def fetch_historical_data(self, days=30):
        """Fetch historical Bitcoin fee data"""
        try:
            url = f"https://api.blockchain.info/charts/mempool-size?timespan={days}days&format=json"
            response = requests.get(url)
            if response.status_code != 200:
                logger.error(f"API request failed with status code: {response.status_code}")
                return False
                
            data = response.json()
            if 'values' not in data:
                logger.error("No 'values' in API response")
                return False
                
            self.data = pd.DataFrame(data['values'])
            self.data['x'] = pd.to_datetime(self.data['x'], unit='s')
            self.data.rename(columns={'x': 'timestamp', 'y': 'fee_per_byte'}, inplace=True)
            logger.debug(f"Fetched {len(self.data)} data points")
            return True
        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            return False

    def preprocess_data(self):
        """Preprocess the data with time-based features"""
        if self.data.empty:
            logger.error("No data available for preprocessing")
            raise ValueError("No data available for preprocessing")
        
        try:
            df = self.data.copy()
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            df['day_of_month'] = df['timestamp'].dt.day
            df['month'] = df['timestamp'].dt.month
            df['rolling_avg_24h'] = df['fee_per_byte'].rolling(24, min_periods=1).mean()
            
            self.data = df.dropna()
            logger.debug(f"Preprocessed data shape: {self.data.shape}")
            return True
        except Exception as e:
            logger.error(f"Error in preprocessing: {e}")
            raise

    # ... rest of the FeePredictor class and route handlers remain the same ...

if __name__ == '__main__':
    app.run(debug=True)
