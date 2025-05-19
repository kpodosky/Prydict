from flask_wtf import FlaskForm
from wtforms import FloatField, SelectField
from wtforms.validators import DataRequired, NumberRange

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
    eth_amount = FloatField('ETH Amount')
    gas_limit = SelectField('Gas Limit',
        choices=[
            ('21000', 'Basic Transfer (21,000)'),
            ('65000', 'Token Transfer (~65,000)'),
            ('200000', 'Smart Contract (~200,000)')
        ]
    )
    usdc_amount = FloatField('USDC Amount')
    usdt_amount = FloatField('USDT Amount')