import logging
import pandas as pd
import numpy as np
import requests
from flask import render_template, request, flash, jsonify
from Prydict import app, transaction_queue, whale_tracker
from Prydict.forms import PredictionForm
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import FloatField, SelectField
from wtforms.validators import DataRequired, NumberRange
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from datetime import datetime, timedelta
from web3 import Web3
from queue import Queue
import threading
from bitcoin_whale_tracker import BitcoinWhaleTracker
import time

# Configure logging at the start
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

csrf = CSRFProtect(app)

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

def predict_btc():
    form = PredictionForm()
    if form.validate_on_submit():
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
            
            return render_template('results.html', results=results, crypto_type='BTC')
            
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            flash(f"An error occurred: {str(e)}")
    
    return render_template('index.html', form=form)

def predict_eth():
    form = PredictionForm()
    if form.validate_on_submit():
        try:
            eth_amount = form.eth_amount.data
            gas_limit = int(form.gas_limit.data)
            
            # Connect to Ethereum node
            w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/YOUR-PROJECT-ID'))
            
            # Get current gas price
            gas_price = w3.eth.gas_price
            
            results = []
            priorities = [1.0, 1.5, 2.0]  # Regular, Fast, Instant
            
            for priority in priorities:
                fee_wei = int(gas_price * priority) * gas_limit
                fee_eth = w3.from_wei(fee_wei, 'ether')
                fee_usd = fee_eth * get_eth_price()
                
                results.append({
                    'priority': 'Regular' if priority == 1.0 else 'Fast' if priority == 1.5 else 'Instant',
                    'fee_eth': f"{fee_eth:.6f}",
                    'fee_usd': f"${fee_usd:.2f}",
                    'time_estimate': '5 min' if priority == 2.0 else '3 min' if priority == 1.5 else '10 min'
                })
            
            return render_template('results.html', results=results, crypto_type='ETH')
            
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            flash(f"An error occurred: {str(e)}")
    
    return render_template('index.html', form=form)

def predict_usdc():
    form = PredictionForm()
    if form.validate_on_submit():
        try:
            usdc_amount = form.usdc_amount.data
            gas_limit = 65000  # Standard ERC20 transfer
            
            w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/YOUR-PROJECT-ID'))
            gas_price = w3.eth.gas_price
            
            results = []
            priorities = [1.0, 1.5, 2.0]
            
            for priority in priorities:
                fee_wei = int(gas_price * priority) * gas_limit
                fee_eth = w3.from_wei(fee_wei, 'ether')
                fee_usd = fee_eth * get_eth_price()
                
                results.append({
                    'priority': 'Regular' if priority == 1.0 else 'Fast' if priority == 1.5 else 'Instant',
                    'fee_eth': f"{fee_eth:.6f}",
                    'fee_usd': f"${fee_usd:.2f}",
                    'token_fee': f"${(fee_usd / usdc_amount * 100):.4f}%",
                    'time_estimate': '5 min' if priority == 2.0 else '3 min' if priority == 1.5 else '10 min'
                })
            
            return render_template('results.html', results=results, crypto_type='USDC')
            
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            flash(f"An error occurred: {str(e)}")
    
    return render_template('index.html', form=form)

def get_whale_transactions():
    transactions = []
    try:
        while not transaction_queue.empty():
            tx = transaction_queue.get_nowait()
            transactions.append(tx)
        return jsonify(transactions)
    except Exception as e:
        logger.error(f"Error getting whale transactions: {e}")
        return jsonify([])

def whale_watch():
    global whale_tracker
    
    try:
        min_btc = float(request.form.get('min_whale_btc', 100))
        
        if whale_tracker is None:
            whale_tracker = BitcoinWhaleTracker(min_btc=min_btc)
            
            def track_transactions():
                while True:
                    try:
                        current_block = whale_tracker.get_latest_block()
                        if current_block:
                            transactions = whale_tracker.get_block_transactions(current_block)
                            for tx in transactions:
                                if whale_tracker.is_whale_transaction(tx):
                                    processed_tx = whale_tracker.process_transaction(tx)
                                    if processed_tx and not transaction_queue.full():
                                        transaction_queue.put(processed_tx)
                        time.sleep(30)  # Wait 30 seconds before next check
                    except Exception as e:
                        logger.error(f"Error in transaction tracking: {e}")
                        time.sleep(30)
            
            # Start tracking in background thread
            thread = threading.Thread(target=track_transactions, daemon=True)
            thread.start()
            flash('Whale watch started successfully!')
        else:
            flash('Whale watch is already running')
            
        return render_template('index.html', form=PredictionForm())
        
    except Exception as e:
        logger.error(f"Error starting whale watch: {e}")
        flash(f"Error starting whale watch: {str(e)}")
        return render_template('index.html', form=PredictionForm())

def get_eth_price():
    try:
        response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd')
        return response.json()['ethereum']['usd']
    except Exception as e:
        logger.error(f"Error fetching ETH price: {e}")
        return 0