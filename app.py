from flask import Flask, render_template, request
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import requests
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

app = Flask(__name__)

class FeePredictor:
    # Keep the FeePredictor class from previous code
    # ... [Previous FeePredictor implementation] ...

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Process form data
        btc_amount = float(request.form['btc_amount'])
        tx_size = request.form['tx_size']
        
        # Get predictions
        predictor = FeePredictor()
        if not predictor.fetch_historical_data(days=60):
            return render_template('error.html', message="Failed to fetch data")
            
        predictor.preprocess_data()
        predictor.train_model()
        
        # Generate predictions
        start_time = datetime.now()
        best_times = predictor.predict_fees(start_time)
        
        # Process results
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
        
        return render_template('results.html', results=results)
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
