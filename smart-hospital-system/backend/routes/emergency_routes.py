from flask import Blueprint, render_template, jsonify, request
from backend.services.emergency_service import calculate_eta, dispatch_nearest_ambulance
from backend.models.ambulance_model import get_all_ambulances
from backend.models.resource_model import get_resources
from backend.services.triage_engine import calculate_priority

from flask_login import login_required

emergency_bp = Blueprint("emergency", __name__, url_prefix="/emergency")

@emergency_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("emergency_dashboard.html")

@emergency_bp.route("/status")
@login_required
def status():
    resources = get_resources()
    ambulances = get_all_ambulances()
    
    # Calculate simple stats
    active_critical = 5 # Mock active critical cases
    
    return jsonify({
        "ambulances": ambulances,
        "emergency_beds": resources.get("emergency_beds", 0),
        "icu_beds": resources.get("beds", 0),
        "oxygen": resources.get("oxygen", 0),
        "ventilators": resources.get("ventilators", 0),
        "active_critical": active_critical
    })

@emergency_bp.route("/dispatch", methods=["POST"])
@login_required
def dispatch():
    data = request.json
    location = data.get("location")
    
    if not location:
        return jsonify({"error": "Location required"}), 400
        
    result = dispatch_nearest_ambulance(location)
    
    if result:
        return jsonify(result)
    else:
        return jsonify({"error": "No ambulances available"}), 404

@emergency_bp.route("/prioritize", methods=["POST"])
@login_required
def prioritize():
    data = request.json
    severity = int(data.get("severity", 1))
    eta = int(data.get("eta", 60))
    
    priority = calculate_priority(severity, eta)
    return jsonify({"priority": priority})
