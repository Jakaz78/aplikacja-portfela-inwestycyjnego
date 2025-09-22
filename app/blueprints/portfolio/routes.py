import pandas as pd
from flask import render_template, flash, redirect, request, url_for, Response, current_app
from flask_login import login_required, current_user
from . import bp
from ...services.portfolio_service import PortfolioService
from ...models.bond import Bond
from ...services.charts_service import build_current_value_timeseries, render_current_value_png
from ...services.inflation_service import fetch_poland_cpi_yoy, align_series_to_common_months

# Mapowanie kolumn
COLUMN_MAPPING = {
    'data_zakupu': ['Data_Zakupu', 'purchase_date'],
    'seria_obligacji': ['Seria_Obligacji', 'series'],
    'typ_obligacji': ['Typ_Obligacji', 'bond_type'],
    'wartosc_nominalna': ['Wartosc_Nominalna', 'nominal_value', 'quantity'],
    'cena_zakupu': ['Cena_Zakupu', 'purchase_price'],
    'data_emisji': ['Data_Emisji', 'emission_date'],
    'data_wykupu': ['Data_Wykupu', 'maturity_date'],
    'aktualna_wartosc': ['Aktualna_Wartosc', 'current_value'],
    'kod_ISIN': ['Kod_ISIN', 'isin'],
    'numer_transakcji': ['Numer_Transakcji', 'transaction_reference']
}


def _get_column_value(row, field_name):
    """Helper do pobierania wartości z różnych nazw kolumn"""
    candidates = COLUMN_MAPPING.get(field_name, [])
    for candidate in candidates:
        value = row.get(candidate)
        if value not in (None, "", "None"):
            return value
    return ""


def _format_coupon_rate(row):
    """Helper do formatowania oprocentowania"""
    text_coupon = row.get("Oprocentowanie")
    if text_coupon and text_coupon not in ("", "None"):
        return text_coupon

    coupon_rate = row.get("coupon_rate")
    if coupon_rate not in (None, "", "None"):
        try:
            return f"{round(float(coupon_rate) * 100, 2)}%"
        except (ValueError, TypeError):
            pass
    return ""


@bp.get("/")
@login_required
def portfolio():
    """Wyświetla portfolio użytkownika - tylko DB"""
    df = PortfolioService.get_user_portfolio_df(current_user.id)

    obligacje = []
    if not df.empty:
        df = df.fillna("").replace({"None": ""})

        for _, row in df.iterrows():
            obligacja = Bond(
                data_zakupu=_get_column_value(row, 'data_zakupu'),
                seria_obligacji=_get_column_value(row, 'seria_obligacji'),
                typ_obligacji=_get_column_value(row, 'typ_obligacji'),
                wartosc_nominalna=_get_column_value(row, 'wartosc_nominalna'),
                cena_zakupu=_get_column_value(row, 'cena_zakupu'),
                data_emisji=_get_column_value(row, 'data_emisji'),
                data_wykupu=_get_column_value(row, 'data_wykupu'),
                oprocentowanie=_format_coupon_rate(row),
                aktualna_wartosc=_get_column_value(row, 'aktualna_wartosc'),
                kod_ISIN=_get_column_value(row, 'kod_ISIN'),
                numer_transakcji=_get_column_value(row, 'numer_transakcji'),
            )
            obligacje.append(obligacja)

    return render_template("portfolio.html", obligacje=obligacje)


@bp.get("/analiza")
@login_required
def portfolio_analysis():
    """Analiza portfela - tylko DB"""
    df = PortfolioService.get_user_portfolio_df(current_user.id)

    freq = request.args.get('freq', 'D')
    timeseries = build_current_value_timeseries(df, freq=freq)
    inflation_compare = _build_inflation_comparison(timeseries)

    return render_template("portfolio_analysis.html",
                           timeseries=timeseries,
                           inflation_compare=inflation_compare)


def _build_inflation_comparison(timeseries):
    """Helper do budowania porównania z inflacją"""
    if not current_app.config.get('FETCH_CPI', False):
        return {'labels': [], 'portfolio_yoy': [], 'cpi_yoy': []}

    try:
        portfolio_ts_df = pd.DataFrame({
            'date': pd.to_datetime(timeseries.get('labels', []), errors='coerce'),
            'value': pd.to_numeric(timeseries.get('values', []), errors='coerce')
        }).dropna()

        cpi_yoy_df = fetch_poland_cpi_yoy()
        compare_df = align_series_to_common_months(portfolio_ts_df, cpi_yoy_df)

        return {
            'labels': [d.isoformat() for d in compare_df['date'].tolist()] if not compare_df.empty else [],
            'portfolio_yoy': compare_df['portfolio_yoy'].round(2).tolist() if not compare_df.empty else [],
            'cpi_yoy': compare_df['cpi_yoy'].round(2).tolist() if not compare_df.empty else [],
        }
    except Exception as e:
        print(f"Warning: Inflation comparison failed: {e}")
        return {'labels': [], 'portfolio_yoy': [], 'cpi_yoy': []}


@bp.get("/analiza/chart.png")
@login_required
def portfolio_analysis_chart_png():
    """Zwraca PNG wykres portfela - tylko DB"""
    df = PortfolioService.get_user_portfolio_df(current_user.id)

    freq = request.args.get('freq', 'D')
    width_px = _safe_int(request.args.get('w'), 900)
    height_px = _safe_int(request.args.get('h'), 400)

    png_bytes = render_current_value_png(df, width_px=width_px, height_px=height_px, freq=freq)
    return Response(png_bytes, mimetype='image/png')


def _safe_int(value, default):
    """Helper do bezpiecznego parsowania int"""
    try:
        return int(value) if value else default
    except (ValueError, TypeError):
        return default


@bp.get("/kalendarz")
@login_required
def portfolio_calendar():
    """Kalendarz wykupów - tylko DB, pusty jeśli brak obligacji"""
    df = PortfolioService.get_user_portfolio_df(current_user.id)

    events = []
    if not df.empty:
        date_cols = ['Data_Wykupu', 'maturity_date']
        date_cols = [c for c in date_cols if c in df.columns]

        for _, row in df.iterrows():
            maturity_date = _extract_maturity_date(row, date_cols)
            if maturity_date:
                title = _build_bond_title(row)
                events.append({
                    "title": f"Wykup: {title}",
                    "start": maturity_date.isoformat(),
                })

    return render_template("calendar.html", events=events)


def _extract_maturity_date(row, date_cols):
    """Helper do wyciągania daty wykupu"""
    for col in date_cols:
        val = row.get(col)
        if pd.notna(val):
            try:
                parsed = pd.to_datetime(val, dayfirst=True, errors='coerce')
                if pd.notna(parsed):
                    return parsed.date()
            except Exception:
                continue
    return None


def _build_bond_title(row):
    """Helper do budowania tytułu obligacji"""
    parts = []
    for field in ['bond_type', 'series', 'Typ_Obligacji', 'Seria_Obligacji']:
        val = row.get(field)
        if pd.notna(val) and val not in ("", "None"):
            parts.append(str(val))
    return " ".join(parts) or "Obligacja"


@bp.post("/import_csv")
@login_required
def import_csv():
    """Import danych z CSV - tylko do DB"""
    try:
        file = request.files.get("csv_file")
        if not file or not file.filename:
            flash("Nie wybrano pliku.", "warning")
            return redirect(url_for('portfolio.portfolio'))

        # Odczytaj CSV
        df = _read_csv_with_encoding(file)
        if df.empty:
            flash("Plik CSV jest pusty.", "warning")
            return redirect(url_for('portfolio.portfolio'))

        # Import tylko do DB
        result = PortfolioService.import_csv_data(current_user.id, df)
        if result['errors']:
            error_msg = ', '.join(result['errors'][:3])
            flash(f"Błędy podczas importu: {error_msg}", "danger")
        else:
            flash(f"Pomyślnie zaimportowano {result['imported']} pozycji", "success")

        return redirect(url_for('portfolio.portfolio'))

    except Exception as e:
        flash(f"Błąd podczas importu: {str(e)[:100]}", "danger")
        return redirect(url_for('portfolio.portfolio'))


def _read_csv_with_encoding(file):
    """Helper do odczytu CSV z różnymi kodowaniami"""
    encodings = ['utf-8', 'cp1250', 'iso-8859-2']

    for encoding in encodings:
        try:
            file.seek(0)
            return pd.read_csv(file, header=0, encoding=encoding)
        except (UnicodeDecodeError, UnicodeError):
            continue
        except Exception:
            break

    try:
        file.seek(0)
        return pd.read_csv(file, header=0)
    except Exception as e:
        raise Exception(f"Nie można odczytać pliku CSV: {e}")
