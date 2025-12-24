from backend.database.db_adapter import get_db_backend
from flask import Blueprint, render_template, request

service_bp = Blueprint("services", __name__)
db = get_db_backend()

@service_bp.route("/doctors")
def doctors():
    query = request.args.get('q')
    if query:
        doctors_list = db.search_doctors(query)
    else:
        doctors_list = db.get_doctors()
        
    return render_template("doctors.html", doctors=doctors_list)

@service_bp.route("/consult")
def consult():
    return render_template("consult.html")

@service_bp.route("/labs")
def labs():
    packages = db.get_lab_packages()
    # DB has: name, tests_count, price, icon (as img), color, icon_color
    # Map 'icon' -> 'img' for template compatibility if needed, 
    # but let's check seed.py. seed uses 'icon'. Template uses 'img'.
    # We should fix dictionary key mapping.
    processed = []
    for p in packages:
        p_dict = dict(p)
        p_dict['img'] = p_dict['icon'] # Map icon column to img key
        processed.append(p_dict)
        
    return render_template("labs.html", packages=processed)

@service_bp.route("/resources")
def resources():
    return render_template("resources.html")

@service_bp.route("/prescription", methods=["GET", "POST"])
def prescription():
    if request.method == "GET":
        return render_template("prescription.html")
        
    if "file" not in request.files:
        return {"error": "No file uploaded"}, 400
        
    file = request.files["file"]
    if file.filename == "":
        return {"error": "No file selected"}, 400
        
    if file:
        from backend.services.vertex_service import VertexGemmaService
        ai_service = VertexGemmaService()
        
        # Read file bytes
        image_bytes = file.read()
        mime_type = file.mimetype
        
        analysis = ai_service.analyze_prescription(image_bytes, mime_type)
        return {"analysis": analysis}
        
    return {"error": "Unknown error"}, 500

@service_bp.route("/consult/room/<int:id>")
def video_room(id):
    # In a real app we would verify if this ID allows a call now
    return render_template("video_room.html", room_id=id)
