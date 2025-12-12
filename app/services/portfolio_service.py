from app.models.portfolio import Portfolio
from app.models.bond_definition import BondDefinition
from app.models.holding import Holding
from app.models.transaction import Transaction
from .. import db
import pandas as pd
from typing import Dict, Optional


class PortfolioService:
    @staticmethod
    def get_user_portfolio_df(user_id: int) -> pd.DataFrame:
        """Pobiera portfolio użytkownika jako DataFrame"""
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
            Holding.quantity.label('quantity'),
            Holding.purchase_price.label('purchase_price'),
            Holding.purchase_date.label('purchase_date'),
            Holding.current_value.label('current_value'),
            Holding.transaction_reference.label('transaction_reference'),
        ).select_from(Portfolio) \
            .join(Holding, Portfolio.id == Holding.portfolio_id) \
            .join(BondDefinition, Holding.bond_definition_id == BondDefinition.id) \
            .filter(Portfolio.user_id == user_id)

        return pd.read_sql(query.statement, con=db.session.get_bind())

    @staticmethod
    def get_or_create_default_portfolio(user_id: int) -> Portfolio:
        """Pobiera lub tworzy domyślny portfel użytkownika"""
        portfolio = Portfolio.query.filter_by(user_id=user_id).first()
        if not portfolio:
            portfolio = Portfolio(user_id=user_id, name='Główny Portfel')
            db.session.add(portfolio)
            db.session.flush()
        return portfolio

    @staticmethod
    def import_csv_data(user_id: int, df: pd.DataFrame) -> Dict[str, any]:
        """Importuje dane CSV do bazy danych"""
        portfolio = PortfolioService.get_or_create_default_portfolio(user_id)
        imported_count = 0
        errors = []

        try:
            for index, row in df.iterrows():
                try:
                    # Walidacja ISIN
                    isin = _extract_isin(row)
                    if not isin:
                        errors.append(f"Wiersz {index}: Brak ISIN")
                        continue

                    # Unikaj duplikacji
                    tx_ref = _extract_transaction_ref(row)
                    if _is_duplicate(portfolio.id, tx_ref):
                        imported_count += 1
                        continue

                    # Utwórz lub pobierz definicję obligacji
                    bond = _get_or_create_bond(isin, row)

                    # Utwórz holding i transakcję
                    _create_holding_and_transaction(portfolio.id, bond.id, row, tx_ref)
                    imported_count += 1

                except Exception as e:
                    errors.append(f"Wiersz {index}: {e}")

            # Commit tylko jeśli brak błędów
            if errors:
                db.session.rollback()
            else:
                db.session.commit()

        except Exception as e:
            db.session.rollback()
            errors.append(str(e))

        return {"imported": imported_count, "errors": errors}


# Helper functions - przeniesione poza klasę dla czytelności
def _extract_isin(row) -> Optional[str]:
    """Wyciąga ISIN z wiersza CSV"""
    isin = str(row.get('Kod_ISIN') or row.get('isin') or '').strip()
    return isin if isin else None


def _extract_transaction_ref(row) -> str:
    """Wyciąga numer transakcji z wiersza"""
    return str(row.get('Numer_Transakcji') or row.get('numer_transakcji') or '')


def _is_duplicate(portfolio_id: int, tx_ref: str) -> bool:
    """Sprawdza czy transakcja już istnieje"""
    return bool(Holding.query.filter_by(
        portfolio_id=portfolio_id,
        transaction_reference=tx_ref
    ).first())


def _parse_coupon_rate(coupon_raw) -> Optional[float]:
    """Parsuje oprocentowanie z formatu '3.25%' na 0.0325"""
    if not isinstance(coupon_raw, str) or not coupon_raw.strip().endswith('%'):
        return None

    try:
        return float(coupon_raw.strip().replace('%', '').replace(',', '.')) / 100.0
    except (ValueError, AttributeError):
        return None


def _get_or_create_bond(isin: str, row) -> BondDefinition:
    """Pobiera lub tworzy definicję obligacji"""
    bond = BondDefinition.query.filter_by(isin=isin).first()

    if not bond:
        bond = BondDefinition(
            isin=isin,
            name=str(row.get('Seria_Obligacji') or row.get('nazwa') or isin),
            issuer=str(row.get('emitent') or 'Skarb Państwa'),
            series=str(row.get('Seria_Obligacji') or row.get('seria') or ''),
            bond_type=str(row.get('Typ_Obligacji') or row.get('typ') or ''),
            maturity_date=_parse_date(row.get('Data_Wykupu') or row.get('data_wykupu')),
            emission_date=_parse_date(row.get('Data_Emisji') or row.get('data_emisji')),
            coupon_rate=_parse_coupon_rate(row.get('Oprocentowanie') or row.get('oprocentowanie')),
            nominal_value=pd.to_numeric(row.get('Wartosc_Nominalna') or row.get('wartosc_nominalna') or 100.00,
                                        errors='coerce')
        )
        db.session.add(bond)
        db.session.flush()
    else:
        # Uzupełnij brakujące dane
        _update_bond_if_needed(bond, row)

    return bond


def _parse_date(date_value):
    """Parsuje datę z różnych formatów"""
    if not date_value:
        return None

    parsed = pd.to_datetime(date_value, errors='coerce')
    return parsed.date() if pd.notna(parsed) else None


def _create_holding_and_transaction(portfolio_id: int, bond_id: int, row, tx_ref: str):
    """Tworzy holding i powiązaną transakcję"""
    quantity = pd.to_numeric(row.get('ilosc') or 1, errors='coerce')
    purchase_price = pd.to_numeric(row.get('Cena_Zakupu') or row.get('cena_zakupu') or 100, errors='coerce')
    purchase_date = _parse_date(row.get('Data_Zakupu') or row.get('data_zakupu'))
    current_value = pd.to_numeric(row.get('Aktualna_Wartosc') or row.get('aktualna_wartosc'), errors='coerce')

    # Holding
    holding = Holding(
        portfolio_id=portfolio_id,
        bond_definition_id=bond_id,
        quantity=quantity,
        purchase_price=purchase_price,
        purchase_date=purchase_date,
        current_value=current_value,
        transaction_reference=tx_ref
    )
    db.session.add(holding)

    # Transaction
    transaction = Transaction(
        portfolio_id=portfolio_id,
        bond_definition_id=bond_id,
        transaction_type='BUY',
        quantity=quantity,
        price=purchase_price,
        transaction_date=purchase_date,
        transaction_reference=tx_ref
    )
    db.session.add(transaction)
