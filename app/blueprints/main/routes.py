from flask import render_template
from . import bp

@bp.get("/")
def index():
    return render_template("index.html")

@bp.get("/statistics")
def statistics():
    return render_template("statistics.html")