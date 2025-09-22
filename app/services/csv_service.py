# Nowy csv_service.py - tylko DB
import pandas as pd
from flask_login import current_user


def read_previous_df() -> pd.DataFrame:
    """Odczyt portfolio z bazy danych"""
    if not (hasattr(current_user, 'is_authenticated') and current_user.is_authenticated):
        return pd.DataFrame()

    from ..services.portfolio_service import PortfolioService
    return PortfolioService.get_user_portfolio_df(current_user.id)


def append_and_save(df: pd.DataFrame) -> int:
    """Import danych przez PortfolioService"""
    if not (hasattr(current_user, 'is_authenticated') and current_user.is_authenticated):
        return 0

    from ..services.portfolio_service import PortfolioService
    result = PortfolioService.import_csv_data(current_user.id, df)
    if result['errors']:
        raise Exception(f"Import errors: {', '.join(result['errors'])}")
    return result['imported']
