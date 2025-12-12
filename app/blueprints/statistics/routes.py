from flask import render_template
from flask_login import login_required, current_user
from . import bp
from ...services.portfolio_service import PortfolioService
from ...services.charts_service import build_allocation_pie_data


@bp.get("/")
@login_required
def statistics():
    df = PortfolioService.get_user_portfolio_df(current_user.id)

    if df.empty:
        return render_template("statistics.html",
                               pie_data={"labels": [], "values": []},
                               has_data=False,
                               total_value=0)

    # Wykres kołowy
    pie_data = build_allocation_pie_data(
        df,
        group_by_candidates=['bond_type', 'Typ_Obligacji', 'bond_definition_bond_type'],
        value_column='current_value'
    )

    # Łączna wartość (Nawiasy są kluczowe!)
    total_value = df['current_value'].sum()  # <--- TUTAJ ()

    return render_template(
        "statistics.html",
        pie_data=pie_data,
        total_value=total_value,
        has_data=True
    )