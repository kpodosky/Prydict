from flask import Flask, render_template, request, flash
from flask_wtf.csrf import CSRFProtect
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from datetime import datetime, timedelta
import requests
import logging

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
            url = f"https://api.blockchain.info/charts/transaction-fees?timespan={days}days&format=json"
            response = requests.get(url)
            data = response.json()
            self.data = pd.DataFrame(data['values'])
            self.data['x'] = pd.to_datetime(self.data['x'], unit='s')
            self.data.rename(columns={'x': 'timestamp', 'y': 'fee_per_byte'}, inplace=True)
            return True
        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            return False

    def preprocess_data(self):
        """Preprocess the data with time-based features"""
        if self.data.empty:
            raise ValueError("No data available for preprocessing")
        
        df = self.data.copy()
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['day_of_month'] = df['timestamp'].dt.day
        df['month'] = df['timestamp'].dt.month
        df['rolling_avg_24h'] = df['fee_per_byte'].rolling(24, min_periods=1).mean()
        self.data = df.dropna()
        logger.debug("Data preprocessing completed")

    def train_model(self):
        """Train the prediction model"""
        if self.data.empty:
            raise ValueError("No data available for training")
            
        X = self.data[self.features]
        y = self.data['fee_per_byte']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
        self.model.fit(X_train, y_train)
        logger.debug("Model training completed")
        return True

    def predict_fees(self, start_time, hours=168, interval=1):
        """Predict fees for future timestamps"""
        predictions = []
        for hour in range(0, hours, interval):
            timestamp = start_time + timedelta(hours=hour)
            features = {
                'hour': timestamp.hour,
                'day_of_week': timestamp.weekday(),
                'day_of_month': timestamp.day,
                'month': timestamp.month,
                'rolling_avg_24h': self.data['fee_per_byte'].iloc[-24:].mean()
            }
            df = pd.DataFrame([features])
            fee = self.model.predict(df)[0]
            predictions.append((timestamp, fee))
        return sorted(predictions, key=lambda x: x[1])[:5]

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            btc_amount = float(request.form['btc_amount'])
            if btc_amount <= 0:
                flash('BTC amount must be positive')
                return render_template('index.html')
                
            tx_size = request.form['tx_size']
            
            predictor = FeePredictor()
            logger.info("Fetching historical data...")
            if not predictor.fetch_historical_data(days=60):
                flash('Failed to fetch historical data')
                return render_template('index.html')
            
            logger.info("Preprocessing data...")
            predictor.preprocess_data()
            
            logger.info("Training model...")
            predictor.train_model()
            
            logger.info("Predicting fees...")
            start_time = datetime.now()
            best_times = predictor.predict_fees(start_time)
            
            size_mapping = {"simple": 250, "average": 500, "complex": 1000}
            tx_size_bytes = size_mapping[tx_size]
            
            results = []
            for time, fee_rate in best_times:
                total_fee_btc = (fee_rate * tx_size_bytes) / 1e8
                fee_percentage = (total_fee_btc / btc_amount) * 100 if btc_amount > 0 else 0
                results.append({
                    'time': time.strftime('%Y-%m-%d %H:%M'),
                    'fee_rate': f"{fee_rate:.1f}",
                    'total_fee': f"{total_fee_btc:.8f}",
                    'fee_percent': f"{fee_percentage:.4f}"
                })
            
            logger.info(f"Generated {len(results)} predictions")
            return render_template('results.html', results=results)
            
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            flash(f"An error occurred: {str(e)}")
            return render_template('index.html')
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
