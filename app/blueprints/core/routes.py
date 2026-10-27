from flask import jsonify

from app.blueprints.core import bp


@bp.get("/health")
def health():
    return jsonify(status="ok")
