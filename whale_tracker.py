from datetime import datetime
from collections import deque
import threading
import time

class WhaleTracker:
    def __init__(self):
        self.transactions = deque(maxlen=50)  # Store last 50 transactions
        self.is_running = False
        self.thread = None

    def start_tracking(self):
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self._track_transactions)
            self.thread.daemon = True
            self.thread.start()

    def stop_tracking(self):
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=1.0)

    def _track_transactions(self):
        while self.is_running:
            # Simulate whale transaction (replace with actual blockchain API calls)
            transaction = {
                "type": "INTERNAL TRANSFER",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "hash": "0x7a23c98ff44b3214567890abcdef123456789012",
                "amount": "235.45",
                "fee": "0.00034521",
                "from_address": "3FaA4dJuuvJFyUHbqHLkZKJcuDPugvG3zE",
                "from_label": "BINANCE EXCHANGE",
                "from_history": "(BINANCE EXCHANGE) [↑1234|↓789] Total: ↑45678.23|↓34567.12 BTC",
                "to_address": "1NDyJtNTjmwk5xPNhjgAMu4HDHigtobu1s",
                "to_label": "BINANCE EXCHANGE",
                "to_history": "(BINANCE EXCHANGE) [↑567|↓890] Total: ↑23456.78|↓12345.67 BTC"
            }
            self.transactions.appendleft(transaction)
            time.sleep(90)  # Wait 1.5 minutes between updates

    def get_transactions(self):
        return list(self.transactions)