def predict_demand(patient_count):
    if patient_count > 10:
        return "HIGH"
    elif patient_count > 5:
        return "MEDIUM"
    return "LOW"
