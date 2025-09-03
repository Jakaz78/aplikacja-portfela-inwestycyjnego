import pandas as pd
from flask import render_template, flash, redirect, request
from . import bp
from ...services.csv_service import read_previous_df, append_and_save

@bp.get("/")
def portfolio():
    df = read_previous_df()
    data = df.to_dict(orient="records") if not df.empty else []
    return render_template("portfolio.html", data=data)

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