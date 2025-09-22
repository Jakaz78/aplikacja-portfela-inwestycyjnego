import pandas as pd
from datetime import datetime
import logging


def fetch_poland_cpi_yoy(start: str = None, end: str = None) -> pd.DataFrame:
    """
    Fetch Poland CPI YoY from Yahoo Finance via yfinance.

    We use the series '^PLCPIYOY' if available; if not, fallback to CPI index 'PLCPIIDX' and compute YoY.
    Returns a DataFrame with columns: ['date', 'value'] where value is percentage (e.g., 6.5).
    """
    import yfinance as yf
    # Suppress noisy yfinance logging
    logging.getLogger("yfinance").setLevel(logging.ERROR)
    logging.getLogger("urllib3").setLevel(logging.ERROR)

    start = start or '2010-01-01'
    end = end or datetime.utcnow().date().isoformat()

    # Try YoY series first
    yoy_symbol_candidates = ["^PLCPIYOY", "PLCPI YOY", "PLCPI%3AYOY"]
    for symbol in yoy_symbol_candidates:
        try:
            t = yf.Ticker(symbol)
            hist = t.history(start=start, end=end, interval="1mo")
            if not hist.empty:
                s = hist['Close'].dropna()
                if not s.empty:
                    df = pd.DataFrame({
                        'date': s.index.to_period('M').to_timestamp().date,
                        'value': s.values
                    })
                    return df
        except Exception:
            pass

    # Fallback: monthly CPI index, compute YoY
    idx_symbol_candidates = ["^PLCPI", "PLCPI", "PLCPIIDX"]
    for symbol in idx_symbol_candidates:
        try:
            t = yf.Ticker(symbol)
            hist = t.history(start=start, end=end, interval="1mo")
            if hist.empty:
                continue
            s = hist['Close'].dropna()
            if s.empty:
                continue
            yoy = (s.pct_change(12) * 100).dropna()
            if yoy.empty:
                continue
            df = pd.DataFrame({
                'date': yoy.index.to_period('M').to_timestamp().date,
                'value': yoy.values
            })
            return df
        except Exception:
            pass

    # As a last resort, return empty
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


