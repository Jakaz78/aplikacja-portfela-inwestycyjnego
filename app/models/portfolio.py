from datetime import datetime
from .. import db


class Portfolio(db.Model):
    __tablename__ = 'portfolios'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False, default='Główny Portfel')
    description = db.Column(db.Text)

    # --- ZMIANA: Dodano pole gotówki ---
    cash_balance = db.Column(db.DECIMAL(15, 2), default=0.00, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    holdings = db.relationship('Holding', backref='portfolio', cascade='all, delete-orphan', lazy=True)
    transactions = db.relationship('Transaction', backref='portfolio', lazy=True)

    # --- ZMIANA: Relacja do historii ---
    history = db.relationship('PortfolioHistory', backref='portfolio', cascade='all, delete-orphan', lazy=True)

    def __repr__(self):
        return f'<Portfolio {self.name}>'