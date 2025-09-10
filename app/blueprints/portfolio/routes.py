import pandas as pd
from flask import render_template, flash, redirect, request
from . import bp
from ...services.csv_service import read_previous_df, append_and_save
from ...models.bond import Bond
import os
from ...services.charts_service import build_current_value_timeseries, render_current_value_png
@bp.get("/")
def portfolio():
    df = read_previous_df()
    obligacje = []
    if not df.empty:
        for _, row in df.iterrows():
            obligacja = Bond(
                data_zakupu=row.get("Data_Zakupu"),
                seria_obligacji=row.get("Seria_Obligacji"),
                typ_obligacji=row.get("Typ_Obligacji"),
                wartosc_nominalna=row.get("Wartosc_Nominalna"),
                cena_zakupu=row.get("Cena_Zakupu"),
                data_emisji=row.get("Data_Emisji"),
                data_wykupu=row.get("Data_Wykupu"),
                oprocentowanie=row.get("Oprocentowanie"),
                aktualna_wartosc=row.get("Aktualna_Wartosc"),
                kod_ISIN=row.get("Kod_ISIN"),
                numer_transakcji=row.get("Numer_Transakcji"),
            )
            obligacje.append(obligacja)
    return render_template("portfolio.html", obligacje=obligacje)
@bp.get("/analiza")
def portfolio_analysis():
    df = read_previous_df()
    timeseries = build_current_value_timeseries(df)
    return render_template("portfolio_analysis.html", timeseries=timeseries)

@bp.get("/analiza/chart.png")
def portfolio_analysis_chart_png():
    df = read_previous_df()
    png_bytes = render_current_value_png(df, width_px=900, height_px=400)
    from flask import Response
    return Response(png_bytes, mimetype='image/png')


@bp.post("/import_csv")
def import_csv():
    try:
        file = request.files.get("csv_file")
        if not file:
            flash("Nie wybrano pliku.", "warning")
            return redirect("/portfolio")

        try:
            df = pd.read_csv(file, header=0)
        except UnicodeDecodeError:
            file.seek(0)
            df = pd.read_csv(file, encoding="cp1250")

        if df.empty:
            flash("Plik CSV jest pusty.", "warning")
            return redirect("/portfolio")

        total = append_and_save(df)
        flash(f"Zaimportowano {len(df)} nowych wierszy. Łącznie: {total}", "success")
        return redirect("/portfolio")

    except Exception as e:
        flash(f"Błąd podczas importu: {e}", "danger")
        return redirect("/portfolio")