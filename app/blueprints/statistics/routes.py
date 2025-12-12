import pandas as pd
from flask import render_template, flash, redirect, request, url_for, Response, current_app
from flask_login import login_required, current_user
from . import bp
from ...services.portfolio_service import PortfolioService
from ...models.bond import Bond
from ...services.charts_service import build_current_value_timeseries, render_current_value_png

from ...models.holding import Holding
from ...models.portfolio import Portfolio
from ...models.transaction import Transaction
from ... import db



@bp.get("/")
@login_required
def statistics():

    return render_template("statistics.html")

