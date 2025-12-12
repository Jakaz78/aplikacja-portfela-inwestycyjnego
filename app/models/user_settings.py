from .. import db


class UserSettings(db.Model):
    __tablename__ = 'user_settings'

    # Klucz główny jest jednocześnie kluczem obcym do usera (relacja 1:1)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), primary_key=True)

    theme = db.Column(db.String(20), default='Dark', nullable=False)
    language = db.Column(db.String(20), default='Polski', nullable=False)
    currency = db.Column(db.String(10), default='PLN', nullable=False)  # Np. do wyświetlania

    # Relacja zwrotna
    user = db.relationship('User', back_populates='settings', uselist=False)

    def __repr__(self):
        return f"<UserSettings user={self.user_id} theme={self.theme}>"