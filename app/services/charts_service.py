import pandas as pd
from typing import Dict, List


def build_current_value_timeseries(df: pd.DataFrame, freq: str = "D") -> Dict[str, List]:
    """Generuje dane do wykresu liniowego wartości portfela w czasie."""
    if df is None or df.empty:
        return {"labels": [], "values": [], "costs": []}

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
    
    # Obliczamy koszt (invested capital) dla każdej pozycji
    # W imporcie CSV: quantity * price (price jest ceną jednostkową? Nie, w modelu Holding purchase_price to cena jednostkowa)
    work["quantity"] = pd.to_numeric(work["quantity"], errors="coerce").fillna(0)
    work["purchase_price"] = pd.to_numeric(work["purchase_price"], errors="coerce").fillna(0)
    work["invested_val"] = work["quantity"] * work["purchase_price"]

    # Grupujemy po dacie i sumujemy
    daily = work.groupby(date_col)[["current_value", "invested_val"]].sum().sort_index()

    if daily.empty:
        return {"labels": [], "values": [], "costs": []}

    # Resampling (uzupełnienie brakujących dni) i forward fill
    ts = daily.asfreq(freq, method='ffill').fillna(0)

    # Obcinamy do dzisiaj (żeby wykres nie leciał w nieskończoność w przyszłość, jeśli są daty przyszłe?)
    # Ale daty "purchase_date" są przeszłe. Wartość portfela jest "na dzień".
    # W obecnej logice user importuje plik z aktualną wartością "na dzień zakupu"? 
    # Nie, importuje stan portfela. Data_Wykupu to przyszłość. 
    # Data_Zakupu to start.
    # W `build_current_value_timeseries` grupujemy po `purchase_date` (lub dacie stanu).
    # Zakładając że CSV to snapshoty, to OK.

    labels = [d.strftime('%Y-%m-%d') for d in ts.index]
    values = ts["current_value"].round(2).tolist()
    costs = ts["invested_val"].round(2).tolist()

    return {"labels": labels, "values": values, "costs": costs}


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


