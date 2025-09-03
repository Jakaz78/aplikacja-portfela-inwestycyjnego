from flask import Blueprint

bp = Blueprint("portfolio", __name__)

from . import routes  # noqa