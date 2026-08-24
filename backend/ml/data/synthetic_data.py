import random
import pandas as pd
import numpy as np

def generate_synthetic_corridor_dataset(num_samples: int = 5000, seed: int = 42) -> pd.DataFrame:
    """
    Generates a realistic synthetic training dataset representing freight movements
    along the Djibouti Port -> Modjo Dry Port corridor (N1 Highway, 910 km).
    """
    np.random.seed(seed)
    random.seed(seed)

    records = []
    vehicle_types = [1, 2, 3]  # 1: Flatbed, 2: Container, 3: Heavy Refrigerated Tanker
    
    for i in range(num_samples):
        remaining_distance_km = round(random.uniform(20.0, 910.0), 2)
        cargo_weight_tons = round(random.uniform(5.0, 45.0), 1)
        vehicle_type = random.choice(vehicle_types)
        hour_of_day = random.randint(0, 23)
        day_of_week = random.randint(0, 6)
        incident_count = np.random.choice([0, 1, 2, 3], p=[0.70, 0.20, 0.07, 0.03])
        security_risk_level = np.random.choice([0, 1, 2], p=[0.80, 0.15, 0.05])
        
        # Base highway speed: ~60 km/h with noise
        base_speed = random.uniform(52.0, 68.0)
        # Weight penalty: heavier cargo slows speed slightly
        weight_penalty = (cargo_weight_tons / 45.0) * 4.0
        # Night penalty: hours 22-05 lower average speed by 8 km/h
        night_penalty = 8.0 if (hour_of_day >= 22 or hour_of_day <= 5) else 0.0
        
        average_speed_kmh = max(20.0, round(base_speed - weight_penalty - night_penalty + random.gauss(0, 3.0), 1))
        
        # Target remaining travel duration in minutes
        base_travel_minutes = (remaining_distance_km / average_speed_kmh) * 60.0
        delay_minutes = (incident_count * 35.0) + (security_risk_level * 25.0)
        noise_minutes = random.gauss(0, 12.0)
        
        target_remaining_minutes = max(15.0, round(base_travel_minutes + delay_minutes + noise_minutes, 1))

        records.append({
            'remaining_distance_km': remaining_distance_km,
            'cargo_weight_tons': cargo_weight_tons,
            'vehicle_type': vehicle_type,
            'hour_of_day': hour_of_day,
            'day_of_week': day_of_week,
            'incident_count': incident_count,
            'security_risk_level': security_risk_level,
            'average_speed_kmh': average_speed_kmh,
            'target_remaining_minutes': target_remaining_minutes,
        })

    return pd.DataFrame(records)
