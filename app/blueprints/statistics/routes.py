from flask import render_template
from flask_login import login_required, current_user
from . import bp
from ...services.portfolio_service import PortfolioService
from ...services.charts_service import build_allocation_pie_data


from ...services.charts_service import build_market_structure_pie_data # <-- Import

@bp.get("/")
@login_required
def statistics():
    df = PortfolioService.get_user_portfolio_df(current_user.id)

    if df.empty:
        return render_template("statistics.html", has_data=False, total_value=0)

    # Wykres 1: Szczegółowy podział (już istnieje)
    pie_data = build_allocation_pie_data(
        df,
        group_by_candidates=['bond_type', 'Typ_Obligacji'],
        value_column='current_value'
    )

    # Wykres 2: Skarbowe vs Korporacyjne (NOWOŚĆ)
    market_data = build_market_structure_pie_data(df)

    total_value = df['current_value'].sum()

    return render_template(
        "statistics.html",
        pie_data=pie_data,
        market_data=market_data,  # <-- Przekazujemy nowe dane
        total_value=total_value,
        has_data=True
    )