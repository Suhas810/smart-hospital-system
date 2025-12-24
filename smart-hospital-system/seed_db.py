from backend.database.db_adapter import get_db_backend, SQLiteBackend
import sqlite3

def seed_data():
    db = get_db_backend()
    if not isinstance(db, SQLiteBackend):
        print("Seeding only supported for SQLite currently.")
        return

    conn = db._get_conn()
    
    # 1. Doctors
    conn.execute("DELETE FROM doctors") # Clear existing
    doctors = [
        ("Dr. A. Sharma", "Cardiologist", "15 years", "₹800", "default.png"),
        ("Dr. P. Verma", "Dentist", "8 years", "₹500", "default.png"),
        ("Dr. K. Singh", "General Physician", "12 years", "₹400", "default.png"),
        ("Dr. R. Gupta", "Orthopedist", "20 years", "₹1000", "default.png")
    ]
    conn.executemany("INSERT INTO doctors (name, spec, exp, fee, image) VALUES (?, ?, ?, ?, ?)", doctors)
    print(f"Seeded {len(doctors)} doctors.")

    # 2. Lab Packages
    conn.execute("DELETE FROM lab_packages")
    packages = [
        ("Full Body Checkup", 75, "₹1499", "fa-heartbeat", "#e0f2fe", "#0284c7"),
        ("Diabetes Screening", 45, "₹999", "fa-tint", "#fce7f3", "#db2777"),
        ("Thyroid Profile", 3, "₹499", "fa-dna", "#fef3c7", "#d97706")
    ]
    conn.executemany("INSERT INTO lab_packages (name, tests_count, price, icon, color, icon_color) VALUES (?, ?, ?, ?, ?, ?)", packages)
    print(f"Seeded {len(packages)} lab packages.")

    # 3. Users (Admin)
    from werkzeug.security import generate_password_hash
    conn.execute("DELETE FROM users WHERE username='admin'")
    admin_hash = generate_password_hash("admin123")
    conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ("admin", admin_hash, "admin"))
    print("Seeded admin user.")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    seed_data()
