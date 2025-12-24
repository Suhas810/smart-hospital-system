def staffing_advice(demand):
    if demand == "HIGH":
        return "Call additional staff"
    elif demand == "MEDIUM":
        return "Maintain current staffing"
    return "Normal staffing sufficient"
