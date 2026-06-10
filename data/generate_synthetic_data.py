import pandas as pd
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker('en_IN')

# Generate 1100 police stations
stations = []
districts = ['Bengaluru Urban', 'Bengaluru Rural', 'Mysore', 'Hubli', 'Belagavi', 
             'Mangalore', 'Kalaburagi', 'Dharwad', 'Shivamogga', 'Tumakuru']

for i in range(1100):
    stations.append({
        'id': i+1,
        'name': f"{fake.city()} Police Station",
        'district': random.choice(districts),
        'lat': 12.97 + random.uniform(-2, 2),
        'lng': 77.59 + random.uniform(-2, 2)
    })

# Generate 50,000 crimes
crime_types = ['theft', 'murder', 'assault', 'robbery', 'rape', 'fraud', 'accident']
crimes = []
start_date = datetime(2020, 1, 1)

for i in range(50000):
    crime_date = start_date + timedelta(days=random.randint(0, 2000))
    district = random.choice(districts)
    crimes.append({
        'id': i+1,
        'case_id': f"CRIME{str(i+1).zfill(6)}",
        'crime_date': crime_date,
        'district': district,
        'crime_type': random.choice(crime_types),
        'status': random.choice(['open', 'closed', 'under investigation']),
        'is_resolved': random.choice([True, False])
    })

# Save to CSV
pd.DataFrame(stations).to_csv('stations.csv', index=False)
pd.DataFrame(crimes).to_csv('crimes.csv', index=False)
print("✅ Synthetic data generated: 1100 stations, 50,000 crimes")
