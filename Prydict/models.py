from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()

class TransactionType(enum.Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"
    UNKNOWN = "unknown"

class WhaleTransaction(Base):
    __tablename__ = 'whale_transactions'
    
    id = Column(Integer, primary_key=True)
    transaction_hash = Column(String(64), unique=True, nullable=False)
    btc_volume = Column(Float, nullable=False)
    fee_btc = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    sender = Column(String(64))
    receiver = Column(String(64))
    from_entity = Column(String(128))
    to_entity = Column(String(128))
    tx_type = Column(Enum(TransactionType))

class FeeHistory(Base):
    __tablename__ = 'fee_history'
    
    id = Column(Integer, primary_key=True)
    crypto_type = Column(String(10), nullable=False)  # BTC, ETH, USDC, USDT
    timestamp = Column(DateTime, default=datetime.utcnow)
    fee_rate = Column(Float)  # sat/byte for BTC, gwei for ETH
    fee_usd = Column(Float)  # USD equivalent
    block_number = Column(Integer)  # For ETH transactions

class EntityAddress(Base):
    __tablename__ = 'entity_addresses'
    
    id = Column(Integer, primary_key=True)
    address = Column(String(64), unique=True, nullable=False)
    entity_name = Column(String(128))
    entity_type = Column(String(64))  # exchange, mining_pool, whale, etc.
    first_seen = Column(DateTime)
    last_seen = Column(DateTime)
    total_volume = Column(Float, default=0.0)
    transaction_count = Column(Integer, default=0)

def init_db(app):

    """Initialize the database with PostgreSQL support for Render"""
    database_url = app.config['SQLALCHEMY_DATABASE_URI']
    
    # Handle PostgreSQL requirement on Render
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    return engine