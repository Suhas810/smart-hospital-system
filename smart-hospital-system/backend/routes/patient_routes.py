from flask import Blueprint, request, jsonify
from backend.models.patient_model import add_patient, get_patients, init_db

patient_bp = Blueprint("patients", __name__, url_prefix="/patients")
init_db()

@patient_bp.route("/add", methods=["POST"])
def add():
    data = request.json
    name = data.get("name")
    age = data.get("age")
    severity = data.get("severity")

    # AI Analysis
    from backend.services.vertex_service import VertexGemmaService
    ai_service = VertexGemmaService()
    analysis = ai_service.analyze_risk(data)
    
    # We should probably store the comprehensive analysis, but for now we follow existing schema
    # Or, preferably, we update the schema.
    # Let's stick to existing arguments for now but log the AI output
    print(f"AI Analysis for {name}: {analysis}")

    add_patient(name, age, severity)
    
    return jsonify({
        "message": "Patient added successfully", 
        "ai_analysis": analysis
    })

@patient_bp.route("/list")
def list_patients():
    patients = get_patients()
    return jsonify([dict(p) for p in patients])
