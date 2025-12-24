import random
from backend.models.ambulance_model import get_all_ambulances, update_ambulance_status

def calculate_eta(origin, dest):
    # Simulated logic: Return random ETA between 5-30 mins based on "traffic"
    # In real world: Use Google Maps Distance Matrix API
    base_time = random.randint(5, 25)
    traffic_factor = random.uniform(1.0, 1.5)
    return round(base_time * traffic_factor)

def dispatch_nearest_ambulance(location):
    available = [a for a in get_all_ambulances() if a["status"] == "Available"]
    if not available:
        return None
    
    # Simulating "nearest" by picking first available
    # In real world: Calculate haversine distance
    selected = available[0]
    update_ambulance_status(selected["id"], "Busy", location)
    
    eta = calculate_eta("Hospital", location)
    return {
        "ambulance": selected,
        "eta": eta,
        "message": f"Ambulance {selected['id']} dispatched. ETA: {eta} mins."
    }
