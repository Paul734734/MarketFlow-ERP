from flask import Blueprint

bp = Blueprint("core", __name__)

from app.blueprints.core import routes  # noqa: E402,F401
