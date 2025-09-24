from datetime import datetime
from .. import db


class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    portfolio_id = db.Column(db.BigInteger, db.ForeignKey('portfolios.id'), nullable=False, index=True)
    bond_definition_id = db.Column(db.BigInteger, db.ForeignKey('bond_definitions.id'), nullable=False, index=True)
    transaction_type = db.Column(db.Enum('BUY', 'SELL', 'MATURITY', 'COUPON', name='transaction_type_enum'), nullable=False)
    quantity = db.Column(db.DECIMAL(15, 2), nullable=False)
    price = db.Column(db.DECIMAL(10, 4), nullable=False)
    transaction_date = db.Column(db.Date, nullable=False, index=True)
    fees = db.Column(db.DECIMAL(10, 2), default=0.00)
    transaction_reference = db.Column(db.VARCHAR(100), index=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)

    # portfolio = db.relationship('Portfolio', backref=db.backref('transactions', lazy=True))
    # bond = db.relationship('BondDefinition', backref=db.backref('transactions', lazy=True))

    __table_args__ = (
        db.Index('idx_portfolio_date', 'portfolio_id', 'transaction_date'),
    )

