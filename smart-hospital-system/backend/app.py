from flask import Flask, render_template
from backend.routes.patient_routes import patient_bp
from backend.routes.resource_routes import resource_bp
from backend.routes.dashboard_routes import dashboard_bp
from backend.routes.appointment_routes import appointment_bp
from backend.routes.service_routes import service_bp
from backend.routes.chat_routes import chat_bp
from backend.routes.auth_routes import auth_bp, User
from flask_login import LoginManager
from backend.database.db_adapter import get_db_backend
import os

app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static"
)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-123")

# Login Manager Setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"

@login_manager.user_loader
def load_user(user_id):
    db = get_db_backend()
    user_data = db.get_user_by_id(user_id)
    if user_data:
        return User(user_data['id'], user_data['username'], user_data['role'])
    return None

# Configure Cloud Logging
import logging

try:
    if os.environ.get("K_SERVICE") or os.environ.get("GOOGLE_CLOUD_PROJECT"):
        import google.cloud.logging
        client = google.cloud.logging.Client()
        client.setup_logging()
        logging.info("Cloud Logging enabled via google-cloud-logging")
    else:
        logging.basicConfig(level=logging.INFO)
except Exception as e:
    logging.warning(f"Cloud Logging not enabled: {e}")

app.register_blueprint(patient_bp)
app.register_blueprint(resource_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(appointment_bp)
app.register_blueprint(service_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(auth_bp)

from backend.routes.emergency_routes import emergency_bp
app.register_blueprint(emergency_bp)

from backend.routes.admin_routes import admin_bp
app.register_blueprint(admin_bp)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/resources")
def resources():
    return render_template("resources.html")

@app.route("/surgeries")
def surgeries():
    return render_template("surgeries.html")
