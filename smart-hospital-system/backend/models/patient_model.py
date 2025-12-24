from backend.database.db_adapter import get_db_backend

def init_db():
    get_db_backend().init_db()

def add_patient(name, age, severity, status="waiting", appointment_time=None, risk_analysis=None, **kwargs):
    get_db_backend().add_patient(name, age, severity, status, appointment_time, risk_analysis, **kwargs)

def get_patients():
    return get_db_backend().get_patients()

def update_patient_status(patient_id, status):
    get_db_backend().update_patient_status(patient_id, status)
