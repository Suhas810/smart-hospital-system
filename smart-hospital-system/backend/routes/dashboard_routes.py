from flask import Blueprint, jsonify
from backend.models.patient_model import get_patients
from backend.services.demand_prediction import predict_demand
from backend.services.staff_scheduler import staffing_advice
from backend.services.gemma_ai import get_ai_advice

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")

@dashboard_bp.route("/summary")
def summary():
    patients = get_patients()
    count = len(patients)
    demand = predict_demand(count)

    return jsonify({
        "total_patients": count,
        "predicted_demand": demand,
        "staffing_advice": staffing_advice(demand)
    })

@dashboard_bp.route("/ai")
def ai_summary():
    return jsonify({
        "ai_advice": get_ai_advice(age=62, severity=8)
    })
