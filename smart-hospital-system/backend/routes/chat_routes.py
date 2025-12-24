from flask import Blueprint, request, jsonify
from backend.services.vertex_service import VertexGemmaService

chat_bp = Blueprint("chat", __name__, url_prefix="/chat")
ai_service = VertexGemmaService()

@chat_bp.route("/message", methods=["POST"])
def message():
    data = request.json
    user_msg = data.get("message", "")
    
    if not user_msg:
        return jsonify({"reply": "Please say something!"})
        
    reply = ai_service.chat(user_msg)
    return jsonify({"reply": reply})
