# -*- coding: UTF-8 -*-
import requests
import time
import os
from datetime import datetime
from collections import defaultdict
import re

class BitcoinWhaleTracker:
    def __init__(self, min_btc=100):
        self.base_url = "https://blockchain.info"
        self.min_btc = min_btc
        self.satoshi_to_btc = 100000000
        self.processed_blocks = set()  # Track processed blocks
        self.last_block_height = None  # Track last block height
        
        # Create svg output directory if it doesn't exist
        self.svg_dir = "whale_transactions_svg"
        if not os.path.exists(self.svg_dir):
            os.makedirs(self.svg_dir)
        
        # Address statistics tracking
        self.address_stats = defaultdict(lambda: {
            'received_count': 0,
            'sent_count': 0,
            'total_received': 0,
            'total_sent': 0,
            'last_seen': None
        })

        # Add known addresses dictionary
        self.known_addresses = {
            'exchanges': {
                'binance': [
                    '34xp4vRoCGJym3xR7yCVPFHoCNxv4Twseo',  # Binance Cold Wallet
                    '3FaA4dJuuvJFyUHbqHLkZKJcuDPugvG3zE',  # Binance Hot Wallet
                ],
                'coinbase': [
                    '3Kzh9qAqVWQhEsfQz7zEQL1EuSx5tyNLNS',  # Coinbase Cold Storage
                    '3FzScn724foqFRWvL1kCZwitQvcxrnSQ4K',  # Coinbase Hot Wallet
                ],
                'kraken': [
                    '3FupZp77ySr7jwoLYEJ9mwzJpvoNBXsBnE',  # Kraken Storage
                ],
            },
            'miners': {
                'f2pool': [
                    '3HuobiNg2wHjdPU2mQczL9on8WF7hZmaGd',  # F2Pool
                ],
                'antpool': [
                    '1CjPR7Z5ZSyWk6WtXvSFgkptmpoi4UM9BC',  # Antpool
                ],
            }
        }

    def get_entity_name(self, address):
        """Identify the entity associated with an address"""
        for category, entities in self.known_addresses.items():
            for entity, addresses in entities.items():
                if address in addresses:
                    return f"{entity.upper()} ({category})"
        return "Unknown Entity"

    def get_latest_block(self):
        """Get latest block hash"""
        try:
            response = requests.get(f"{self.base_url}/latestblock")
            if response.status_code == 200:
                return response.json()['hash']
            return None
        except Exception as e:
            print(f"Error getting latest block: {e}")
            return None

    def get_block_transactions(self, block_hash):
        """Get transactions from a block"""
        try:
            response = requests.get(f"{self.base_url}/rawblock/{block_hash}")
            if response.status_code == 200:
                return response.json()['tx']
            return []
        except Exception as e:
            print(f"Error getting block transactions: {e}")
            return []

    def process_transaction(self, tx):
        """Process a transaction and return if it's a whale movement"""
        try:
            # Calculate total input value
            input_value = sum(inp.get('prev_out', {}).get('value', 0) 
                            for inp in tx.get('inputs', []))
            btc_value = input_value / self.satoshi_to_btc
            
            if btc_value < self.min_btc:
                return None
                
            # Get sender and receiver addresses
            sender = tx.get('inputs', [{}])[0].get('prev_out', {}).get('addr', 'Unknown')
            receiver = tx.get('out', [{}])[0].get('addr', 'Unknown')
            
            # Get entity names
            from_entity = self.get_entity_name(sender)
            to_entity = self.get_entity_name(receiver)
            
            # Calculate fee
            output_value = sum(out.get('value', 0) for out in tx.get('out', []))
            fee = (input_value - output_value) / self.satoshi_to_btc
            
            # Determine transaction type
            if 'exchange' in from_entity.lower():
                tx_type = 'withdrawal'
            elif 'exchange' in to_entity.lower():
                tx_type = 'deposit'
            else:
                tx_type = 'transfer'
            
            # Update address statistics
            self.update_address_stats(sender, receiver, btc_value)
            
            return {
                'timestamp': datetime.fromtimestamp(tx.get('time', 0)).strftime('%Y-%m-%d %H:%M:%S'),
                'transaction_hash': tx.get('hash', 'Unknown'),
                'btc_volume': f"{btc_value:.8f}",
                'fee_btc': f"{fee:.8f}",
                'sender': sender,
                'receiver': receiver,
                'from_entity': from_entity,
                'to_entity': to_entity,
                'tx_type': tx_type
            }
            
        except Exception as e:
            print(f"Error processing transaction: {e}")
            return None

    def update_address_stats(self, sender, receiver, amount):
        """Update statistics for addresses involved in transaction"""
        now = datetime.now()
        
        # Update sender stats
        self.address_stats[sender]['sent_count'] += 1
        self.address_stats[sender]['total_sent'] += amount
        self.address_stats[sender]['last_seen'] = now
        
        # Update receiver stats
        self.address_stats[receiver]['received_count'] += 1
        self.address_stats[receiver]['total_received'] += amount
        self.address_stats[receiver]['last_seen'] = now

    def monitor_transactions(self):
        """Monitor for whale transactions"""
        while True:
            try:
                block_hash = self.get_latest_block()
                if block_hash:
                    transactions = self.get_block_transactions(block_hash)
                    for tx in transactions:
                        whale_tx = self.process_transaction(tx)
                        if whale_tx:
                            yield whale_tx
                time.sleep(30)  # Wait 30 seconds before next check
            except Exception as e:
                print(f"Error monitoring transactions: {e}")
                time.sleep(30)

if __name__ == "__main__":
    try:
        print("\n" + "=" * 80)
        print("🐋 Bitcoin Whale Transaction Monitor Starting")
        print("📊 Minimum transaction size: 100 BTC")
        print("📅 Started at:", time.strftime("%Y-%m-%d %H:%M:%S"))
        print("⚡ Press Ctrl+C to stop monitoring")
        print("=" * 80 + "\n")
        
        # Create tracker instance
        tracker = BitcoinWhaleTracker(min_btc=100)
        
        # Start monitoring
        for whale_tx in tracker.monitor_transactions():
            print(f"🚨 Whale Transaction Detected: {whale_tx}")
        
    except KeyboardInterrupt:
        print("\n" + "=" * 80)
        print("🛑 Stopping whale transaction monitor...")
        print("=" * 80 + "\n")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
