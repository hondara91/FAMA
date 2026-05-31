from flask import Blueprint, render_template

from utils.db import check_mongo_connection

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """Muestra el estado inicial de Flask y MongoDB."""
    mongo_ok, mongo_message = check_mongo_connection()

    return render_template(
        "index.html",
        mongo_ok=mongo_ok,
        mongo_message=mongo_message,
    )
