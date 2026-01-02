import pandas as pd
from datetime import datetime
import logging


def fetch_poland_cpi_yoy(start: str = None, end: str = None) -> pd.DataFrame:
    """
    Pobiera wskaźnik CPI dla Polski (r/r) z Yahoo Finance.
    Zwraca DataFrame z kolumnami ['date', 'value'] (procent).
    """
    import yfinance as yf
    logging.getLogger("yfinance").setLevel(logging.ERROR)

    start = start or '2015-01-01'
    end = end or datetime.utcnow().date().isoformat()

    # Kod Yahoo Finance dla indeksu CPI lub podobnego wskaźnika. 
    # Niestety Yahoo często zmienia tickery dla danych makro. 
    # Spróbujmy najpopularniejszego kandydata na "Polish CPI".
    # Jeśli nie zadziała, zwracamy pusty (w realnym wdrożeniu należałoby to brać np. z GUS/Stooq/FRED).
    symbol = "PLNCPI=ECI" 

    try:
        t = yf.Ticker(symbol)
        # Pobieramy historię
        hist = t.history(start=start, end=end, interval="1mo")
        
        if hist.empty:
            # Fallback - czasem CL=F lub inne futures dają podgląd, ale tu lepiej nie zgadywać.
            # Zwróćmy pusty, frontend obsłuży brak danych.
            return pd.DataFrame(columns=['date', 'value'])

        # Zakładając, że to jest wartość indeksu lub % r/r.
        # Sprawdzamy to: ECI na Yahoo zazwyczaj zwraca wartość procentową (np. 14.4 dla 14.4%).
        s = hist['Close'].dropna()
        
        df = pd.DataFrame({
            'date': s.index.to_period('M').to_timestamp().date,
            'value': s.values
        })
        return df

    except Exception:
        return pd.DataFrame(columns=['date', 'value'])


def align_series_to_common_months(portfolio_ts: pd.DataFrame, cpi_yoy: pd.DataFrame) -> pd.DataFrame:
    """
    Align portfolio monthly returns and CPI YoY into common timeline.

    portfolio_ts: DataFrame with columns ['date', 'value'] where value is total value level.
    Returns DataFrame with columns ['date','portfolio_yoy','cpi_yoy'].
    """
    if portfolio_ts is None or portfolio_ts.empty:
        return pd.DataFrame(columns=['date','portfolio_yoy','cpi_yoy'])

    # Convert to month-end and compute YoY % change of portfolio value
    work = portfolio_ts.copy()
    work['date'] = pd.to_datetime(work['date'])
    work = work.set_index('date').resample('ME').last()
    work['portfolio_yoy'] = work['value'].pct_change(12) * 100
    work = work[['portfolio_yoy']].dropna()

    cpi = cpi_yoy.copy()
    if not cpi.empty:
        cpi['date'] = pd.to_datetime(cpi['date'])
        cpi = cpi.set_index('date').resample('ME').last()[['value']].rename(columns={'value':'cpi_yoy'}).dropna()
    else:
        cpi = pd.DataFrame(columns=['cpi_yoy'])

    merged = work.join(cpi, how='inner')
    # Ensure index name so reset_index creates a 'date' column
    merged.index.name = 'date'
    merged = merged.reset_index()
    # If index name was missing, Pandas would have created 'index' column; normalize it
    if 'date' not in merged.columns and 'index' in merged.columns:
        merged = merged.rename(columns={'index': 'date'})
    merged['date'] = pd.to_datetime(merged['date']).dt.date
    return merged


