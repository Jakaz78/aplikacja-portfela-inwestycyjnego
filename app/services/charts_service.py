import pandas as pd
from typing import Dict, List


def build_current_value_timeseries(df: pd.DataFrame, freq: str = "D") -> Dict[str, List]:
    """
    Generuje dane do wykresu liniowego wartości portfela w czasie.
    Zwraca słownik z listami: labels (daty), values (wartość bieżąca), costs (zainwestowany kapitał).
    """
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

    # Kopiujemy i konwertujemy typy danych
    work = df.copy()
    work[date_col] = pd.to_datetime(work[date_col], errors="coerce")
    work["current_value"] = pd.to_numeric(work["current_value"], errors="coerce").fillna(0)

    # Konwersja ilości i ceny zakupu
    work["quantity"] = pd.to_numeric(work["quantity"], errors="coerce").fillna(0)
    work["purchase_price"] = pd.to_numeric(work["purchase_price"], errors="coerce").fillna(0)

    # Obliczamy koszt (invested capital) dla każdej pozycji
    work["invested_val"] = work["quantity"] * work["purchase_price"]

    # Grupujemy po dacie i sumujemy
    daily = work.groupby(date_col)[["current_value", "invested_val"]].sum().sort_index()

    if daily.empty:
        return {"labels": [], "values": [], "costs": []}

    # Resampling (uzupełnienie brakujących dni metodą forward fill)
    ts = daily.asfreq(freq, method='ffill').fillna(0)

    labels = [d.strftime('%Y-%m-%d') for d in ts.index]
    values = ts["current_value"].round(2).tolist()
    costs = ts["invested_val"].round(2).tolist()

    return {"labels": labels, "values": values, "costs": costs}


def build_allocation_pie_data(df: pd.DataFrame, group_by_candidates: List[str] = None,
                              value_column: str = "current_value") -> Dict[str, List]:
    """
    Generuje dane do wykresu kołowego na podstawie zadanego kryterium grupowania.
    """
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

    # Agregacja i sortowanie
    agg = work.groupby(group_col)[value_column].sum().sort_values(ascending=False)

    labels = agg.index.astype(str).tolist()
    values = agg.round(2).tolist()

    return {"labels": labels, "values": values}


def build_market_structure_pie_data(df: pd.DataFrame) -> Dict[str, List]:
    """
    Generuje dane do wykresu kołowego z podziałem na Rynek (Skarbowe vs Korporacyjne).
    Klasyfikuje obligacje na podstawie emitenta i serii.
    """
    if df is None or df.empty:
        return {"labels": [], "values": []}

    work = df.copy()
    work['current_value'] = pd.to_numeric(work['current_value'], errors='coerce').fillna(0)

    # Funkcja pomocnicza do klasyfikacji
    def classify(row):
        issuer = str(row.get('issuer', '')).lower()
        series = str(row.get('series', '')).upper()
        b_type = str(row.get('bond_type', '')).lower()

        # 1. Sprawdzenie po emitencie (Skarb Państwa)
        if 'skarb' in issuer or 'minister' in issuer:
            return 'Skarbowe'

        # 2. Sprawdzenie po typowych seriach detalicznych obligacji skarbowych
        treasury_prefixes = ['OTS', 'DOS', 'TOZ', 'COI', 'EDO', 'ROR', 'DOR', 'SP', 'DS', 'WS', 'PS']
        if any(series.startswith(p) for p in treasury_prefixes):
            return 'Skarbowe'

        # 3. Jeśli to nie Skarb, sprawdzamy typ lub zakładamy Korporacyjne
        if 'korporac' in b_type:
            return 'Korporacyjne'

        # Domyślna kategoria dla reszty
        return 'Korporacyjne'

    # Zastosowanie klasyfikacji
    work['market_category'] = work.apply(classify, axis=1)

    # Agregacja
    agg = work.groupby('market_category')['current_value'].sum().sort_values(ascending=False)

    return {
        "labels": agg.index.astype(str).tolist(),
        "values": agg.round(2).tolist()
    }