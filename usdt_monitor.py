import requests
import time
import logging
from datetime import datetime
from collections import defaultdict
from keys import YOUR_ETHERSCAN_API_KEY

# Add known addresses dictionary
KNOWN_ADDRESSES = {
    'binance': {
        'addresses': [
            '0x28C6c06298d514Db089934071355E5743bf21d60',  # Binance Hot Wallet
            '0x21a31Ee1afC51d94C2eFcCAa2092aD1028285549',  # Binance Cold Wallet
            '0x5a52E96BAcdaBb82fd05763E25335261B270Efcb',  # Binance USDT Cold
            '0x9696f59E4d72E237BE84fFD425DCaD154Bf96976',  # Binance USDC Hot
            '0x4270BB238f6DD8B1c3ca01f96CA65b2647c06D3C',  # Binance Bridge
        ]
    },
    'coinbase': {
        'addresses': [
            '0xa090e606E30bD747d4E6245a1517EbE430F0057e',  # Coinbase USDT
            '0xF6874c88757721a02F47592140905C4336DfBc61',  # Coinbase Commerce
            '0x7180eB39A6264938FDb3EfFD7341C4727c382153',  # Coinbase Protocol
            '0x3052cd6bf951449a984fe4b5a38b46aef9455c8e'   # Coinbase Pool
        ]
    },
    'bitget': {
        'addresses': [
            '0x0639556F03714A74a5fEEaF5736a4A64fF70D206',  # Bitget Hot Wallet
            '0x5bdf85216ec1e38d6458c870992a69e38e03f7ef'   # Bitget Cold Storage
        ]
    },
    'bybit': {
        'addresses': [
            '0x1Db92e43C9c6F4c7f0c59C986e0033B941D01D4C',  # Bybit Hot Wallet
            '0x00000000219ab540356cbb839cbe05303d7705fa'    # Bybit Staking
        ]
    },
    'okx': {
        'addresses': [
            '0x5041ed759dd4afc3a72b8192c143f72f4724081a',  # OKX USDT Reserve
            '0x1c4b70a3968436b9a0a9cf5205c787eb81bb558c',  # OKX Hot Wallet 2
            '0x36b0b0d46c1990b3f035f9c9c907bef0af0e2426',  # OKX Bridge
            '0x3019d4e366576a88d28b623afaf3ecb9ec9d9580'   # OKX Earn
        ]
    },
    'kraken': {
        'addresses': [
            '0x2910543af39aba0cd09dbb2d50200b3e800a63d2',  # Kraken Main
            '0x0a869d79a7052c7f1b55a8ebabbea3420f0d1e13',  # Kraken Hot
            '0xe853c56864a2ebe4576a807d26fdc4a0ada51919',  # Kraken USDT
            '0x267be1c1d684f78cb4f6a176c4911b741e4ffdc0'   # Kraken USDC
        ]
    },
    'kucoin': {
        'addresses': [
            '0x2B5634C42055806a59e9107ED44D43c426E58258',  # KuCoin Hot Wallet
            '0x689C56AEf474Df92D44A1B70850f808488F9769C'   # KuCoin Cold Wallet
        ]
    },
    'gemini': {
        'addresses': [
            '0xd24400ae8bfebb18ca49be86258a3c749cf46853',  # Gemini Hot Wallet
            '0x6fc82a5fe25a5cdb58bc74600a40a69c065263f8'   # Gemini Cold Storage
        ]
    },
    'bitfinex': {
        'addresses': [
            '0x876EabF441B2EE5B5b0554Fd502a8E0600950cFa',  # Bitfinex Hot Wallet
            '0xDc8bD6c290FF2C1a618c8b9C4EDd99eaCE56826d'   # Bitfinex Cold Storage
        ]
    },
    'gate_io': {
        'addresses': [
            '0x0D0707963952f2fBA59dD06f2b425ace40b492Fe',  # Gate.io Hot
            '0x1c4b70a3968436b9a0a9cf5205c787eb81bb558c'   # Gate.io Cold
        ]
    },
    'huobi': {
        'addresses': [
            '0x5a52e96bacdabb82fd05763e25335261b270efcb',  # Huobi Hot Wallet
            '0x6748f50f686bfbca6fe8ad62b22228b87f31ff2b'   # Huobi Cold Storage
        ]
    }
    # Add more exchanges as you get their verified addresses
}

KNOWN_ADDRESSES.update({
    'cryptocom': {
        'addresses': [
            '0x6262998Ced04146fA42253a5C0AF90CA02dfd2A3',  # Crypto.com USDT
            '0x72A53cDBBcc1b9efa39c834A540550e23463AAcB',  # Crypto.com Hot
            '0x7758E507850dA48cd47f4fate72b8c88D4D17699'   # Crypto.com USDC
        ]
    },
    'arkham': {
        'addresses': [
            '0x738399AeB122b05471A746E9E4C6d7640C7Cfe47',  # Arkham USDT
            '0x0A42d758Bf9F9b6f4d96B7cF2347dF3aDD2c864b'   # Arkham USDC
        ]
    },
    'luno': {
        'addresses': [
            '0x12D05AEBc6aaF2994839D4B4bD8E5AB0cCCB91d5',  # Luno Hot
            '0xF8b04F5185F58Bce1fa0E1F4B8f211a6a0E54463'   # Luno Cold
        ]
    },
    'mexc_additional': {
        'addresses': [
            '0x71dB18356C5F7b1Da3b4Ef20494722c35f3Cb728',  # MEXC USDT 
            '0x0211F3cEDbEf3143223D3ACF0e589747933139c5'   # MEXC USDC
        ]
    },
    'htx': {  # Former Huobi
        'addresses': [
            '0xeEE28d484628d41A82d01e21d12E2E78D69920da',  # HTX USDT
            '0x5c985E89DDe482eFE97ea9f1950aD149Eb73829B',  # HTX Hot
            '0x4Fabb145d64652a948d72533023f6E7A623C7C53'   # HTX USDC
        ]
    },
    'whitebit_new': {
        'addresses': [
            '0x39F6a6C85d39d5ABAd8A398310c52E7c374F2bA3',  # WhiteBIT USDT
            '0xDD96B55D3D28D4608A9E99c0a242bF9089126791'   # WhiteBIT USDC
        ]
    },
    'pionex': {
        'addresses': [
            '0x8705CCF3B08E95f0Af13726EaAE7c91585C5b556',  # Pionex USDT
            '0xBa7B3387D88Bd7675DE8B492cCD69cB11d61b787'   # Pionex Hot
        ]
    },
    'bingx': {
        'addresses': [
            '0x33f6D189826E12dB263f6E7B466A8844eB854907',  # BingX USDT
            '0x44b37Aa45D275E7Bb3cB2E8D6777C3c8F0D3f1b4'   # BingX USDC
        ]
    },
    'hashkey': {
        'addresses': [
            '0x892789F732182c2F7a2665B603B59D618d691Ae4',  # HashKey USDT
            '0x0C58B57E2e0675eDcB8AEb42665b552A00B62915'   # HashKey USDC
        ]
    },
    'backpack': {
        'addresses': [
            '0x2B95A1Dcc519A08519Fc0fb3E8e64eF0A8c923bE',  # Backpack USDT
            '0x2B5634C42055806a59e9107ED44D43c426E58258'   # Backpack Hot
        ]
    },
    'binance_us': {
        'addresses': [
            '0x892789F732182c2F7a2665B603B59D618d691Ae4',  # Binance.US USDT
            '0x7758E507850dA48cd47f4fate72b8c88D4D17699'   # Binance.US USDC
        ]
    },
    'bitmart_new': {
        'addresses': [
            '0xE79eE3c62004339E730FB5036e0Bfc44E76559Bb',  # BitMart USDT
            '0x1d036LogF85F5A08D29A8bd5D850EBc046feB848'   # BitMart USDC
        ]
    },
    'defi_protocols': {
        'addresses': [
            '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D',  # Uniswap V2 Router
            '0x68b3465833fb72a70ecdf485e0e4c7bd8665fc45',  # Uniswap V3 Router
            '0xDef1C0ded9bec7F1a1670819833240f027b25EfF',  # 0x Protocol
            '0x11111112542D85B3EF69AE05771c2dCCff4fAa26',  # 1inch Router
            '0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9'   # Aave V2
        ]
    },
    'stablecoin_issuers': {
        'addresses': [
            '0x5754284f345afc66a98fbb0a0afe71e0f007b949',  # Tether Treasury
            '0x0000000000000000000000000000000000000000',  # USDC Reserve
            '0x47ac0Fb4F2D84898e4D9E7b4DaB3C24507a6D503'   # Paxos Treasury
        ]
    },
    'institutional': {
        'addresses': [
            '0x40ec5B33f54e0e8A33A975908C5BA1c14e5BbbDf',  # Grayscale
            '0xc6CDE7C39eB2f0F0095F41570af89eFC2C1Ea828',  # Jump Trading
            '0x1Db3439a222C519ab44bb1144fC28167b4Fa6EE6'   # Three Arrows Capital
        ]
    },
    'dao_treasuries': {
        'addresses': [
            '0xBE8E3e3618f7474F8cB1d074A26afFef007E98FB',  # MakerDAO
            '0x73feaa1eE314F8c655E354234017bE2193C9E24E',  # Curve DAO
            '0x8EB8a3b98659Cce290402893d0123abb75E3ab28'   # Yearn Treasury
        ]
    },
    'validators': {
        'addresses': [
            '0x00000000219ab540356cBB839Cbe05303d7705Fa',  # Ethereum 2.0 Deposit
            '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',  # Wrapped ETH
            '0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84'   # Lido
        ]
    },
    'venture_capital': {
        'addresses': [
            '0x4862733B5FdDFd35f35ea8CCf08F5045e57388B3',  # Polychain Capital
            '0x8d12A197cB00D4747a1fe03395095ce2A5CC6819',  # A16z
            '0x99d1Fa417f94dcD62BfE781a1213c092a47041Bc'   # Paradigm
        ]
    },
    'gaming_nft': {
        'addresses': [
            '0x8a90CAb2b38dba80c64b7734e58Ee1dB38B8992e',  # Doodles
            '0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D',  # BAYC
            '0x60E4d786628Fea6478F785A6d7e704777c86a7c6'   # MAYC
        ]
    },
    'lending_platforms': {
        'addresses': [
            '0x3d9819210A31b4961b30EF54bE2aeD79B9c9Cd3B',  # Compound
            '0x398eC7346DcD622eDc5ae82352F02bE94C62d119',  # Aave
            '0x0brothers0c481D6447f4eA15baAB1EF89E4b0A2c934'   # Celsius
        ]
    }
})

class CryptoWhaleTracker:
    def __init__(self, min_usdt=1000000, min_eth=1000000):
        self.base_url = "https://api.etherscan.io/api"
        self.min_usdt = min_usdt
        self.min_eth = min_eth
        self.eth_price = 0
        self.last_block = None
        self.processed_blocks = set()
        self.api_key = YOUR_ETHERSCAN_API_KEY
        self.retry_count = 3
        self.retry_delay = 5
        self.rate_limit_delay = 0.2
        self.logger = logging.getLogger('crypto_whale_tracker')
        
        # Add ETH tracking alongside stablecoins
        self.contracts = {
            'eth': '0x0000000000000000000000000000000000000000',  # ETH native token
            'usdt_ethereum': '0xdac17f958d2ee523a2206206994597c13d831ec7',  # Ethereum USDT
            'usdc_ethereum': '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48',  # Ethereum USDC
        }

    def monitor_transfers(self):
        """Main monitoring loop"""
        print(f"🚀 Starting monitoring - Min USDT: ${self.min_usdt:,.2f}, Min ETH: {self.min_eth} ETH")
        
        while True:
            try:
                block = self.get_latest_block()
                if block:
                    transfers = self.get_all_transfers(block)
                    for tx in transfers:
                        message = self.format_transfer_message(tx)
                        print(f"\n{message}")
                time.sleep(15)
                
            except KeyboardInterrupt:
                print("\n👋 Stopping monitor...")
                break
            except Exception as e:
                print(f"Error in main loop: {e}")
                time.sleep(30)

    def get_latest_block(self):
        """Get latest Ethereum block"""
        try:
            response = requests.get(
                self.base_url,
                params={
                    "module": "proxy",
                    "action": "eth_blockNumber",
                    "apikey": self.api_key
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('result'):
                    block_num = int(data['result'], 16)
                    if block_num != self.last_block:
                        self.last_block = block_num
                        print(f"Processing block: {block_num}")
                        return block_num
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get latest block: {e}")
            return None

    def get_all_transfers(self, block_number):
        """Get all token transfers from block"""
        transfers = []
        
        # Check ETH transfers
        eth_params = {
            "module": "proxy",
            "action": "eth_getBlockByNumber",
            "tag": hex(block_number),
            "boolean": "true",
            "apikey": self.api_key
        }
        
        try:
            response = requests.get(self.base_url, params=eth_params, timeout=10)
            if response.status_code == 200:
                block_data = response.json().get('result', {})
                if block_data and 'transactions' in block_data:
                    for tx in block_data['transactions']:
                        amount = float(int(tx['value'], 16)) / 1e18  # Convert Wei to ETH
                        if amount >= self.min_eth:
                            transfers.append({
                                'token': 'ETH',
                                'hash': tx['hash'],
                                'from': tx['from'],
                                'to': tx['to'],
                                'amount': amount,
                                'fee': float(int(tx['gas'], 16) * int(tx['gasPrice'], 16)) / 1e18
                            })
            
            # Check USDT/USDC transfers
            for token, contract in self.contracts.items():
                if token == 'eth':
                    continue
                    
                token_params = {
                    "module": "account",
                    "action": "tokentx",
                    "contractaddress": contract,
                    "startblock": str(block_number),
                    "endblock": str(block_number),
                    "apikey": self.api_key
                }
                
                response = requests.get(self.base_url, params=token_params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') == '1' and data.get('result'):
                        for tx in data['result']:
                            amount = float(tx['value']) / 1e6  # Convert to USDT/USDC
                            if amount >= self.min_usdt:
                                transfers.append({
                                    'token': token.split('_')[0].upper(),
                                    'hash': tx['hash'],
                                    'from': tx['from'],
                                    'to': tx['to'],
                                    'amount': amount,
                                    'fee': float(tx['gasUsed']) * float(tx['gasPrice']) / 1e18
                                })
                
                time.sleep(self.rate_limit_delay)  # Respect rate limits
                
        except Exception as e:
            self.logger.error(f"Error getting transfers: {e}")
            
        return transfers

    def format_transfer_message(self, transfer):
        """Format whale transfer alert message"""
        alert_count = min(3, max(1, int(transfer['amount'] / 1000000)))
        alerts = "🚨" * alert_count
        
        from_entity = self.get_entity_name(transfer['from'])
        to_entity = self.get_entity_name(transfer['to'])
        
        token = transfer['token'].lower()
        amount = transfer['amount']
        usd_amount = transfer['usd_amount'] if 'usd_amount' in transfer else amount
        
        return (
            f"{alerts} {amount:.2f} #{token} "
            f"(${usd_amount:,.2f} USD) transferred "
            f"from #{from_entity} to #{to_entity} "
            f"for a ${transfer.get('fee', 0.0) * 40000:.2f} fee"
        )

    def get_entity_name(self, address):
        """Get entity name from address"""
        address = address.lower()
        for entity, data in KNOWN_ADDRESSES.items():
            if address in [addr.lower() for addr in data['addresses']]:
                return entity
        return 'unknown'

    def get_eth_price(self):
        """Get current ETH price"""
        try:
            response = requests.get(
                "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd",
                timeout=10
            )
            if response.status_code == 200:
                return float(response.json()['ethereum']['usd'])
        except Exception as e:
            self.logger.error(f"Error getting ETH price: {e}")
        return 0

# Add main execution
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Create and run tracker
    tracker = CryptoWhaleTracker(min_usdt=5000000, min_eth=5000000)
    tracker.monitor_transfers()
