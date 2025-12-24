from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, UserMixin
from backend.database.db_adapter import get_db_backend
import werkzeug.security as ws

auth_bp = Blueprint("auth", __name__)
db = get_db_backend()

class User(UserMixin):
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        user_data = db.get_user_by_username(username)
        if user_data and ws.check_password_hash(user_data['password'], password):
            user = User(user_data['id'], user_data['username'], user_data['role'])
            login_user(user)
            return redirect(url_for("dashboard.dashboard"))
        else:
            flash("Invalid username or password")
            
    return render_template("login.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        # Simple validation
        if not username or not password:
            flash("Please fill all fields")
            return redirect(url_for("auth.register"))

        hashed = ws.generate_password_hash(password)
        if db.create_user(username, hashed):
            flash("Account created! Please login.")
            return redirect(url_for("auth.login"))
        else:
            flash("Username already exists")

    return render_template("register.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))
