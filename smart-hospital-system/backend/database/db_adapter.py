import sqlite3
import os
import logging
from abc import ABC, abstractmethod

# Handle optional imports
try:
    from google.cloud import firestore
except ImportError:
    firestore = None

logger = logging.getLogger(__name__)

class DatabaseBackend(ABC):
    @abstractmethod
    def add_patient(self, name, age, severity, status="waiting", appointment_time=None, risk_analysis=None):
        pass

    @abstractmethod
    def get_patients(self):
        pass

    @abstractmethod
    def update_patient_status(self, patient_id, status):
        pass

    @abstractmethod
    def init_db(self):
        pass

class SQLiteBackend(DatabaseBackend):
    def __init__(self, db_path):
        self.db_path = db_path

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        conn = self._get_conn()
        
        # Patients Table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                age INTEGER,
                severity INTEGER,
                status TEXT DEFAULT 'waiting',
                appointment_time TEXT,
                risk_analysis TEXT
            )
        """)
        
        # Doctors Table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS doctors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                spec TEXT NOT NULL,
                exp TEXT NOT NULL,
                fee TEXT NOT NULL,
                image TEXT DEFAULT 'default_doc.png'
            )
        """)

        # Lab Packages Table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS lab_packages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                tests_count INTEGER NOT NULL,
                price TEXT NOT NULL,
                icon TEXT NOT NULL,
                color TEXT NOT NULL,
                icon_color TEXT NOT NULL
            )
        """)

        # Users Table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'patient'
            )
        """)

        # Migrations
        self._run_migrations(conn)

        conn.commit()
        conn.close()

    def _run_migrations(self, conn):
        try:
            conn.execute("ALTER TABLE patients ADD COLUMN status TEXT DEFAULT 'waiting'")
        except sqlite3.OperationalError: pass
        try:
            conn.execute("ALTER TABLE patients ADD COLUMN appointment_time TEXT")
        except sqlite3.OperationalError: pass
        try:
            conn.execute("ALTER TABLE patients ADD COLUMN risk_analysis TEXT")
        except sqlite3.OperationalError: pass
        try:
            conn.execute("ALTER TABLE patients ADD COLUMN user_id INTEGER")
        except sqlite3.OperationalError: pass
        try:
            conn.execute("ALTER TABLE patients ADD COLUMN doctor_id INTEGER")
        except sqlite3.OperationalError: pass
        try:
            conn.execute("ALTER TABLE patients ADD COLUMN slot TEXT")
        except sqlite3.OperationalError: pass

    def get_doctors(self):
        conn = self._get_conn()
        rows = conn.execute("SELECT * FROM doctors").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_doctor_by_id(self, doctor_id):
        conn = self._get_conn()
        row = conn.execute("SELECT * FROM doctors WHERE id = ?", (doctor_id,)).fetchone()
        conn.close()
        return dict(row) if row else None

    def search_doctors(self, query):
        conn = self._get_conn()
        sql = "SELECT * FROM doctors WHERE name LIKE ? OR spec LIKE ?"
        rows = conn.execute(sql, (f'%{query}%', f'%{query}%')).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_lab_packages(self):
        conn = self._get_conn()
        rows = conn.execute("SELECT * FROM lab_packages").fetchall()
        conn.close()
        return [dict(r) for r in rows]
    
    def create_user(self, username, password, role="patient"):
        try:
            conn = self._get_conn()
            conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_user_by_username(self, username):
        conn = self._get_conn()
        row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()
        return dict(row) if row else None
    
    def get_user_by_id(self, user_id):
        conn = self._get_conn()
        row = conn.execute("SELECT * FROM users WHERE id = ?", (int(user_id),)).fetchone()
        conn.close()
        return dict(row) if row else None

    def add_patient(self, name, age, severity, status="waiting", appointment_time=None, risk_analysis=None, user_id=None, doctor_id=None, slot=None):
        conn = self._get_conn()
        conn.execute(
            "INSERT INTO patients (name, age, severity, status, appointment_time, risk_analysis, user_id, doctor_id, slot) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (name, age, severity, status, appointment_time, risk_analysis, user_id, doctor_id, slot)
        )
        conn.commit()
        conn.close()

    def get_patients(self):
        conn = self._get_conn()
        rows = conn.execute("SELECT * FROM patients").fetchall()
        conn.close()
        return [{
            "id": r["id"], 
            "name": r["name"], 
            "age": r["age"], 
            "severity": r["severity"],
            "status": r["status"],
            "appointment_time": r["appointment_time"],
            "risk_analysis": r["risk_analysis"],
            "user_id": r["user_id"] if "user_id" in r.keys() else None,
            "doctor_id": r["doctor_id"] if "doctor_id" in r.keys() else None,
            "slot": r["slot"] if "slot" in r.keys() else None
        } for r in rows]

    def get_appointments_by_user(self, user_id):
        conn = self._get_conn()
        rows = conn.execute("SELECT * FROM patients WHERE user_id = ?", (user_id,)).fetchall()
        conn.close()
        return [{
            "id": r["id"], 
            "name": r["name"], 
            "age": r["age"], 
            "severity": r["severity"],
            "status": r["status"],
            "appointment_time": r["appointment_time"],
            "risk_analysis": r["risk_analysis"],
            "doctor_id": r["doctor_id"] if "doctor_id" in r.keys() else None,
            "slot": r["slot"] if "slot" in r.keys() else None
        } for r in rows]

    def get_patient(self, patient_id):
        conn = self._get_conn()
        row = conn.execute("SELECT * FROM patients WHERE id = ?", (patient_id,)).fetchone()
        conn.close()
        if not row: return None
        r = row
        return {
            "id": r["id"], 
            "name": r["name"], 
            "age": r["age"], 
            "severity": r["severity"],
            "status": r["status"],
            "appointment_time": r["appointment_time"],
            "risk_analysis": r["risk_analysis"],
            "user_id": r["user_id"] if "user_id" in r.keys() else None,
            "doctor_id": r["doctor_id"] if "doctor_id" in r.keys() else None,
            "slot": r["slot"] if "slot" in r.keys() else None
        }

    def update_patient_status(self, patient_id, status):
        conn = self._get_conn()
        conn.execute("UPDATE patients SET status = ? WHERE id = ?", (status, patient_id))
        conn.commit()
        conn.close()

class FirestoreBackend(DatabaseBackend):
    def __init__(self):
        self.db = firestore.Client()
        self.collection = self.db.collection('patients')

    def init_db(self):
        # No schema initialization needed for Firestore
        pass

    def add_patient(self, name, age, severity, status="waiting", appointment_time=None, risk_analysis=None):
        self.collection.add({
            "name": name,
            "age": age,
            "severity": severity,
            "status": status,
            "appointment_time": appointment_time,
            "risk_analysis": risk_analysis,
            "timestamp": firestore.SERVER_TIMESTAMP
        })

    def update_patient_status(self, patient_id, status):
        # Firestore implementation for completeness
        try:
            self.collection.document(patient_id).update({"status": status})
        except Exception:
            pass

    def get_patients(self):
        docs = self.collection.stream()
        patients = []
        for doc in docs:
            d = doc.to_dict()
            d['id'] = doc.id
            patients.append(d)
        return patients

# Global instance
_db_instance = None

def get_db_backend():
    global _db_instance
    if _db_instance:
        return _db_instance

    # Check environment
    is_cloud_run = os.environ.get('K_SERVICE') is not None
    use_firestore = os.environ.get('USE_FIRESTORE', 'false').lower() == 'true'

    if (is_cloud_run or use_firestore) and firestore:
        try:
            logger.info("Initializing Firestore Backend")
            _db_instance = FirestoreBackend()
        except Exception as e:
            logger.error(f"Failed to init Firestore: {e}. Falling back to SQLite.")
            _db_instance = SQLiteBackend("backend/database/sample_data.db")
    else:
        logger.info("Initializing SQLite Backend")
        _db_instance = SQLiteBackend("backend/database/sample_data.db")
    
    return _db_instance
