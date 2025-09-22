from datetime import datetime
from .. import db


class BondDefinition(db.Model):
    __tablename__ = 'bond_definitions'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    isin = db.Column(db.VARCHAR(12), unique=True, nullable=False, index=True)
    name = db.Column(db.VARCHAR(200), nullable=False, index=True)
    issuer = db.Column(db.VARCHAR(100), nullable=False, index=True)
    series = db.Column(db.VARCHAR(50))
    bond_type = db.Column(db.VARCHAR(50), index=True)
    maturity_date = db.Column(db.Date, index=True)
    emission_date = db.Column(db.Date)
    coupon_rate = db.Column(db.DECIMAL(5, 4))
    nominal_value = db.Column(db.DECIMAL(10, 2), default=100.00)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, nullable=False)

    holdings = db.relationship('Holding', backref='bond', lazy=True)

    def __repr__(self):
        return f'<Bond {self.isin}: {self.name}>'


