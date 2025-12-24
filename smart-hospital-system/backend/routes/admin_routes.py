from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from backend.database.db_adapter import get_db_backend

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")
db = get_db_backend()

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash("You do not have permission to access this page.")
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route("/")
@login_required
@admin_required
def dashboard():
    doctors = db.get_doctors()
    patients = db.get_patients() # This is the full list
    
    # Calculate stats
    total_patients = len(patients)
    total_doctors = len(doctors)
    active_now = len([p for p in patients if p['status'] == 'waiting'])
    
    return render_template("admin_dashboard.html", 
                         doctors=doctors,
                         stats={
                             "patients": total_patients,
                             "doctors": total_doctors,
                             "active": active_now
                         })

@admin_bp.route("/resource/update", methods=["POST"])
@login_required
@admin_required
def update_resource():
    # Placeholder for resource update logic
    # In a real app we would update the DB. For now, we just flash a message.
    # Because resources are currently mock data or served via resource_routes.
    flash("Resource updated successfully!")
    return redirect(url_for("admin.dashboard"))
