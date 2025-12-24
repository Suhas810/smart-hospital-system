
# Mock database for ambulances
ambulances = [
    {"id": "AMB-01", "type": "ALS", "status": "Available", "location": "Hospital Base", "lat": 12.9716, "lng": 77.5946},
    {"id": "AMB-02", "type": "BLS", "status": "Busy", "location": "Sector 4", "lat": 12.9250, "lng": 77.5900},
    {"id": "AMB-03", "type": "ALS", "status": "Available", "location": "Sector 9", "lat": 12.9350, "lng": 77.6100},
    {"id": "AMB-04", "type": "BLS", "status": "Maintenance", "location": "Workshop", "lat": 12.9100, "lng": 77.6000}
]

def get_all_ambulances():
    return ambulances

def get_ambulance_by_id(amb_id):
    return next((a for a in ambulances if a["id"] == amb_id), None)

def update_ambulance_status(amb_id, status, location=None):
    amb = get_ambulance_by_id(amb_id)
    if amb:
        amb["status"] = status
        if location:
            amb["location"] = location
        return True
    return False
