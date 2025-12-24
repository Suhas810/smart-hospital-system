from flask import Blueprint, request, jsonify, render_template
from backend.models.patient_model import add_patient, get_patients
from backend.database.db_adapter import get_db_backend
from datetime import datetime
from flask_login import current_user, login_required

appointment_bp = Blueprint("appointments", __name__, url_prefix="/appointments")
db = get_db_backend()

@appointment_bp.route("/book/<int:doctor_id>", methods=["GET"])
@login_required
def booking_page(doctor_id):
    doctor = db.get_doctor_by_id(doctor_id)
    if not doctor:
        return "Doctor not found", 404
        
    # Generate mock slots
    import random
    slots = ["10:00 AM", "10:30 AM", "11:00 AM", "11:30 AM", 
             "02:00 PM", "02:30 PM", "03:00 PM", "03:30 PM"]
    # Randomly disable some? Nah, keep simple.
    
    return render_template("book_appointment.html", doctor=doctor, slots=slots)

@appointment_bp.route("/download/<int:appointment_id>")
@login_required
def download_report(appointment_id):
    appointment = db.get_patient(appointment_id)
    if not appointment:
        return "Appointment not found", 404
        
    # Check ownership (simple check)
    if appointment.get('user_id') != current_user.id:
        return "Unauthorized", 403

    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from io import BytesIO
    from flask import send_file

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Header
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, 750, "SmartHospital - Medical Appointment Record")
    
    p.setFont("Helvetica", 12)
    p.drawString(50, 720, f"Date: {appointment['appointment_time'][:10]}")
    p.drawString(50, 700, f"Patient Name: {appointment['name']}")
    p.drawString(50, 680, f"Age: {appointment['age']}")
    p.drawString(50, 660, f"Doctor ID: {appointment.get('doctor_id', 'N/A')}")
    p.drawString(50, 640, f"Slot: {appointment.get('slot', 'N/A')}")
    
    p.line(50, 620, 550, 620)
    
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, 590, "AI Triage Analysis")
    p.setFont("Helvetica", 11)
    
    analysis = appointment.get('risk_analysis')
    y = 570
    if analysis:
        # Simple text wrapping could be better, but this suffices for a prototype
        text = str(analysis)
        # Split by comma or naive wrap
        for line in text.split(','):
            p.drawString(50, y, line.strip())
            y -= 20
            
    p.setFont("Helvetica-Oblique", 10)
    p.drawString(50, 100, "This is a computer generated report.")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"report_{appointment_id}.pdf", mimetype='application/pdf')


@appointment_bp.route("/book", methods=["POST"])
def book_appointment():
    data = request.json
    name = data.get("name")
    age = data.get("age")
    severity = int(data.get("severity", 1))
    appointment_time = data.get("appointment_time", datetime.now().isoformat())
    
    # New Fields
    doctor_id = data.get("doctor_id")
    slot = data.get("slot") # e.g. "10:30 AM"

    # Capture logged-in user ID if available
    user_id = current_user.id if current_user.is_authenticated else None
    
    # Integrated AI Triage
    from backend.services.vertex_service import VertexGemmaService
    import json
    
    ai_service = VertexGemmaService()
    analysis = ai_service.analyze_risk(data)
    
    db.add_patient(
        name=name, 
        age=age, 
        severity=severity, 
        status="booked", 
        appointment_time=appointment_time,
        risk_analysis=json.dumps(analysis),
        user_id=user_id,
        doctor_id=doctor_id,
        slot=slot
    )
    
    return jsonify({
        "message": "Appointment booked successfully", 
        "status": "booked",
        "ai_analysis": analysis
    })

@appointment_bp.route("/queue", methods=["GET"])
def get_queue():
    """
    Returns the priority queue.
    Sorting Logic:
    1. Severity (High to Low)
    2. Appointment Time (Earliest first)
    """
    patients = get_patients()
    
    # Filter for active patients (waiting or booked)
    active_queue = [p for p in patients if p.get('status') in ['waiting', 'booked']]
    
    sorted_queue = sorted(
        active_queue, 
        key=lambda x: (-x['severity'], x.get('appointment_time') or "")
    )
    
    return jsonify(sorted_queue)

@appointment_bp.route("/my", methods=["GET"])
@login_required
def my_appointments():
    appointments = db.get_appointments_by_user(current_user.id)
    return render_template("my_appointments.html", appointments=appointments)
