from app.models.portfolio import Portfolio
from app.models.bond_definition import BondDefinition
from app.models.holding import Holding
from app.models.transaction import Transaction
from .. import db
import pandas as pd
from typing import Dict, Optional
from datetime import date


class PortfolioService:

    @staticmethod
    def get_user_portfolio_df(user_id: int) -> pd.DataFrame:
        """
        Pobiera zagregowane portfolio użytkownika.
        """
        query = db.session.query(
            Holding.id.label('holding_id'),
            BondDefinition.isin.label('isin'),
            BondDefinition.name.label('name'),
            BondDefinition.issuer.label('issuer'),
            BondDefinition.series.label('series'),
            BondDefinition.bond_type.label('bond_type'),
            BondDefinition.maturity_date.label('maturity_date'),
            BondDefinition.emission_date.label('emission_date'),
            BondDefinition.coupon_rate.label('coupon_rate'),
            BondDefinition.nominal_value.label('nominal_value'),

            # Dane z holdingu (już zagregowane)
            Holding.quantity.label('quantity'),
            Holding.purchase_price.label('purchase_price'),  # Średnia ważona
            Holding.purchase_date.label('purchase_date'),  # Data pierwszego/ostatniego zakupu
            Holding.current_value.label('current_value'),

            # Transaction reference w holdingu może być pusty przy agregacji
            Holding.transaction_reference.label('transaction_reference'),
        ).select_from(Portfolio) \
            .join(Holding, Portfolio.id == Holding.portfolio_id) \
            .join(BondDefinition, Holding.bond_definition_id == BondDefinition.id) \
            .filter(Portfolio.user_id == user_id)

        return pd.read_sql(query.statement, con=db.session.get_bind())

    @staticmethod
    def get_or_create_default_portfolio(user_id: int) -> Portfolio:
        portfolio = Portfolio.query.filter_by(user_id=user_id).first()
        if not portfolio:
            portfolio = Portfolio(user_id=user_id, name='Główny Portfel')
            db.session.add(portfolio)
            db.session.flush()
        return portfolio

    @staticmethod
    def import_csv_data(user_id: int, df: pd.DataFrame) -> Dict[str, any]:
        """
        Importuje dane z CSV, agregując pozycje w Holdings i zapisując historię w Transactions.
        """
        portfolio = PortfolioService.get_or_create_default_portfolio(user_id)
        imported_count = 0
        errors = []

        try:
            for index, row in df.iterrows():
                try:
                    # 1. Parsowanie wiersza
                    row_data = PortfolioService._parse_csv_row(row)
                    if not row_data:
                        continue

                    # 2. Sprawdzenie duplikatów transakcji
                    if row_data['tx_ref'] and _transaction_exists(portfolio.id, row_data['tx_ref']):
                        continue

                    # 3. Definicja obligacji
                    bond_def = _get_or_create_bond_definition(row_data['isin'], row)

                    # 4. Aktualizacja Holdingu (Upsert)
                    PortfolioService._upsert_holding(portfolio, bond_def, row_data)

                    # 5. Rejestracja Transakcji
                    PortfolioService._create_transaction_record(portfolio, bond_def, row_data)

                    imported_count += 1

                except Exception as e:
                    errors.append(f"Wiersz {index}: {str(e)}")

            if errors:
                db.session.rollback()
            else:
                db.session.commit()

        except Exception as e:
            db.session.rollback()
            errors.append(f"Błąd ogólny: {str(e)}")

        return {"imported": imported_count, "errors": errors}

    @staticmethod
    def _parse_csv_row(row) -> Optional[Dict]:
        """Ekstrahuje i parsuje dane z pojedynczego wiersza DataFrame."""
        isin = _extract_val(row, ['Kod_ISIN', 'isin', 'kod_isin'])
        if not isin:
            return None

        return {
            'isin': isin,
            'tx_ref': _extract_val(row, ['Numer_Transakcji', 'numer_transakcji', 'id_operacji']),
            'qty': _parse_float(row, ['ilosc', 'Liczba', 'quantity'], default=1.0),
            'price': _parse_float(row, ['Cena_Zakupu', 'cena', 'price'], default=100.0),
            'curr_val': _parse_float(row, ['Aktualna_Wartosc', 'Wartosc', 'current_value'], default=0.0),
            'date': _parse_date(row, ['Data_Zakupu', 'Data', 'date']) or date.today()
        }

    @staticmethod
    def _upsert_holding(portfolio: Portfolio, bond_def: BondDefinition, data: Dict):
        """Aktualizuje lub tworzy pozycję (Holding) w portfelu - teraz uwzględnia partie (lots)."""
        qty = data['qty']
        price = data['price']
        curr_val = data['curr_val']
        p_date = data['date']

        # Szukamy DOKŁADNEGO dopasowania (ta sama obligacja, ta sama data zakupu, ta sama cena zakupu)
        # Dzięki temu "dokupienie" w tych samych warunkach powiększy pozycję,
        # a zakup w innej dacie/cenie stworzy nową (osobny wiersz).
        holding = Holding.query.filter_by(
            portfolio_id=portfolio.id,
            bond_definition_id=bond_def.id,
            purchase_date=p_date,
            purchase_price=price
        ).first()

        if holding:
            # Dopasowano partię -> Aktualizacja ilości
            new_total_qty = float(holding.quantity) + float(qty)
            holding.quantity = new_total_qty
            
            # Cena jest ta sama (warunek wyszukiwania), więc nie zmieniamy purchase_price

            # Sumowanie wartości bieżącej
            current_val_base = float(holding.current_value) if holding.current_value is not None else 0.0
            holding.current_value = current_val_base + float(curr_val)

            # Reset referencji transakcji przy agregacji
            holding.transaction_reference = None
        else:
            # Nowa pozycja (osobny lot)
            holding = Holding(
                portfolio_id=portfolio.id,
                bond_definition_id=bond_def.id,
                quantity=qty,
                purchase_price=price,
                purchase_date=p_date,
                current_value=curr_val,
                transaction_reference=None
            )
            db.session.add(holding)

    @staticmethod
    def _create_transaction_record(portfolio: Portfolio, bond_def: BondDefinition, data: Dict):
        """Tworzy rekord w historii transakcji."""
        new_tx = Transaction(
            portfolio_id=portfolio.id,
            bond_definition_id=bond_def.id,
            transaction_type='BUY',
            quantity=data['qty'],
            price=data['price'],
            transaction_date=data['date'],
            transaction_reference=data['tx_ref']
        )
        db.session.add(new_tx)


# --- Helpers (funkcje pomocnicze) ---

def _extract_val(row, keys):
    for k in keys:
        if k in row and pd.notna(row[k]) and str(row[k]).strip() != '':
            return str(row[k]).strip()
    return None


def _parse_float(row, keys, default=0.0):
    val = _extract_val(row, keys)
    if not val: return default
    try:
        # Obsługa polskiego formatu liczb
        clean = str(val).replace(' ', '').replace(',', '.').replace('zł', '').replace('%', '')
        return float(clean)
    except:
        return default


def _parse_date(row, keys):
    val = _extract_val(row, keys)
    if not val: return None
    try:
        return pd.to_datetime(val, dayfirst=True).date()
    except:
        return None


def _transaction_exists(pid, ref):
    if not ref: return False
    # Sprawdzamy w tabeli Transactions
    return db.session.query(Transaction).filter_by(
        portfolio_id=pid,
        transaction_reference=ref
    ).first() is not None


def _get_or_create_bond_definition(isin, row):
    bond = BondDefinition.query.filter_by(isin=isin).first()
    if not bond:
        # Próba wyciągnięcia danych z różnych kolumn
        name = _extract_val(row, ['Nazwa', 'Papier', 'name']) or isin
        series = _extract_val(row, ['Seria_Obligacji', 'Seria', 'series']) or isin
        b_type = _extract_val(row, ['Typ_Obligacji', 'Typ', 'type'])

        # Parsowanie dat
        mat_date = _parse_date(row, ['Data_Wykupu', 'Maturity'])
        em_date = _parse_date(row, ['Data_Emisji', 'Emission'])

        # Oprocentowanie
        coupon = _parse_float(row, ['Oprocentowanie', 'Coupon']) / 100.0 if _extract_val(row, ['Oprocentowanie',
                                                                                               'Coupon']) else None

        bond = BondDefinition(
            isin=isin,
            name=name,
            issuer='Skarb Państwa',  # Domyślnie
            series=series,
            bond_type=b_type,
            maturity_date=mat_date,
            emission_date=em_date,
            coupon_rate=coupon
        )
        db.session.add(bond)
        db.session.flush()  # Żeby dostać ID
    else:
        # Opcjonalnie: Uzupełnianie brakujących danych w definicji
        pass
    return bond