from datetime import datetime
from .. import db


class Holding(db.Model):
    __tablename__ = 'holdings'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    portfolio_id = db.Column(db.BigInteger, db.ForeignKey('portfolios.id'), nullable=False, index=True)
    bond_definition_id = db.Column(db.BigInteger, db.ForeignKey('bond_definitions.id'), nullable=False, index=True)
    quantity = db.Column(db.DECIMAL(15, 4), nullable=False, default=1)
    purchase_price = db.Column(db.DECIMAL(10, 4), nullable=False)
    purchase_date = db.Column(db.Date, nullable=False, index=True)
    transaction_reference = db.Column(db.VARCHAR(100))
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, nullable=False)
    current_value = db.Column(db.DECIMAL(12, 4))

    __table_args__ = (
        db.Index('idx_portfolio_bond', 'portfolio_id', 'bond_definition_id'),
        db.Index('idx_purchase_date', 'purchase_date'),
        db.UniqueConstraint('portfolio_id', 'transaction_reference', name='uq_holding_portfolio_ref'),
    )

    def __repr__(self):
        return f'<Holding {self.quantity} of {self.bond_definition_id}>'

    @property
    def total_value(self):
        return self.quantity * self.purchase_price


