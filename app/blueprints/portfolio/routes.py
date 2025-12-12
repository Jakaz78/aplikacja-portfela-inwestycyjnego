import pandas as pd
from flask import render_template, flash, redirect, request, url_for, Response
from flask_login import login_required, current_user
from . import bp
from ...services.portfolio_service import PortfolioService
from ...services.csv_service import CsvService
from ...services.charts_service import build_current_value_timeseries
from ...models.bond import Bond
from ...models.holding import Holding
from ...models.portfolio import Portfolio
from ...models.transaction import Transaction
from ... import db


@bp.get("/")
@login_required
def portfolio():
    """Wyświetla portfolio użytkownika - tylko DB"""
    df = PortfolioService.get_user_portfolio_df(current_user.id)

    obligacje = []
    if not df.empty:
        df = df.fillna("").replace({"None": ""})
        # Teraz cała logika mapowania jest schowana w metodzie .from_dataframe_row()
        obligacje = [Bond.from_dataframe_row(row) for _, row in df.iterrows()]

    return render_template("portfolio.html", obligacje=obligacje)


@bp.get("/analiza")
@login_required
def portfolio_analysis():
    """Analiza portfela"""
    df = PortfolioService.get_user_portfolio_df(current_user.id)
    freq = request.args.get('freq', 'D')
    timeseries = build_current_value_timeseries(df, freq=freq)
    return render_template("portfolio_analysis.html", timeseries=timeseries)


@bp.get("/kalendarz")
@login_required
def portfolio_calendar():
    """Kalendarz wykupów"""
    df = PortfolioService.get_user_portfolio_df(current_user.id)
    events = []

    if not df.empty:
        # Logikę ekstrakcji daty można by też przenieść do modelu, ale tutaj jest specyficzna
        date_cols = ['Data_Wykupu', 'maturity_date']

        for _, row in df.iterrows():
            maturity = None
            for col in date_cols:
                if col in row and pd.notna(row[col]):
                    try:
                        maturity = pd.to_datetime(row[col], dayfirst=True).date()
                        break
                    except Exception:
                        continue

            if maturity:
                # Budowanie tytułu
                parts = [str(row.get(f)) for f in ['bond_type', 'series'] if row.get(f)]
                title = " ".join(parts) or "Obligacja"

                events.append({
                    "title": f"Wykup: {title}",
                    "start": maturity.isoformat(),
                })

    return render_template("calendar.html", events=events)


@bp.post("/import_csv")
@login_required
def import_csv():
    """Import danych z CSV"""
    try:
        file = request.files.get("csv_file")
        if not file or not file.filename:
            flash("Nie wybrano pliku.", "warning")
            return redirect(url_for('portfolio.portfolio'))

        # Użycie nowego serwisu
        df = CsvService.read_csv_with_encoding(file)

        if df.empty:
            flash("Plik CSV jest pusty.", "warning")
            return redirect(url_for('portfolio.portfolio'))

        # Import do DB
        result = PortfolioService.import_csv_data(current_user.id, df)

        if result['errors']:
            error_msg = ', '.join(result['errors'][:3])
            flash(f"Błędy podczas importu: {error_msg}...", "danger")
        else:
            flash(f"Pomyślnie zaimportowano {result['imported']} pozycji", "success")

    except Exception as e:
        flash(f"Błąd krytyczny: {str(e)[:100]}", "danger")

    return redirect(url_for('portfolio.portfolio'))


@bp.post("/delete/<int:holding_id>")
@login_required
def delete_holding(holding_id):
    """Usuwanie pozycji"""
    try:
        holding = Holding.query.join(Portfolio).filter(
            Holding.id == holding_id,
            Portfolio.user_id == current_user.id
        ).first()

        if not holding:
            flash("Pozycja nie została znaleziona.", "danger")
        else:
            # Usuwamy transakcje powiązane z tym holdingiem (po referencji)
            Transaction.query.filter_by(
                portfolio_id=holding.portfolio_id,
                transaction_reference=holding.transaction_reference
            ).delete()

            db.session.delete(holding)
            db.session.commit()
            flash("Usunięto pozycję.", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Błąd podczas usuwania: {str(e)}", "danger")

    return redirect(url_for('portfolio.portfolio'))