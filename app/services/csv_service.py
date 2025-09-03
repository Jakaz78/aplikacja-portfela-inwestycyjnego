from pathlib import Path
from flask import current_app
import pandas as pd

def _previous_csv_path() -> Path:
    return Path(current_app.config['UPLOAD_FOLDER']) / 'previous.csv'

def read_previous_df() -> pd.DataFrame:
    path = _previous_csv_path()
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()

def append_and_save(df: pd.DataFrame) -> int:
    """
    Dopisuje df do previous.csv i zwraca łączną liczbę wierszy po zapisie.
    """
    path = _previous_csv_path()
    if path.exists():
        prev = pd.read_csv(path)
        combined = pd.concat([prev, df], ignore_index=True)
    else:
        combined = df
    combined.to_csv(path, index=False)
    return len(combined)