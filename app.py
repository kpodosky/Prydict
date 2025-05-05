import logging
import pandas as pd
import numpy as np
import requests
from flask import Flask, render_template, request, flash
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import FloatField, SelectField
from wtforms.validators import DataRequired, NumberRange
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from datetime import datetime, timedelta
from web3 import Web3

# Configure logging at the start
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
csrf = CSRFProtect(app)

class PredictionForm(FlaskForm):
    btc_amount = FloatField('BTC Amount', 
        validators=[
            DataRequired(message="Please enter a BTC amount"),
            NumberRange(min=0.00000001, message="Amount must be positive")
        ])
    tx_size = SelectField('Transaction Size',
        choices=[
            ('simple', 'Simple (250 bytes)'),
            ('average', 'Average (500 bytes)'),
            ('complex', 'Complex (1000 bytes)')
        ],
        validators=[DataRequired()]
    )

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
    form = PredictionForm()
    if request.method == 'POST' and form.validate():
        try:
            btc_amount = form.btc_amount.data
            tx_size = form.tx_size.data
            
            predictor = FeePredictor()
            logger.info("Fetching historical data...")
            if not predictor.fetch_historical_data(days=60):
                flash('Failed to fetch historical data')
                return render_template('index.html', form=form)
            
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
            return render_template('index.html', form=form)
    
    return render_template('index.html', form=form)

@app.route('/predict/eth', methods=['POST'])
def predict_eth():
    if request.method == 'POST':
        try:
            eth_amount = float(request.form['eth_amount'])
            gas_limit = int(request.form['gas_limit'])
            
            # Connect to Ethereum node (use your preferred provider)
            w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/YOUR-PROJECT-ID'))
            
            # Get current gas price
            gas_price = w3.eth.gas_price
            
            # Calculate fees for different priorities
            fees = []
            priorities = [1.0, 1.5, 2.0]  # Regular, Fast, Instant
            
            for priority in priorities:
                fee_wei = int(gas_price * priority) * gas_limit
                fee_eth = w3.from_wei(fee_wei, 'ether')
                fee_usd = fee_eth * get_eth_price()  # Implement price fetching
                
                fees.append({
                    'priority': 'Regular' if priority == 1.0 else 'Fast' if priority == 1.5 else 'Instant',
                    'fee_eth': f"{fee_eth:.6f}",
                    'fee_usd': f"${fee_usd:.2f}",
                    'time_estimate': '5 min' if priority == 2.0 else '3 min' if priority == 1.5 else '10 min'
                })
            
            return render_template('results.html', results=fees, crypto_type='ETH')
            
        except Exception as e:
            flash(f"Error: {str(e)}")
            return render_template('index.html')

@app.route('/predict/usdc', methods=['POST'])
def predict_usdc():
    # Similar implementation for USDC
    pass

@app.route('/predict/usdt', methods=['POST'])
def predict_usdt():
    # Similar implementation for USDT
    pass

def get_eth_price():
    """Fetch current ETH price in USD"""
    try:
        response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd')
        return response.json()['ethereum']['usd']
    except Exception as e:
        logger.error(f"Error fetching ETH price: {e}")
        return 0

if __name__ == '__main__':
    app.run(debug=True)
