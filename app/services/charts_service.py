import pandas as pd
from typing import Dict, List


def build_current_value_timeseries(df: pd.DataFrame, freq: str = "D") -> Dict[str, List]:
    """Generuje dane do wykresu liniowego wartości portfela w czasie."""
    if df is None or df.empty:
        return {"labels": [], "values": []}

    # Szukamy kolumny z datą
    date_col = None
    candidates = ["purchase_date", "Data_Zakupu", "Data", "date"]
    for c in candidates:
        if c in df.columns:
            date_col = c
            break

    if not date_col:
        return {"labels": [], "values": []}

    # Kopiujemy i konwertujemy
    work = df.copy()
    work[date_col] = pd.to_datetime(work[date_col], errors="coerce")
    work["current_value"] = pd.to_numeric(work["current_value"], errors="coerce").fillna(0)

    # Grupujemy po dacie i sumujemy
    daily_sum = work.groupby(date_col)["current_value"].sum().sort_index()

    if daily_sum.empty:
        return {"labels": [], "values": []}

    # Resampling (uzupełnienie brakujących dni) i forward fill
    ts = daily_sum.asfreq(freq, method='ffill').fillna(0)

    labels = [d.strftime('%Y-%m-%d') for d in ts.index]
    # !!! TU BYŁ BŁĄD - dodano nawiasy () na końcu !!!
    values = ts.round(2).tolist()

    return {"labels": labels, "values": values}


def build_allocation_pie_data(df: pd.DataFrame, group_by_candidates: List[str] = None,
                              value_column: str = "current_value") -> Dict[str, List]:
    """Generuje dane do wykresu kołowego."""
    if df is None or df.empty:
        return {"labels": [], "values": []}

    group_col = None
    if group_by_candidates:
        for c in group_by_candidates:
            if c in df.columns:
                group_col = c
                break

    if not group_col:
        return {"labels": [], "values": []}

    work = df.copy()
    work[value_column] = pd.to_numeric(work[value_column], errors="coerce").fillna(0)
    work[group_col] = work[group_col].fillna("Inne")

    # Agregacja
    agg = work.groupby(group_col)[value_column].sum().sort_values(ascending=False)

    # !!! TU BYŁ BŁĄD - dodano nawiasy () na końcu obu linii !!!
    labels = agg.index.astype(str).tolist()
    values = agg.round(2).tolist()

    return {"labels": labels, "values": values}


