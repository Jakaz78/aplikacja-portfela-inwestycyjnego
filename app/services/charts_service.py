import pandas as pd
from typing import Dict, List, Tuple


def build_current_value_timeseries(df: pd.DataFrame,
                                   date_column_candidates: List[str] = None,
                                   value_column: str = "Aktualna_Wartosc",
                                   freq: str = "D") -> Dict[str, List]:
    """
    Build time series of total current value over time.

    - Picks first existing date column among candidates and parses to datetime
    - Groups by date and sums current value for that date
    - Resamples to `freq` and forward-fills to create a continuous series (no cumulative sum)

    Returns a dict with 'labels' (ISO date strings) and 'values' (floats) suitable for charts.
    """
    if df is None or df.empty:
        return {"labels": [], "values": []}

    if date_column_candidates is None:
        date_column_candidates = [
            "Data_Zakupu",
            "Data_Emisji",
            "Data_Wykupu",
            "Data",
            "Date",
        ]

    date_col = None
    for candidate in date_column_candidates:
        if candidate in df.columns:
            date_col = candidate
            break

    if date_col is None:
        return {"labels": [], "values": []}

    work = df.copy()

    if value_column not in work.columns:
        for alt in ["Aktualna Wartość", "Wartosc_Aktualna", "Current_Value", "Wartość"]:
            if alt in work.columns:
                value_column = alt
                break
        if value_column not in work.columns:
            return {"labels": [], "values": []}

    work[value_column] = pd.to_numeric(work[value_column], errors="coerce")
    work[date_col] = pd.to_datetime(work[date_col], errors="coerce", dayfirst=True)

    work = work.dropna(subset=[date_col, value_column])
    if work.empty:
        return {"labels": [], "values": []}

    daily_sum = (
        work.groupby(work[date_col].dt.normalize())[value_column]
        .sum()
        .sort_index()
    )

    # Resample to continuous frequency and forward-fill last known total for days without records
    total_over_time = daily_sum.asfreq(freq).ffill()

    total_over_time = total_over_time.dropna()

    labels = [d.date().isoformat() for d in total_over_time.index]
    values = total_over_time.round(2).tolist()

    return {"labels": labels, "values": values}


def render_current_value_png(df: pd.DataFrame, width_px: int = 900, height_px: int = 400) -> bytes:
    """
    Render the current value time series to a PNG image and return raw bytes.
    """
    # Lazy import to avoid requiring matplotlib where not needed
    import matplotlib
    matplotlib.use("Agg")
    from matplotlib import pyplot as plt
    from matplotlib.ticker import FuncFormatter
    import io

    ts = build_current_value_timeseries(df)
    fig_w = max(1.0, width_px / 100)
    fig_h = max(1.0, height_px / 100)

    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=100)

    if ts["labels"]:
        # Convert ISO date strings to pandas datetime for plotting spacing
        x = pd.to_datetime(ts["labels"])  # type: ignore[arg-type]
        y = ts["values"]
        ax.plot(x, y, color="#0d6efd")
        ax.fill_between(x, y, color="#0d6efd", alpha=0.15)

    ax.set_title("Łączna aktualna wartość (PLN)")
    ax.grid(True, axis="y", alpha=0.2)

    def pln_fmt(y, _):
        return f"{y:,.0f} zł".replace(",", " ").replace(".", ",")

    ax.yaxis.set_major_formatter(FuncFormatter(pln_fmt))
    fig.autofmt_xdate()
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()
