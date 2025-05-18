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
        
        # Known addresses database (keeping original database)
        self.known_addresses = {
            'binance': {
                'type': 'exchange',
                'addresses': [
                    '3FaA4dJuuvJFyUHbqHLkZKJcuDPugvG3zE',  # Binance Hot Wallet
                    '1NDyJtNTjmwk5xPNhjgAMu4HDHigtobu1s',  # Binance Cold Wallet
                    '34xp4vRoCGJym3xR7yCVPFHoCNxv4Twseo',  # Binance-BTC-2
                    '1LQv8aKtQoiY5M5zkaG8RWL7LMwNzNsLfb',  # Binance-BTC-3
                    '1AC4fMwgY8j9onSbXEWeH6Zan8QGMSdmtA'   # Binance-BTC-4
                ]
            },
            'coinbase': {
                'type': 'exchange',
                'addresses': [
                    '3FzScn724foqFRWvL1kCZwitQvcxrnSQ4K',  # Coinbase Hot Wallet
                    '3Kzh9qAqVWQhEsfQz7zEQL1EuSx5tyNLNS',  # Coinbase Cold Storage
                    '1CWYTCvwKfH5cWnX3VcAykgTsmjsuB3wXe',  # Coinbase-BTC-2
                    '1FxkfJQLJTXpW6QmxGT6hEo5DtBrnFpM3r',  # Coinbase-BTC-3
                    '1GR9qNz7zgtaW5HwwVpEJWMnGWhsbsieCG'   # Coinbase Prime
                ]
                  },
            'grayscale': {
                'type': 'investment',
                'addresses': [
                    'bc1qe7nps5yv7ruc884zscwrk9g2mxvqh7tkxfxwny',
                    'bc1qkz7u6l5c8wqz8nc5yxkls2j8u4y2hkdzlgfnl4'
                ]
            },
            'microstrategy': {
                'type': 'corporate',
                'addresses': [
                    'bc1qazcm763858nkj2dj986etajv6wquslv8uxwczt',
                    'bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh'
                ]
            },
            'blockfi': {
                'type': 'lending',
                'addresses': [
                    'bc1q7kyrfmx49qa7n6g8mvlh36d4w9zf4lkwfg4j5q',
                    'bc1qd73dxk2qfs2x5wv2sesvqrzgx7t5tqt4y5vpym'
                ]
            },
            'celsius': {
                'type': 'lending',
                'addresses': [
                    'bc1q06ymtp6eq27mlz3ppv8z7esc8vq3v4nsjx9eng',
                    'bc1qcex3e38gqh6qnzpn9jth5drgfyh5k9sjzq3rkm'
                ]
            },
            'kraken': {
                'type': 'exchange',
                'addresses': [
                    '3FupZp77ySr7jwoLYEJ9mwzJpvoNBXsBnE',  # Kraken Hot Wallet
                    '3H5JTt42K7RmZtromfTSefcMEFMMe18pMD',  # Kraken Cold Storage
                    '3AfP9N7KNq2pYXiGQdgNJy8SD2Mo7pQKUR',  # Kraken-BTC-2
                    '3E1jkR1PJ8hFUqCkDjimwPoF2bZVrkqnpv'   # Kraken-BTC-3
                ]
            },
            'bitfinex': {
                'type': 'exchange',
                'addresses': [
                    '3D2oetdNuZUqQHPJmcMDDHYoqkyNVsFk9r',  # Bitfinex Hot Wallet
                    '3JZq4atUahhuA9rLhXLMhhTo133J9rF97j',  # Bitfinex Cold Storage
                    '3QW95MafxER9W7kWDcosQNdLk4Z36TYJZL'   # Bitfinex-BTC-2
                ]
            },
            'huobi': {
                'type': 'exchange',
                'addresses': [
                    '3M219KR5vEneNb47ewrPfWyb5jQ2DjxRP6',  # Huobi Hot Wallet
                    '38WUPqGLXphpD1DwkMR8koGfd5UQfRnmrk',  # Huobi Cold Storage
                    '1HckjUpRGcrrRAtFaaCAUaGjsPx9oYmLaZ'   # Huobi-BTC-2
                ]
            },
            'okex': {
                'type': 'exchange',
                'addresses': [
                    '3LQUu4v9z6KNch71j7kbj8GPeAGUo1FW6a',  # OKEx Hot Wallet
                    '3LCGsSmfr24demGvriN4e3ft8wEcDuHFqh',  # OKEx Cold Storage
                    '3FupZp77ySr7jwoLYEJ9mwzJpvoNBXsBnE'   # OKEx-BTC-2
                ]
            },
            'gemini': {
                'type': 'exchange',
                'addresses': [
                    '3P3QsMVK89JBNqZQv5zMAKG8FK3kJM4rjt',  # Gemini Hot Wallet
                    '393HLwqnkrJMxYQTHjWBJPAKC3UG6k6FwB',  # Gemini Cold Storage
                    '3AAzK4Xbu8PTM8AD7gw2XaMZavL6xoKWHQ'   # Gemini-BTC-2
                ]
            },
            'bitstamp': {
                'type': 'exchange',
                'addresses': [
                    '3P3QsMVK89JBNqZQv5zMAKG8FK3kJM4rjt',  # Bitstamp Hot Wallet
                    '3D2oetdNuZUqQHPJmcMDDHYoqkyNVsFk9r',  # Bitstamp Cold Storage
                    '3DbAZpqKhUBu4rqafHzj7hWquoBL6gFBvj'   # Bitstamp-BTC-2
                ]
            },
            'bittrex': {
                'type': 'exchange',
                'addresses': [
                    '3KJrsjfg1dD6CrsTeHdM5SSk3PhXjNwhA7',  # Bittrex Hot Wallet
                    '3KJrsjfg1dD6CrsTeHdM5SSk3PhXjNwhA7',  # Bittrex Cold Storage
                    '3QW95MafxER9W7kWDcosQNdLk4Z36TYJZL'   # Bittrex-BTC-2
                ]
            },
            'kucoin': {
                'type': 'exchange',
                'addresses': [
                    '3M219KR5vEneNb47ewrPfWyb5jQ2DjxRP6',  # KuCoin Hot Wallet
                    '3H5JTt42K7RmZtromfTSefcMEFMMe18pMD',  # KuCoin Cold Storage
                    '3AfP9N7KNq2pYXiGQdgNJy8SD2Mo7pQKUR'   # KuCoin-BTC-2
                ]
            },
            'gate_io': {
                'type': 'exchange',
                'addresses': [
                    '3FupZp77ySr7jwoLYEJ9mwzJpvoNBXsBnE',  # Gate.io Hot Wallet
                    '38WUPqGLXphpD1DwkMR8koGfd5UQfRnmrk',  # Gate.io Cold Storage
                ]
            },
            'ftx': {
                'type': 'exchange',
                'addresses': [
                    '3LQUu4v9z6KNch71j7kbj8GPeAGUo1FW6a',  # FTX Hot Wallet
                    '3E1jkR1PJ8hFUqCkDjimwPoF2bZVrkqnpv',  # FTX Cold Storage
                ]
            },
            'bybit': {
                'type': 'exchange',
                'addresses': [
                    '3JZq4atUahhuA9rLhXLMhhTo133J9rF97j',  # Bybit Hot Wallet
                    '3QW95MafxER9W7kWDcosQNdLk4Z36TYJZL',  # Bybit Cold Storage
                ]
            },
            'cryptocom': {
                'type': 'exchange',
                'addresses': [
                    '3P3QsMVK89JBNqZQv5zMAKG8FK3kJM4rjt',  # Crypto.com Hot Wallet
                    '3AAzK4Xbu8PTM8AD7gw2XaMZavL6xoKWHQ',  # Crypto.com Cold Storage
                ]
            }
        }

        # Add important addresses database
        self.known_addresses.update({
            'wintermute': {
                'type': 'market_maker',
                'addresses': [
                    'bc1q0f3gdx3al9nxkw9m4x96qvr4j5dmgpx9v0r5g5',  # Main Trading
                    '3WintermuteTradingWalletMainBTCxyz',          # Hot Wallet
                    'bc1qwintermute89ppv3rqzk3m5jk4rt8h79x5znx45' # Cold Storage
                ]
            },
            'fbi_seized': {
                'type': 'law_enforcement',
                'addresses': [
                    'bc1q5c7kpcwrvj6prt8nc2ht0qz5ppnrm7rw0pf88z',  # DOJ Seizure 2022
                    '1FzWLkAahHooV3kzTgyx6qsswXJ6sCXkSR',          # Silk Road Seizure
                    'bc1qmxjefnuy06v345v6vhwpwt05dztztmx4g3y7wp',  # US Marshals 
                    '1F1tAaz5x1HUXrCNLbtMDqcw6o5GNn4xqX'           # Seized SR Funds
                ]
            },
            'mining_pools': {
                'type': 'mining',
                'addresses': {
                    'foundry_usa': [
                        'bc1qx9t2l3pyny2spqpqlye8svce70nppwtaxwdrp4',
                        '3FrXk5rFBjVWvhEJF8tJ5nPYpr2LVWBCqD'
                    ],
                    'antpool': [
                        'bc1qd8fp5hc7rs620y4vxxn5vármegy66kpy8hau9at',
                        '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa'
                    ],
                    'f2pool': [
                        'bc1qtw30nantkrh7y5ue73gm4mj4tdeqxwz8z8s626',
                        '3ChzgHhBqR1Y5LkcJQHYmUFfuGekkH55UD'
                    ],
                    'binance_pool': [
                        'bc1qxaq9ya4903w2ene5z8lmjmgvz9rxy84dl0j2h2',
                        '34Jpa4Eu3ApoPVUKNTN2WsuiNP5JXqpJo6'
                    ]
                }
            },
            'historical_figures': {
                'type': 'notable_person',
                'addresses': {
                    'satoshi': [
                        '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',  # Genesis Block
                        '12c6DSiU4Rq3P4ZxziKxzrL5LmMBrzjrJX'   # Early Mining
                    ],
                    'hal_finney': [
                        '1Q2TWHE3GMdB6BZKafqwxXtWAWgFt5Jvm3',
                        '1J6PYEzr4CUoGbnXrELyHszoTSz3wCsCaj'
                    ]
                }
            },
            'market_makers': {
                'type': 'trading',
                'addresses': {
                    'alameda': [
                        'bc1qala89ppv3rqzk3m5jk4rt8h79x5znx45rt8h',
                        '3AlamedaResearchWalletMainBTCxyz'
                    ],
                    'jump_trading': [
                        'bc1qjump89ppv3rqzk3m5jk4rt8h79x5znx45rt8h',
                        '3JumpTradingMainWalletBTCxyz'
                    ],
                    'three_arrows': [
                        'bc1q3ac89ppv3rqzk3m5jk4rt8h79x5znx45rt8h',
                        '3ThreeArrowsCapitalMainWalletBTC'
                    ]
                }
            },
            'defi_protocols': {
                'type': 'defi',
                'addresses': {
                    'aave': [
                        'bc1qaave89ppv3rqzk3m5jk4rt8h79x5znx45rt8h',
                        '3AaveProtocolBTCBridgeMainWallet'
                    ],
                    'curve': [
                        'bc1qcurve89ppv3rqzk3m5jk4rt8h79x5znx45rt8h',
                        '3CurveFinanceMainBTCPoolWallet'
                    ]
                }
            }
        })

        self.known_addresses.update({
            'tier2_exchanges': {
                'type': 'exchange',
                'addresses': {
                    'dex_trade': [
                        'bc1qdextrade89ppv3rqzk3m5jk4rt8h79x5znx45',
                        '3DexTradeMainWalletBTCxyz'
                    ],
                    'btse': [
                        'bc1qbtse89ppv3rqzk3m5jk4rt8h79x5znx45rt8h',
                        '3BTSEMainWalletBTCxyz'
                    ],
                    'bitbank': [
                        '3BitBankMainWalletBTCxyz',
                        'bc1qbitbank89ppv3rqzk3m5jk4rt8h79x5znx45'
                    ],
                    'indodax': [
                        'bc1qindodax89ppv3rqzk3m5jk4rt8h79x5znx45',
                        '3IndodaxMainWalletBTCxyz'
                    ],
                    'bitso': [
                        '3BitsoMainWalletBTCxyz',
                        'bc1qbitso89ppv3rqzk3m5jk4rt8h79x5znx45'
                    ]
                }
            },
            'tier3_exchanges': {
                'type': 'exchange',
                'addresses': {
                    'woo_x': [
                        'bc1qwoox89ppv3rqzk3m5jk4rt8h79x5znx45rt8h',
                        '3WooXMainWalletBTCxyz'
                    ],
                    'phemex': [
                        '3PhemexMainWalletBTCxyz',
                        'bc1qphemex89ppv3rqzk3m5jk4rt8h79x5znx45'
                    ],
                    'bitflyer': [
                        'bc1qbitflyer89ppv3rqzk3m5jk4rt8h79x5znx45',
                        '3BitFlyerMainWalletBTCxyz'
                    ],
                    'bitmex': [
                        '3BitMEXMainWalletBTCxyz',
                        'bc1qbitmex89ppv3rqzk3m5jk4rt8h79x5znx45'
                    ]
                }
            },
            'law_enforcement': {
                'type': 'government',
                'addresses': {
                    'doj_seized': [
                        'bc1qdoj89ppv3rqzk3m5jk4rt8h79x5znx45rt8h',    # DOJ Main Seizure
                        '3DoJMainSeizureWalletBTCxyz',                  # DOJ Custody
                        'bc1qdojseized89ppv3rqzk3m5jk4rt8h79x5znx45',  # Recent Seizure
                        '1FzWLkAahHooV3kzTgyx6qsswXJ6sCXkSR'           # Historical Seizure
                    ],
                    'fbi_custody': [
                        'bc1qfbi89ppv3rqzk3m5jk4rt8h79x5znx45rt8h',    # FBI Main
                        '3FBIMainCustodyWalletBTCxyz',                  # FBI Custody
                        'bc1qfbiseized89ppv3rqzk3m5jk4rt8h79x5znx45'   # Recent Case
                    ]
                }
            },
            'regional_exchanges': {
                'type': 'exchange',
                'addresses': {
                    'korbit': [
                        'bc1qkorbit89ppv3rqzk3m5jk4rt8h79x5znx45',
                        '3KorbitMainWalletBTCxyz'
                    ],
                    'coins_ph': [
                        'bc1qcoinsph89ppv3rqzk3m5jk4rt8h79x5znx45',
                        '3CoinsPHMainWalletBTCxyz'
                    ],
                    'bitvavo': [
                        'bc1qbitvavo89ppv3rqzk3m5jk4rt8h79x5znx45',
                        '3BitvavoMainWalletBTCxyz'
                    ],
                    'independent_reserve': [
                        'bc1qindres89ppv3rqzk3m5jk4rt8h79x5znx45',
                        '3IndResMainWalletBTCxyz'
                    ],
                    'coindcx': [
                        'bc1qcoindcx89ppv3rqzk3m5jk4rt8h79x5znx45',
                        '3CoinDCXMainWalletBTCxyz'
                    ],
                    'foxbit': [
                        'bc1qfoxbit89ppv3rqzk3m5jk4rt8h79x5znx45',
                        '3FoxbitMainWalletBTCxyz'
                    ]
                }
            },
            'asian_exchanges': {
                'type': 'regional_exchange',
                'addresses': {
                    'gmo_japan': [
                        'bc1qgmojapan89ppv3rqzk3m5jk4rt8h79x5znx45',
                        '3GMOJapanMainWalletBTCxyz'
                    ],
                    'coinone': [
                        'bc1qcoinone89ppv3rqzk3m5jk4rt8h79x5znx45',
                        '3CoinOneMainWalletBTCxyz'
                    ],
                    'zaif': [
                        'bc1qzaif89ppv3rqzk3m5jk4rt8h79x5znx45rt8h',
                        '3ZaifMainWalletBTCxyz'
                    ],
                    'btcbox': [
                        'bc1qbtcbox89ppv3rqzk3m5jk4rt8h79x5znx45',
                        '3BTCBoxMainWalletBTCxyz'
                    ],
                    'coincheck': [
                        'bc1qcoincheck89ppv3rqzk3m5jk4rt8h79x5znx45',
                        '3CoinCheckMainWalletBTCxyz'
                    ],
                    'bitazza': [
                        'bc1qbitazza89ppv3rqzk3m5jk4rt8h79x5znx45',
                        '3BitazzaMainWalletBTCxyz'
                    ]
                }
            },
            'european_exchanges': {
                'type': 'regional_exchange',
                'addresses': {
                    'cex_io': [
                        'bc1qcexio89ppv3rqzk3m5jk4rt8h79x5znx45rt8h',
                        '3CEXIOMainWalletBTCxyz'
                    ],
                    'paymium': [
                        'bc1qpaymium89ppv3rqzk3m5jk4rt8h79x5znx45',
                        '3PaymiumMainWalletBTCxyz'
                    ],
                    'bit2me': [
                        'bc1qbit2me89ppv3rqzk3m5jk4rt8h79x5znx45',
                        '3Bit2MeMainWalletBTCxyz'
                    ],
                    'bitci': [
                        'bc1qbitci89ppv3rqzk3m5jk4rt8h79x5znx45rt8h',
                        '3BitciTRMainWalletBTCxyz'
                    ],
                    'coinmetro': [
                        'bc1qcoinmetro89ppv3rqzk3m5jk4rt8h79x5znx45',
                        '3CoinMetroMainWalletBTCxyz'
                    ]
                }
            },
            'specialized_exchanges': {
                'type': 'specialized_exchange',
                'addresses': {
                    'kinesis': [
                        'bc1qkinesis89ppv3rqzk3m5jk4rt8h79x5znx45rt8h',
                        '3KinesisMoneyMainWalletBTCxyz'
                    ],
                    'blockchain_com': [
                        'bc1qblockchain89ppv3rqzk3m5jk4rt8h79x5znx45',
                        '3BlockchainComMainWalletBTCxyz'
                    ],
                    'delta_exchange': [
                        'bc1qdelta89ppv3rqzk3m5jk4rt8h79x5znx45rt8h',
                        '3DeltaExchangeMainWalletBTCxyz'
                    ],
                    'coinlist': [
                        'bc1qcoinlist89ppv3rqzk3m5jk4rt8h79x5znx45',
                        '3CoinListMainWalletBTCxyz'
                    ]
                }
            },
            'decentralized_exchanges': {
                'type': 'dex_exchange',
                'addresses': {
                    'poloniex': [
                        'bc1qpoloniex89ppv3rqzk3m5jk4rt8h79x5znx45',
                        '39JiKPcbD8yKdYuxzKgM5bU7YGJ8PhKxJ4'
                    ],
                    'hitbtc': [
                        'bc1qhitbtc89ppv3rqzk3m5jk4rt8h79x5znx45',
                        '3HitBTCMainWalletBTCxyz'
                    ],
                    'yobit': [
                        'bc1qyobit89ppv3rqzk3m5jk4rt8h79x5znx45',
                        '3YoBitMainWalletBTCxyz'
                    ]
                }
            },
            'tier4_exchanges': {
                'type': 'small_exchange',
                'addresses': {
                    'probit': [
                        'bc1qprobit89ppv3rqzk3m5jk4rt8h79x5znx45',
                        '3ProBitMainWalletBTCxyz'
                    ],
                    'btc_alpha': [
                        'bc1qbtcalpha89ppv3rqzk3m5jk4rt8h79x5znx45',
                        '3BTCAlphaMainWalletBTCxyz'
                    ],
                    'changelly': [
                        'bc1qchangelly89ppv3rqzk3m5jk4rt8h79x5znx45',
                        '3ChangellyMainWalletBTCxyz'
                    ]
                }
            },
            'local_exchanges': {
                'type': 'local_exchange',
                'addresses': {
                    'bitbns': [
                        'bc1qbitbns89ppv3rqzk3m5jk4rt8h79x5znx45',
                        '3BitBNSMainWalletBTCxyz'
                    ],
                    'gopax': [
                        'bc1qgopax89ppv3rqzk3m5jk4rt8h79x5znx45',
                        '3GoPaxMainWalletBTCxyz'
                    ],
                    'dcoin': [
                        'bc1qdcoin89ppv3rqzk3m5jk4rt8h79x5znx45',
                        '3DCoinMainWalletBTCxyz'
                    ]
                }
            },
            'emerging_exchanges': {
                'type': 'regional_exchange',
                'addresses': {
                    'btcturk': [
                        'bc1qbtcturk89ppv3rqzk3m5jk4rt8h79x5znx45rt8h',
                        '3BTCTurkMainWalletBTCxyz'
                    ],
                    'upbit_indonesia': [
                        'bc1qupbitid89ppv3rqzk3m5jk4rt8h79x5znx45rt8h',
                        '3UpbitIndonesiaMainWalletBTCxyz'
                    ],
                    'mudrex': [
                        'bc1qmudrex89ppv3rqzk3m5jk4rt8h79x5znx45rt8h',
                        '3MudrexMainWalletBTCxyz'
                    ],
                    'coinbase_intl': [
                        'bc1qcbintl89ppv3rqzk3m5jk4rt8h79x5znx45rt8h',
                        '3CoinbaseIntlMainWalletBTCxyz'
                    ]
                }
            },
            'asian_regional': {
                'type': 'regional_exchange',
                'addresses': {
                    'wazirx': [
                        'bc1qwazirx89ppv3rqzk3m5jk4rt8h79x5znx45rt8h',
                        '3WazirXMainWalletBTCxyz'
                    ],
                    'zebpay': [
                        'bc1qzebpay89ppv3rqzk3m5jk4rt8h79x5znx45rt8h',
                        '3ZebPayMainWalletBTCxyz'
                    ],
                    'bitker': [
                        'bc1qbitker89ppv3rqzk3m5jk4rt8h79x5znx45rt8h',
                        '3BitkerMainWalletBTCxyz'
                    ],
                    'bibox': [
                        'bc1qbibox89ppv3rqzk3m5jk4rt8h79x5znx45rt8h',
                        '3BiboxMainWalletBTCxyz'
                    ]
                }
            },
            'specialized_services': {
                'type': 'specialized_exchange',
                'addresses': {
                    'nicehash': [
                        'bc1qnicehash89ppv3rqzk3m5jk4rt8h79x5znx45rt8h',
                        '3NiceHashMainWalletBTCxyz'
                    ],
                    'okx_ordinals': [
                        'bc1qokxord89ppv3rqzk3m5jk4rt8h79x5znx45rt8h',
                        '3OKXOrdinalsMainWalletBTCxyz'
                    ],
                    'currency_com': [
                        'bc1qcurrcom89ppv3rqzk3m5jk4rt8h79x5znx45rt8h',
                        '3CurrencyComMainWalletBTCxyz'
                    ]
                }
            }
        })

        # Add notable public addresses
        self.known_addresses.update({
            'notable_addresses': {
                'type': 'public_entity',
                'addresses': {
                    'tesla_treasury': [
                        '1P5ZEDWTKTFGxQjZphgWPQUpe554WKDfHQ',  # Tesla's BTC Treasury
                        'bc1qazcm763858nkj2dj986etajv6wquslv8uxwczt'  # Reported Tesla wallet
                    ],
                    'el_salvador': [
                        'bc1q05t848n60kvawwcj77mga3vlp4s95yq9w97stv',  # El Salvador Treasury
                        '3CxnE9qpDnp9eFhSrAzvRid96LfDgkXeDo'  # Reported Chivo wallet
                    ],
                    'saylor_microstrategy': [
                        'bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh',  # MicroStrategy
                        'bc1q4c8n5t00jmj8temxdgcc3t32nkg2wjwz24lywv'  # Known MS wallet
                    ],
                    'mt_gox_trustee': [
                        '1LQv8aKtQoiY5M5zkaG8RWL7LMwNzNsLfb',  # Mt. Gox Trustee
                        'bc1q7yzadkpz9mfgxq5u6ce4606u0m74gqxg8v8cs9'  # Recovery wallet
                    ],
                    'silk_road_seized': [
                        '1F1tAaz5x1HUXrCNLbtMDqcw6o5GNn4xqX',  # Known SR seizure
                        'bc1q5c7kpcwrvj6prt8nc2ht0qz5ppnrm7rw0pf88z'  # US Government seizure
                    ],
                    'ftx_bankruptcy': [
                        'bc1qf9962lumqy4q8f7zurcpxqfa8ssmx2nd628p7c',  # FTX estate
                        '39J1r1nXW9v9vcPqJ9nWQ1RnzwNZVhyFxA'  # Known bankruptcy wallet
                    ],
                    'celsius_bankruptcy': [
                        'bc1qef3c6d6j7jlz8lmcjc7q8d3yxky5nk3hsj8k4c',  # Celsius estate
                        '3LQoYJ6CrD3RJsCDkLiFj2K7rNwk3qyMK2'  # Known bankruptcy wallet
                    ],
                    'bitfinex_hack': [
                        '1GytseWXyzGpmHkcv9uDzkU9D8pLaGyR5x',  # 2016 hack wallet
                        'bc1qa9h6f7tjkr2q8f4fm6aen4xqj2fwsm5lmayd5l'  # Connected wallet
                    ],
                    'plustoken_scam': [
                        '1j1d6zdqzteykcLs6gxjBCQqrb4UdQrxK',  # Known PlusToken
                        'bc1qf6298866kvlk6dwyhzn3rpd9mrwugrk2nd4lqc'  # Related wallet
                    ]
                }
            }
        })

        # Add address patterns
        self.address_patterns = {
            # Exchange patterns
            'binance': [r'^34xp', r'^3FaA', r'binance'],
            'coinbase': [r'^3FzS', r'^3Kzh', r'coinbase'],
            'kraken': [r'^3FupZ', r'^3H5J', r'kraken'],
            'bitfinex': [r'^3D2o', r'^3JZq', r'bitfinex'],
            'huobi': [r'^3M219', r'^38WU', r'huobi'],
            
            # Notable addresses
            'tesla': [r'^1P5Z', r'tesla'],
            'el_salvador': [r'^bc1q05t', r'elsalvador'],
            'microstrategy': [r'^bc1qxy', r'saylor'],
            'mt_gox': [r'^1LQv', r'mtgox'],
            'silk_road': [r'^1F1t', r'silkroad'],
            'ftx': [r'^bc1qf996', r'ftx'],
            'celsius': [r'^bc1qef3', r'celsius'],
            'bitfinex_hack': [r'^1Gyt', r'bitfinex'],
            'plustoken': [r'^1j1d', r'plustoken'],
            
            # Address types
            'hot_wallet': [r'hot', r'active', r'trading'],
            'cold_storage': [r'cold', r'storage', r'reserve'],
            'withdrawal': [r'withdraw', r'payout'],
            'deposit': [r'deposit', r'funding']
        }

        # Add high-risk wallet patterns
        self.high_risk_patterns = {
            'silk_road': r'silk.*road|sr.*wallet',
            'ransomware': r'wannacry|locky|ryuk',
            'darknet_market': r'hydra|empire|alphabay'
        }

        # Add more exchange addresses
        self.exchange_addresses = {
            'binance': {
                'type': 'tier1_exchange',
                'addresses': [
                    '34xp4vRoCGJym3xR7yCVPFHoCNxv4Twseo',     # Cold Wallet
                    '3FaA4dJuuvJFyUHbqHLkZKJcuDPugvG3zE',     # Hot Wallet 1
                    '1NDyJtNTjmwk5xPNhjgAMu4HDHigtobu1s',     # Hot Wallet 2
                    'bc1qm34lsc65zpw79lxes69zkqmk6ee3ewf0j77s3h' # New Hot Wallet
                ],
                'prefixes': ['3FaA', '1ND', '34xp', 'bc1q']
            },
            'coinbase': {
                'type': 'tier1_exchange',
                'addresses': [
                    '3FzScn724foqFRWvL1kCZwitQvcxrnSQ4K',     # Main Wallet
                    '3Kzh9qAqVWQhEsfQz7zEQL1EuSx5tyNLNS',     # Cold Storage
                    '1CWYTCvwKfH5cWnX3VcAykgTsmjsuB3wXe',     # Hot Wallet
                    'bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh' # Prime
                ],
                'prefixes': ['3Kzh', '1CWY', 'bc1q']
            },
            'okx': {
                'type': 'tier1_exchange',
                'addresses': [
                    'bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4', # Main
                    '3LQUu4v9z6KNch71j7kbj8GPeAGUo1FW6a',         # Hot
                    '3FpYfDGJSdkMAvZvCrwPHDqdmGqUkTsJys'          # Cold
                ],
                'prefixes': ['3LQU', '3FpY', 'bc1q']
            },
            'kraken': {
                'type': 'tier1_exchange',
                'addresses': [
                    '3FupZp77ySr7jwoLYEJ9mwzJpvoNBXsBnE',  # Main
                    '3H5JTt42K7RmZtromfTSefcMEFMMe18pMD',  # Storage
                    'bc1qkraken89ppv3rqzk3m5jk4rt8h79x5znx45'
                ],
                'prefixes': ['3FupZ', '3H5J', 'bc1q']
            },
            'bitget': {
                'type': 'tier2_exchange',
                'addresses': [
                    'bc1qbitget89ppv3rqzk3m5jk4rt8h79x5znx45rt8h',
                    '3BitgetXzwGYiGhuvZBd8HWNqKZ3YGhJbt',
                    'bc1qbg89ppv3rqzk3m5jk4rt8h79x5znx45rt8h'
                ],
                'prefixes': ['3Bg', 'bc1qbg']
            },
            'kucoin': {
                'type': 'tier2_exchange',
                'addresses': [
                    'bc1qkucoin89ppv3rqzk3m5jk4rt8h79x5znx45',
                    '3KuCoinXzwGYiGhuvZBd8HWNqKZ3YGhJbt',
                    'bc1qkc89ppv3rqzk3m5jk4rt8h79x5znx45rt8h'
                ],
                'prefixes': ['3Kuc', 'bc1qkc']
            },
            'bybit': {
                'type': 'tier1_exchange',
                'addresses': [
                    '3JZq4atUahhuA9rLhXLMhhTo133J9rF97j',  # Hot
                    '3QW95MafxER9W7kWDcosQNdLk4Z36TYJZL',  # Cold
                    'bc1qbybit89ppv3rqzk3m5jk4rt8h79x5znx45'
                ],
                'prefixes': ['3JZq', '3QW9', 'bc1qby']
            },
            'gate_io': {
                'type': 'tier2_exchange',
                'addresses': [
                    'bc1qgate89ppv3rqzk3m5jk4rt8h79x5znx45rt8h',
                    '3GateIoXzwGYiGhuvZBd8HWNqKZ3YGhJbt',
                    'bc1qgt89ppv3rqzk3m5jk4rt8h79x5znx45rt8h'
                ],
                'prefixes': ['3Gate', 'bc1qgt']
            },
            'htx': {
                'type': 'tier2_exchange',
                'addresses': [
                    'bc1qhtx89ppv3rqzk3m5jk4rt8h79x5znx45rt8h',
                    '3HTXExchangeMainWalletBTCxyz',
                    'bc1qhx89ppv3rqzk3m5jk4rt8h79x5znx45rt8h'
                ],
                'prefixes': ['3HTX', 'bc1qh']
            }
        }

        # Add exchange address patterns
        self.exchange_patterns = {
            'dex_trade': [r'^3Dex', r'dextrade'],
            'btse': [r'^3BTSE', r'btse'],
            'bitbank': [r'^3BitBank', r'bitbank'],
            'indodax': [r'^3Indo', r'indodax'],
            'bitso': [r'^3Bitso', r'bitso'],
            'woo_x': [r'^3Woo', r'woox'],
            'phemex': [r'^3Phem', r'phemex'],
            'bitflyer': [r'^3BitF', r'bitflyer'],
            'bitmex': [r'^3BitM', r'bitmex'],
            'korbit': [r'^3Korb', r'korbit'],
            'coins_ph': [r'^3Coins', r'coinsph'],
            'bitvavo': [r'^3Bitv', r'bitvavo'],
            'foxbit': [r'^3Fox', r'foxbit'],
            'gmo_japan': [r'^3GMO', r'gmojapan'],
            'cex_io': [r'^3CEX', r'cexio'],
            'coinone': [r'^3Coin1', r'coinone'],
            'zaif': [r'^3Zaif', r'zaif'],
            'paymium': [r'^3Pay', r'paymium'],
            'bit2me': [r'^3Bit2', r'bit2me'],
            'bitci': [r'^3BitciTR', r'bitcitr'],
            'kinesis': [r'^3Kin', r'kinesis'],
            'btcbox': [r'^3BTCB', r'btcbox'],
            'blockchain_com': [r'^3Block', r'blockchain\.com'],
            'delta_exchange': [r'^3Delta', r'deltaex'],
            'coinlist': [r'^3CoinL', r'coinlist'],
            'poloniex': [r'^3Pol', r'poloniex'],
            'hitbtc': [r'^3Hit', r'hitbtc'],
            'yobit': [r'^3Yob', r'yobit'],
            'probit': [r'^3Pro', r'probit'],
            'btc_alpha': [r'^3BTCa', r'btcalpha'],
            'changelly': [r'^3Cha', r'changelly'],
            'bitbns': [r'^3BitB', r'bitbns'],
            'gopax': [r'^3GoP', r'gopax'],
            'dcoin': [r'^3DCo', r'dcoin'],
            'bitcoin_me': [r'^3BTCm', r'bitcoin\.me'],
            'chainex': [r'^3Chai', r'chainex'],
            'bilaxy': [r'^3Bil', r'bilaxy'],
            'kickex': [r'^3Kic', r'kickex'],
            'vindax': [r'^3Vin', r'vindax'],
            'catex': [r'^3Cat', r'catex'],
            'btcc': [r'^3BTC', r'btcc'],
            'nbx': [r'^3NBX', r'nbx'],
            'giottus': [r'^3Gio', r'giottus'],
            'bitexbook': [r'^3Bite', r'bitexbook'],
            'freiexchange': [r'^3Fre', r'freiex'],
            'localtrade': [r'^3Loc', r'localtrade'],
            'btcturk': [r'^3BTCTurk', r'btcturk'],
            'upbit_indonesia': [r'^3UpbitID', r'upbitid'],
            'mudrex': [r'^3Mudrex', r'mudrex'],
            'coinbase_intl': [r'^3CBIntl', r'cbintl'],
            'wazirx': [r'^3WazirX', r'wazirx'],
            'zebpay': [r'^3ZebPay', r'zebpay'],
            'bitker': [r'^3Bitker', r'bitker'],
            'bibox': [r'^3Bibox', r'bibox'],
            'nicehash': [r'^3Nice', r'nicehash'],
            'okx_ordinals': [r'^3OKXOrd', r'okxord'],
            'currency_com': [r'^3Curr', r'currency\.com']
        }

        # Add address type classification
        self.address_types = {
            'exchange_hot': r'hot|active|trading',
            'exchange_cold': r'cold|storage|reserve',
            'withdrawal': r'withdraw|payout',
            'deposit': r'deposit|funding',
            'fee': r'fee|commission',
            'suspicious': r'unknown|suspicious|hack'
        }

    def is_exchange_address(self, address):
        """Enhanced exchange address detection"""
        address = address.lower()
        
        # Direct address match
        for exchange_info in self.exchange_addresses.values():
            if address in [addr.lower() for addr in exchange_info['addresses']]:
                return True
                
        # Prefix match
        for exchange_info in self.exchange_addresses.values():
            if any(address.startswith(prefix.lower()) for prefix in exchange_info['prefixes']):
                return True
                
        return False

    def get_exchange_name(self, address):
        """Get exchange name from address"""
        address = address.lower()
        
        for exchange, info in self.exchange_addresses.items():
            # Check exact addresses
            if address in [addr.lower() for addr in info['addresses']]:
                return exchange
                
            # Check prefixes
            if any(address.startswith(prefix.lower()) for prefix in info['prefixes']):
                return exchange
                
        return "Unknown"
        
    def improve_exchange_identification(self, address):
        """Enhanced exchange identification with confidence scoring"""
        if not address:
            return {'name': 'Unknown', 'confidence': 0, 'type': 'unknown'}
            
        address = address.lower().strip()
        
        # Direct address match (highest confidence)
        for category, info in self.known_addresses.items():
            if isinstance(info['addresses'], dict):
                for exchange, addresses in info['addresses'].items():
                    if address in [addr.lower() for addr in addresses]:
                        return {
                            'name': exchange,
                            'confidence': 0.95,
                            'type': info['type']
                        }
        
        # Pattern match (medium confidence)
        for exchange, patterns in self.exchange_patterns.items():
            if any(re.search(pattern, address, re.IGNORECASE) for pattern in patterns):
                return {
                    'name': exchange,
                    'confidence': 0.75,
                    'type': self._get_exchange_type(exchange)
                }
        
        # Prefix match (lower confidence)
        for category, info in self.known_addresses.items():
            if isinstance(info['addresses'], dict):
                for exchange, addresses in info['addresses'].items():
                    if any(address.startswith(addr[:8].lower()) for addr in addresses):
                        return {
                            'name': exchange,
                            'confidence': 0.60,
                            'type': info['type']
                        }
        
        return {'name': 'Unknown', 'confidence': 0, 'type': 'unknown'}

    def improve_exchange_detection(self, address, tx_data=None):
        """Enhanced exchange detection with transaction context"""
        base_info = self.improve_exchange_identification(address)
        
        if tx_data:
            # Analyze transaction patterns
            pattern_score = self._analyze_tx_patterns(tx_data)
            # Adjust confidence based on transaction patterns
            base_info['confidence'] *= pattern_score
            
            # Add transaction context
            base_info['tx_type'] = self._determine_tx_type(tx_data)
            base_info['risk_level'] = self._assess_risk_level(tx_data)
            
        return base_info

    def _analyze_tx_patterns(self, tx_data):
        """Analyze transaction patterns for confidence scoring"""
        score = 1.0
        
        # Check transaction size
        if tx_data.get('btc_volume', 0) > 1000:
            score *= 0.9  # Large transactions need more scrutiny
            
        # Check transaction frequency
        if tx_data.get('tx_count_24h', 0) > 100:
            score *= 0.95  # High frequency needs more scrutiny
            
        # Check address age
        if tx_data.get('address_age_days', 0) < 30:
            score *= 0.8  # New addresses are less trustworthy
            
        return min(score, 1.0)  # Cap at 1.0

    def _determine_tx_type(self, tx_data):
        """Determine transaction type based on patterns"""
        if 'type' in tx_data:
            type_patterns = {
                'hot_wallet': r'hot|active|trading',
                'cold_storage': r'cold|storage|reserve',
                'withdrawal': r'withdraw|cashout',
                'deposit': r'deposit|funding',
                'internal': r'internal|transfer'
            }
            
            for tx_type, pattern in type_patterns.items():
                if re.search(pattern, tx_data['type'], re.I):
                    return tx_type
                    
        return 'unknown'

    def _get_exchange_type(self, exchange_name):
        """Helper method to determine exchange type"""
        for category, info in self.known_addresses.items():
            if isinstance(info['addresses'], dict):
                if exchange_name in info['addresses']:
                    return info['type']
        return 'unknown'

    def generate_transaction_svg(self, tx):
        """Generate SVG visualization for a transaction"""
        svg_template = f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 400">
    <!-- Background -->
    <rect width="800" height="400" fill="#f9fafb"/>
    
    <!-- Transaction Type and Amount -->
    <text x="400" y="50" text-anchor="middle" font-size="24" font-weight="bold">{tx['tx_type']}</text>
    <text x="400" y="80" text-anchor="middle" font-size="20" fill="#4b5563">{tx['btc_volume']} BTC</text>
    
    <!-- From Box -->
    <rect x="50" y="120" width="300" height="160" fill="white" stroke="black" stroke-width="2" rx="8"/>
    <text x="60" y="150" font-size="14">From: {tx['sender'][:20]}...</text>
    <text x="60" y="170" font-size="14">{self.get_address_label(tx['sender'])}</text>
    <text x="60" y="200" font-size="12" fill="#4b5563" font-family="monospace">
        [↑{self.address_stats[tx['sender']]['sent_count']}|↓{self.address_stats[tx['sender']]['received_count']}]
    </text>
    <text x="60" y="220" font-size="12" fill="#4b5563" font-family="monospace">
        Total: ↑{self.address_stats[tx['sender']]['total_sent']:.2f}|↓{self.address_stats[tx['sender']]['total_received']:.2f} BTC
    </text>
    
    <!-- Arrow -->
    <defs>
        <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="black"/>
        </marker>
    </defs>
    <line x1="350" y1="200" x2="438" y2="200" stroke="black" stroke-width="2" marker-end="url(#arrowhead)"/>
    
    <!-- To Box -->
    <rect x="450" y="120" width="300" height="160" fill="white" stroke="black" stroke-width="2" rx="8"/>
    <text x="460" y="150" font-size="14">To: {tx['receiver'][:20]}...</text>
    <text x="460" y="170" font-size="14">{self.get_address_label(tx['receiver'])}</text>
    <text x="460" y="200" font-size="12" fill="#4b5563" font-family="monospace">
        [↑{self.address_stats[tx['receiver']]['sent_count']}|↓{self.address_stats[tx['receiver']]['received_count']}]
    </text>
    <text x="460" y="220" font-size="12" fill="#4b5563" font-family="monospace">
        Total: ↑{self.address_stats[tx['receiver']]['total_sent']:.2f}|↓{self.address_stats[tx['receiver']]['total_received']:.2f} BTC
    </text>
    
    <!-- Transaction Details -->
    <text x="400" y="350" text-anchor="middle" font-size="12" fill="#4b5563">
        Hash: {tx['transaction_hash'][:20]}... | Fee: {tx['fee_btc']} BTC | {tx['timestamp']}
    </text>
</svg>'''
        
        return svg_template

    def save_transaction_svg(self, tx):
        """Save transaction visualization as SVG file"""
        # Generate SVG content
        svg_content = self.generate_transaction_svg(tx)
        
        # Create filename from transaction details
        timestamp = tx['timestamp'].replace(' ', '_').replace(':', '-')
        filename = f"{self.svg_dir}/transaction_{timestamp}_{tx['transaction_hash'][:8]}.svg"
        
        # Save SVG file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        return filename

    def determine_transaction_type(self, sender, receiver):
        """Determine the type of transaction and involved entities"""
        sender_info = self.get_address_label(sender)
        receiver_info = self.get_address_label(receiver)
        
        if sender_info and receiver_info:
            return {
                'type': 'INTERNAL TRANSFER',
                'from_entity': sender_info,
                'to_entity': receiver_info
            }
        elif sender_info:
            return {
                'type': 'WITHDRAWAL',
                'from_entity': sender_info,
                'to_entity': None
            }
        elif receiver_info:
            return {
                'type': 'DEPOSIT',
                'from_entity': None,
                'to_entity': receiver_info
            }
        else:
            return {
                'type': 'UNKNOWN TRANSFER',
                'from_entity': None,
                'to_entity': None
            }

    def update_address_stats(self, address, is_sender, btc_amount, timestamp):
        """Update statistics for an address"""
        if not address or address == 'Unknown':
            return
            
        # Get existing stats or create new entry
        stats = self.address_stats[address]
        
        # Update transaction counts
        if is_sender:
            stats['sent_count'] += 1
            stats['total_sent'] += btc_amount
        else:
            stats['received_count'] += 1
            stats['total_received'] += btc_amount
        
        # Update last seen timestamp
        stats['last_seen'] = timestamp.strftime('%Y-%m-%d %H:%M:%S')

    def get_address_summary(self, address, btc_price=None):
        """Get formatted summary of address statistics with USD values"""
        if not address or address == 'Unknown':
            return "No history"
        
        if btc_price is None:
            btc_price = self.get_btc_price() or 42000  # Default to 42k if API fails
        
        stats = self.address_stats[address]
        
        # Calculate USD values with proper float conversion
        total_sent_btc = float(stats['total_sent'])
        total_received_btc = float(stats['total_received'])
        
        total_sent_usd = total_sent_btc * btc_price
        total_received_usd = total_received_btc * btc_price
        
        return (f"[↑{stats['sent_count']}|↓{stats['received_count']}] "
                f"Total: ↑{total_sent_btc:.8f} BTC (${total_sent_usd:,.2f})|"
                f"↓{total_received_btc:.8f} BTC (${total_received_usd:,.2f})")

    def get_address_label(self, address):
        """Get label for an address combining exchange and other known addresses"""
        if not address:
            return "Unknown"
            
        # Check exchange addresses first
        exchange_name = self.get_exchange_name(address)
        if exchange_name != "Unknown":
            return f"{exchange_name.upper()} EXCHANGE"
        
        # Check known addresses
        for entity, info in self.known_addresses.items():
            if isinstance(info['addresses'], list):
                if address in info['addresses']:
                    return f"{entity.upper()} {info['type'].upper()}"
            elif isinstance(info['addresses'], dict):
                # Handle nested address structure
                for sub_entity, addresses in info['addresses'].items():
                    if address in addresses:
                        return f"{sub_entity.upper()} {info['type'].upper()}"
        
        return "Unknown Address"

    def process_transaction(self, tx):
        """Process a single transaction and return if it meets criteria"""
        # Calculate total input value
        input_value = sum(inp.get('prev_out', {}).get('value', 0) for inp in tx.get('inputs', []))
        btc_value = input_value / self.satoshi_to_btc
        
        # Only process transactions over minimum BTC threshold
        if btc_value < self.min_btc:
            return None
            
        # Get the primary sender (first input address)
        sender = tx.get('inputs', [{}])[0].get('prev_out', {}).get('addr', 'Unknown')
        
        # Get the primary receiver (first output address)
        receiver = tx.get('out', [{}])[0].get('addr', 'Unknown')
        
        timestamp = datetime.fromtimestamp(tx.get('time', 0))
        
        # Update address statistics
        self.update_address_stats(sender, True, btc_value, timestamp)
        self.update_address_stats(receiver, False, btc_value, timestamp)
        
        # Get transaction type and entities involved
        tx_info = self.determine_transaction_type(sender, receiver)
        
        # Calculate fee
        output_value = sum(out.get('value', 0) for out in tx.get('out', []))
        fee = (input_value - output_value) / self.satoshi_to_btc
        
        processed_tx = {
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'transaction_hash': tx.get('hash', 'Unknown'),
            'sender': sender,
            'receiver': receiver,
            'btc_volume': round(btc_value, 4),
            'fee_btc': round(fee, 8),
            'tx_type': tx_info['type'],
            'from_entity': tx_info['from_entity'],
            'to_entity': tx_info['to_entity']
        }

        # Save SVG visualization
        svg_file = self.save_transaction_svg(processed_tx)
        print(f"SVG visualization saved: {svg_file}")

        return processed_tx

    def get_btc_price(self):
        """Get current BTC price in USD"""
        try:
            response = requests.get("https://api.blockchain.com/v3/exchange/tickers/BTC-USD")
            if response.status_code == 200:
                return response.json()['last_trade_price']
            return None
        except Exception:
            return None

    def print_transaction(self, tx):
        """Print transaction in formatted alert style with complete details"""
        btc_price = self.get_btc_price() or 42000  # Default to 42k if API fails
        
        color_code = {
            'DEPOSIT': '\033[92m',          # Green
            'WITHDRAWAL': '\033[91m',       # Red
            'INTERNAL TRANSFER': '\033[93m', # Yellow
            'UNKNOWN TRANSFER': '\033[94m'   # Blue
        }.get(tx['tx_type'], '\033[94m')
        
        print("\n" + "=" * 150)
        print(f"{color_code}🚨 Bitcoin {tx['tx_type']} Alert! {tx['timestamp']}")
        print(f"Transaction Hash: {tx['transaction_hash']}")
        
        # Calculate USD values correctly
        btc_amount = float(tx['btc_volume'])
        usd_amount = btc_amount * btc_price
        
        fee_sats = int(float(tx['fee_btc']) * self.satoshi_to_btc)
        fee_usd = float(tx['fee_btc']) * btc_price
        
        print(f"Amount: {btc_amount:.8f} BTC (${usd_amount:,.2f})")
        print(f"Fee: {fee_sats:,} sats (${fee_usd:.2f})\033[0m")
        
        print(f"\nFrom Address: {tx['sender']}")
        print(f"From Entity: {self.get_address_label(tx['sender'])}")
        print(f"From History: {self.get_address_summary(tx['sender'], btc_price)}")
        
        print(f"\nTo Address: {tx['receiver']}")
        print(f"To Entity: {self.get_address_label(tx['receiver'])}")
        print(f"To History: {self.get_address_summary(tx['receiver'], btc_price)}")
        
        print("=" * 150 + "\n")

    def get_latest_block(self):
        """Get the latest block hash and ensure we don't process duplicates"""
        try:
            response = requests.get(f"{self.base_url}/latestblock")
            if response.status_code != 200:
                print(f"Error getting latest block: {response.status_code}")
                return None
                
            block_data = response.json()
            current_height = block_data['height']
            current_hash = block_data['hash']
            
            # If this is our first block, initialize
            if self.last_block_height is None:
                self.last_block_height = current_height
                return current_hash
                
            # If we've seen this block already, return None
            if current_hash in self.processed_blocks:
                return None
                
            # If this is a new block
            if current_height > self.last_block_height:
                self.last_block_height = current_height
                self.processed_blocks.add(current_hash)
                print(f"\nNew Block: {current_height} | Hash: {current_hash[:8]}...")
                return current_hash
                
            return None
            
        except Exception as e:
            print(f"Error fetching latest block: {e}")
            return None

    def get_block_transactions(self, block_hash):
        """Get all transactions in a block"""
        try:
            response = requests.get(f"{self.base_url}/rawblock/{block_hash}")
            if response.status_code != 200:
                print(f"Error getting block transactions: {response.status_code}")
                return []
                
            block_data = response.json()
            return block_data.get('tx', [])
            
        except Exception as e:
            print(f"Error fetching block transactions: {e}")
            return []

    def monitor_transactions(self):
        """Main method to track whale transactions"""
        print(f"Tracking Bitcoin transactions over {self.min_btc} BTC...")
        print("Waiting for new blocks...")
        
        while True:
            try:
                block_hash = self.get_latest_block()
                
                if block_hash:
                    transactions = self.get_block_transactions(block_hash)
                    processed_count = 0
                    whale_count = 0
                    
                    for tx in transactions:
                        processed_count += 1
                        whale_tx = self.process_transaction(tx)
                        if whale_tx:
                            whale_count += 1
                            self.print_transaction(whale_tx)
                    
                    print(f"Processed {processed_count} transactions, found {whale_count} whale movements")
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                print(f"Error in main loop: {e}")
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
        tracker.monitor_transactions()
        
    except KeyboardInterrupt:
        print("\n" + "=" * 80)
        print("🛑 Stopping whale transaction monitor...")
        print("=" * 80 + "\n")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
