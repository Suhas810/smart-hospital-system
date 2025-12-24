def get_ai_advice(age, severity):
    # Hackathon-safe simulated Gemma response
    if severity >= 8:
        return "Immediate ICU attention required."
    elif severity >= 5:
        return "Monitor closely and allocate resources."
    return "Routine observation recommended."
