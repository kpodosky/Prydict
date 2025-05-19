import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import requests
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

class FeeArchive:
    def __init__(self):
        self.conn = sqlite3.connect('fee_data.db')
        self.create_table()
        
    def create_table(self):
        """Create database table for storing fee data"""
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS fees (
                    timestamp DATETIME PRIMARY KEY,
                    fee_per_byte REAL,
                    total_fee_btc REAL
                )
            ''')
    
    def store_data(self, timestamp, fee_per_byte, total_fee_btc):
        """Store fee data in database"""
        with self.conn:
            self.conn.execute('''
                INSERT OR IGNORE INTO fees VALUES (?, ?, ?)
            ''', (timestamp, fee_per_byte, total_fee_btc))
    
    def get_weekly_data(self):
        """Retrieve weekly aggregated data"""
        query = '''
            SELECT STRFTIME('%Y-%W', timestamp) as week,
                   AVG(fee_per_byte) as avg_fee,
                   AVG(total_fee_btc) as avg_total
            FROM fees
            GROUP BY week
            ORDER BY week DESC
            LIMIT 12
        '''
        return pd.read_sql(query, self.conn)

class FeePredictor:
    def __init__(self):
        self.data = pd.DataFrame()
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.features = ['hour', 'day_of_week', 'day_of_month', 'month', 'rolling_avg_24h']
        
    def fetch_historical_data(self, days=30):
        """Fetch historical fee data from Blockchain.com API"""
        url = f"https://api.blockchain.info/charts/transaction-fees?timespan={days}days&format=json"
        try:
            response = requests.get(url)
            data = response.json()
            self.data = pd.DataFrame(data['values'])
            self.data['x'] = pd.to_datetime(self.data['x'], unit='s')
            self.data.rename(columns={'x': 'timestamp', 'y': 'fee_per_byte'}, inplace=True)
            return True
        except Exception as e:
            print(f"Error fetching data: {e}")
            return False

    def preprocess_data(self):
        """Create time-based features and rolling averages"""
        df = self.data.copy()
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['day_of_month'] = df['timestamp'].dt.day
        df['month'] = df['timestamp'].dt.month
        df['rolling_avg_24h'] = df['fee_per_byte'].rolling(24, min_periods=1).mean()
        self.data = df.dropna()

    def train_model(self):
        """Train the prediction model"""
        X = self.data[self.features]
        y = self.data['fee_per_byte']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
        self.model.fit(X_train, y_train)
        return mean_absolute_error(y_test, self.model.predict(X_test))

    def predict_fees(self, start_time, hours=168, interval=1):
        """Predict fees for multiple future timestamps"""
        predictions = []
        for hour in range(0, hours, interval):
            timestamp = start_time + timedelta(hours=hour)
            features = self._create_features(timestamp)
            fee = self.model.predict(pd.DataFrame([features]))[0]
            predictions.append((timestamp, fee))
        return sorted(predictions, key=lambda x: x[1])[:5]

    def _create_features(self, timestamp):
        """Create input features for prediction"""
        return {
            'hour': timestamp.hour,
            'day_of_week': timestamp.weekday(),
            'day_of_month': timestamp.day,
            'month': timestamp.month,
            'rolling_avg_24h': self.data['fee_per_byte'].iloc[-24:].mean()
        }

class FeePredictorApp:
    def __init__(self, master):
        self.master = master
        self.predictor = FeePredictor()
        self.archive = FeeArchive()
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """Initialize GUI components"""
        self.master.title("Bitcoin Fee Optimizer Pro")
        self.notebook = ttk.Notebook(self.master)
        
        # Recommendation Tab
        self.recommendation_frame = ttk.Frame(self.notebook)
        self.setup_recommendation_tab()
        
        # Explanation Tab
        self.explanation_frame = ttk.Frame(self.notebook)
        self.setup_explanation_tab()
        
        # Archive Tab
        self.archive_frame = ttk.Frame(self.notebook)
        self.setup_archive_tab()
        
        self.notebook.add(self.recommendation_frame, text="Fee Calculator")
        self.notebook.add(self.explanation_frame, text="How Fees Work")
        self.notebook.add(self.archive_frame, text="Price Archive")
        self.notebook.pack(expand=1, fill="both")

    def setup_recommendation_tab(self):
        """Optimal timing recommendation tab"""
        # Input Section
        input_frame = ttk.Frame(self.recommendation_frame)
        input_frame.pack(pady=10)
        
        ttk.Label(input_frame, text="BTC Amount:").grid(row=0, column=0, padx=5)
        self.btc_amount = tk.DoubleVar()
        ttk.Entry(input_frame, textvariable=self.btc_amount, width=15).grid(row=0, column=1, padx=5)
        
        ttk.Label(input_frame, text="Transaction Complexity:").grid(row=0, column=2, padx=5)
        self.tx_size = ttk.Combobox(input_frame, values=["Simple (250 bytes)", "Average (500 bytes)", "Complex (1000 bytes)"], width=15)
        self.tx_size.current(0)
        self.tx_size.grid(row=0, column=3, padx=5)
        
        ttk.Button(input_frame, text="Calculate Optimal Times", 
                 command=self.update_recommendations).grid(row=0, column=4, padx=5)
        
        # Results Section
        self.results_frame = ttk.Frame(self.recommendation_frame)
        self.results_frame.pack(fill='both', expand=True)
        
        columns = ("Time", "Fee Rate", "Total Fee", "Fee %")
        self.recommendations = ttk.Treeview(self.results_frame, columns=columns, show="headings")
        
        for col in columns:
            self.recommendations.heading(col, text=col)
            self.recommendations.column(col, width=120)
            
        self.recommendations.pack(fill='both', expand=True)

    def setup_explanation_tab(self):
        """Tab explaining fee calculation"""
        explanation = """Bitcoin Transaction Fees Explained:

1. Fees are based on transaction size (in bytes), not BTC amount
2. Transaction size depends on:
   - Number of inputs (previous transactions being spent)
   - Number of outputs (recipient addresses)
3. Typical transaction sizes:
   - Simple transaction: 250 bytes
   - Multi-input transaction: 500 bytes
   - Complex transaction: 1000+ bytes
4. Fee Rate = satoshis per byte (sat/byte)
5. Total Fee = Fee Rate × Transaction Size

The calculator estimates fees based on:
- Historical fee patterns
- Time of day/week trends
- Current network conditions"""
        
        text = tk.Text(self.explanation_frame, wrap="word", padx=10, pady=10)
        text.insert("1.0", explanation)
        text.config(state="disabled")
        text.pack(fill="both", expand=True)

    def setup_archive_tab(self):
        """Tab for historical price visualization"""
        # Weekly bar chart
        self.fig_archive, self.ax_archive = plt.subplots(figsize=(10, 4))
        self.canvas_archive = FigureCanvasTkAgg(self.fig_archive, master=self.archive_frame)
        self.canvas_archive.get_tk_widget().pack(fill='both', expand=True)
        
        # Refresh button
        ttk.Button(self.archive_frame, text="Refresh Archive",
                 command=self.update_archive).pack(pady=5)

    def load_data(self):
        """Load and prepare historical data"""
        if not self.predictor.fetch_historical_data(days=60):
            messagebox.showerror("Error", "Failed to fetch historical data")
            return
            
        self.predictor.preprocess_data()
        try:
            mae = self.predictor.train_model()
            print(f"Model trained with MAE: {mae:.2f} sat/byte")
        except Exception as e:
            messagebox.showerror("Error", f"Model training failed: {str(e)}")

    def update_recommendations(self):
        """Calculate and display optimal transaction times"""
        try:
            btc_amount = self.btc_amount.get()
            if btc_amount <= 0:
                raise ValueError("BTC amount must be positive")
                
            # Get transaction size from selection
            size_mapping = {"Simple (250 bytes)": 250, 
                           "Average (500 bytes)": 500,
                           "Complex (1000 bytes)": 1000}
            tx_size_bytes = size_mapping[self.tx_size.get()]
            
            # Get predictions
            start_time = datetime.now()
            best_times = self.predictor.predict_fees(start_time)
            
            # Clear existing recommendations
            self.recommendations.delete(*self.recommendations.get_children())
            
            # Calculate and display results
            for time, fee_rate in best_times:
                total_fee_sats = fee_rate * tx_size_bytes
                total_fee_btc = total_fee_sats / 1e8  # Convert sats to BTC
                fee_percentage = (total_fee_btc / btc_amount) * 100 if btc_amount > 0 else 0
                
                self.recommendations.insert("", "end", values=(
                    time.strftime('%Y-%m-%d %H:%M'),
                    f"{fee_rate:.1f} sat/byte",
                    f"{total_fee_btc:.8f} BTC",
                    f"{fee_percentage:.4f}%"
                ))
                
                # Store transaction data
                self.archive.store_data(
                    time.isoformat(),
                    fee_rate,
                    total_fee_btc
                )
                
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to calculate fees: {str(e)}")

    def update_archive(self):
        """Update the weekly price bar chart"""
        self.ax_archive.clear()
        
        weekly_data = self.archive.get_weekly_data()
        if not weekly_data.empty:
            weekly_data['week'] = pd.to_datetime(weekly_data['week'] + '-1', format='%Y-%W-%w')
            
            self.ax_archive.bar(
                weekly_data['week'],
                weekly_data['avg_fee'],
                width=5,
                color='skyblue'
            )
            
            self.ax_archive.set_title("12-Week Average Fees")
            self.ax_archive.set_ylabel("Fee (sat/byte)")
            self.ax_archive.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
            self.fig_archive.autofmt_xdate()
        
        self.canvas_archive.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = FeePredictorApp(root)
    root.mainloop()
