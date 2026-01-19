from datetime import datetime
from decimal import Decimal
from .. import db


class Holding(db.Model):
    __tablename__ = 'holdings'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    portfolio_id = db.Column(db.BigInteger, db.ForeignKey('portfolios.id'), nullable=False, index=True)
    bond_definition_id = db.Column(db.BigInteger, db.ForeignKey('bond_definitions.id'), nullable=False, index=True)

    # Ilość i cena (średnia ważona)
    quantity = db.Column(db.DECIMAL(15, 4), nullable=False, default=Decimal('0'))
    purchase_price = db.Column(db.DECIMAL(10, 4), nullable=False, default=Decimal('0'))

    # Data pierwszego zakupu (lub ostatniej modyfikacji - zależy od logiki)
    purchase_date = db.Column(db.Date, nullable=False, index=True)

    # To pole teraz może być NULL, bo holding agreguje wiele transakcji
    transaction_reference = db.Column(db.VARCHAR(100), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    current_value = db.Column(db.DECIMAL(12, 4))

    # Relacje
    # (Portfolio i BondDefinition są już podpięte przez backref w innych modelach,
    # ale można je tu zadeklarować explicit jeśli wolisz)

    __table_args__ = (
        # USUNIĘTO UniqueConstraint aby pozwolić na wiele "partii" (lots) tej samej obligacji
        # np. kupionych w różnych datach lub cenach.
        # db.UniqueConstraint('portfolio_id', 'bond_definition_id', name='uq_holding_portfolio_bond'),
    )

    def __repr__(self):
        return f'<Holding id={self.id} qty={self.quantity}>'

    @property
    def total_cost(self):
        """Łączny koszt zakupu (ilość * średnia cena)"""
        return self.quantity * self.purchase_price

    @property
    def total_current_value(self):
        """Łączna wycena rynkowa"""
        if self.current_value:
            # Zakładamy, że current_value w bazie to wartość CAŁEJ pozycji (nie jednej sztuki),
            # tak jak to zapisujemy w importerze.
            return self.current_value
        return self.quantity * self.purchase_price