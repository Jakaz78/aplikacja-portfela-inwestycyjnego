from datetime import datetime
from .. import db


class Portfolio(db.Model):
    __tablename__ = 'portfolios'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False, index=True)
    name = db.Column(db.VARCHAR(100), nullable=False, default='Główny Portfel')
    description = db.Column(db.Text)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('portfolios', lazy=True))
    holdings = db.relationship('Holding', backref='portfolio', cascade='all, delete-orphan', lazy=True)

    def __repr__(self):
        return f'<Portfolio {self.name}>'


