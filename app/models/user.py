from datetime import datetime
from .. import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(120), nullable=True)
    last_name = db.Column(db.String(120), nullable=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    # --- ZMIANA: Relacja do ustawień zamiast kolumny integer ---
    # lazy='joined' sprawia, że ustawienia ładują się od razu z użytkownikiem (szybciej)
    settings = db.relationship('UserSettings', back_populates='user', uselist=False, cascade='all, delete-orphan',
                               lazy='joined')

    portfolios = db.relationship('Portfolio', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)