from datetime import datetime
from .. import db


class PortfolioHistory(db.Model):
    __tablename__ = 'portfolio_history'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    portfolio_id = db.Column(db.BigInteger, db.ForeignKey('portfolios.id'), nullable=False, index=True)

    date = db.Column(db.Date, nullable=False, index=True)
    total_value = db.Column(db.DECIMAL(15, 2), nullable=False)  # Łączna wartość (gotówka + obligacje)
    cash_value = db.Column(db.DECIMAL(15, 2), default=0.00)  # Ile było gotówki
    bond_value = db.Column(db.DECIMAL(15, 2), default=0.00)  # Ile były warte obligacje

    created_at = db.Column(db.DateTime, default=datetime.now)

    # Zabezpieczenie: tylko jeden wpis historii na dany dzień dla jednego portfela
    __table_args__ = (
        db.UniqueConstraint('portfolio_id', 'date', name='uq_portfolio_history_date'),
    )