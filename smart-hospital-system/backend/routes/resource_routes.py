from flask import Blueprint, jsonify
from backend.models.resource_model import get_resources

resource_bp = Blueprint("resources", __name__, url_prefix="/resources")

@resource_bp.route("/status")
def status():
    return jsonify(get_resources())
