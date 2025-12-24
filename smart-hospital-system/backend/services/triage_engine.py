def triage_score(age, severity):
    return round((severity * 0.7) + (age * 0.3), 2)

def calculate_priority(severity, eta):
    # Golden Hour Logic: Low ETA + High Severity = Critical Priority
    # Severity 1-10, ETA in mins
    
    score = severity * 10
    
    if eta < 60: # Within Golden Hour
        score += 20
        
    if severity >= 8:
        return "RED"
    elif severity >= 5:
        return "YELLOW"
    else:
        return "GREEN"
