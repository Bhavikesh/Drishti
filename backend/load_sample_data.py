"""
Load rich, interconnected synthetic crime data into Supabase + ChromaDB
Designed to make the hackathon demo look impressive
"""
import random
from datetime import datetime, timedelta
from database import get_db_connection
import rag_pipeline
import pandas as pd

# === Karnataka-specific realistic data ===

DISTRICTS = ['Bengaluru Urban', 'Mysuru', 'Mangaluru', 'Hubli-Dharwad', 'Belagavi',
             'Kalaburagi', 'Vijayapura', 'Tumakuru', 'Shivamogga', 'Ballari']

POLICE_STATIONS = {
    'Bengaluru Urban': ['Indiranagar PS', 'Koramangala PS', 'Whitefield PS', 'HSR Layout PS', 'JP Nagar PS', 'Marathahalli PS', 'Electronic City PS', 'Yelahanka PS', 'Jayanagar PS', 'Rajajinagar PS'],
    'Mysuru': ['Vijayanagar PS', 'Kuvempunagar PS', 'Nazarbad PS', 'Devaraja PS', 'Jayalakshmipuram PS', 'Udayagiri PS', 'Saraswathipuram PS', 'Lashkar Mohalla PS'],
    'Mangaluru': ['Barke PS', 'Kadri PS', 'Mangaluru North PS', 'Mangaluru South PS', 'Surathkal PS', 'Ullal PS'],
    'Hubli-Dharwad': ['Hubli Old PS', 'Hubli New PS', 'Dharwad PS', 'Keshwapur PS', 'Vidyanagar PS'],
    'Belagavi': ['Camp PS', 'Market PS', 'Tilakwadi PS', 'Shahapur PS', 'Khade Bazaar PS'],
    'Kalaburagi': ['Brahmapur PS', 'Chowk PS', 'Station Bazaar PS', 'Supermarket PS'],
    'Vijayapura': ['City PS', 'Bagevadi PS', 'Indi PS', 'Muddebihal PS'],
    'Tumakuru': ['Town PS', 'Kyatsandra PS', 'Sira PS', 'Madhugiri PS'],
    'Shivamogga': ['Doddapet PS', 'Vinobhanagar PS', 'Bhadravathi PS', 'Shimoga Rural PS'],
    'Ballari': ['Gandhinagar PS', 'Cowl Bazaar PS', 'Hospet PS', 'Sandur PS'],
}

CRIME_TYPES = ['Theft', 'Burglary', 'Assault', 'Robbery', 'Fraud', 'Cybercrime',
               'Drug Trafficking', 'Vehicle Theft', 'Chain Snatching', 'Murder']

# Weighted distribution — Mysuru gets more burglaries, Bengaluru more thefts
DISTRICT_CRIME_WEIGHTS = {
    'Bengaluru Urban': {'Theft': 0.25, 'Cybercrime': 0.15, 'Vehicle Theft': 0.15, 'Chain Snatching': 0.10, 'Fraud': 0.10, 'Robbery': 0.05, 'Assault': 0.05, 'Burglary': 0.05, 'Drug Trafficking': 0.05, 'Murder': 0.05},
    'Mysuru': {'Burglary': 0.30, 'Theft': 0.15, 'Chain Snatching': 0.12, 'Assault': 0.10, 'Robbery': 0.08, 'Fraud': 0.08, 'Vehicle Theft': 0.07, 'Cybercrime': 0.05, 'Drug Trafficking': 0.03, 'Murder': 0.02},
}

CRIMINAL_NAMES = [
    'Amit Kumar', 'Ravi Sharma', 'Suresh Patil', 'Manoj Gowda', 'Rajesh Naik',
    'Deepak Shetty', 'Kiran Rao', 'Venkatesh Reddy', 'Prakash Jain', 'Arun Hegde',
    'Sanjay Deshpande', 'Naveen Kulkarni', 'Vijay Hosamani', 'Santosh Mane', 'Ramesh Bhat',
    'Ganesh Poojari', 'Harish Suvarna', 'Mahesh Acharya', 'Dinesh Prabhu', 'Umesh Kamat',
    'Anand Shenoy', 'Prasad Nayak', 'Sachin Devadiga', 'Mohan Amin', 'Jagadish Pujar',
    'Basavaraj Hiremath', 'Shivaraj Kumbar', 'Mallikarjun Swamy', 'Fakkiresh Kattimani', 'Channappa Hoogar',
    'Raju Singh', 'Imran Khan', 'Farhan Sheikh', 'Abdul Razak', 'Mohammed Hussain',
    'Priya Devi', 'Lakshmi Bai', 'Kavitha Shetty', 'Meena Kumari', 'Sunitha Rao',
    'Rekha Gowda', 'Savitha Naik', 'Manjula Patil', 'Shobha Reddy', 'Geeta Sharma',
    'Nithin Shetty', 'Rakesh Bhandary', 'Sunil Pinto', 'Joseph D\'Souza', 'Michael Lobo',
]

# Shared phone numbers (to create network links)
SHARED_PHONES = [
    '9845012345', '9901234567', '8861234567', '7760012345', '9880067890',
    '8884456789', '9632145678', '8792345678', '9741234567', '8553456789',
]

DESCRIPTIONS = {
    'Theft': [
        'Suspect broke into residential premises and stole electronics worth ₹2.5 lakhs. Fingerprints recovered from the scene.',
        'Mobile phone theft reported at commercial complex. CCTV footage shows suspect fleeing on two-wheeler.',
        'Gold jewelry stolen from locked almirah. Servant suspected. Investigation underway.',
        'Laptop and cash stolen from IT professional\'s apartment during daytime. Door lock was picked.',
        'Theft of copper wiring from construction site. Security guard was found absent from duty.',
    ],
    'Burglary': [
        'Commercial establishment broken into at night. Safe cracked and ₹8 lakhs cash stolen. Professional job suspected.',
        'Residential burglary in gated community. Multiple houses targeted on same night. Gang operation suspected.',
        'Warehouse burglary. Electronic goods worth ₹15 lakhs missing. Entry through ventilation shaft.',
        'Jewellery shop burglary. Alarm system was disabled. Insider involvement suspected.',
        'Series of house break-ins in residential area. MO matches known offender Amit Kumar.',
    ],
    'Assault': [
        'Victim attacked with iron rod during argument over property dispute. Hospitalized with head injuries.',
        'Domestic violence case. Victim sustained multiple injuries. Suspect fled after incident.',
        'Group assault during local festival. Five persons injured. Communal angle ruled out.',
        'Road rage incident escalated to physical assault. Both parties sustained injuries. FIR registered.',
    ],
    'Robbery': [
        'Armed robbery at jewelry store in broad daylight. Suspects wore masks and carried country-made pistols.',
        'ATM robbery. Guard tied up, cash tray emptied. Vehicle used was found abandoned 2 km away.',
        'Highway robbery. Truck driver robbed of ₹3 lakhs. Gang used spike strip to stop the vehicle.',
        'Daylight robbery at bank. Three armed suspects held staff at gunpoint. Dye pack activated.',
    ],
    'Fraud': [
        'Online investment fraud. Victim lost ₹12 lakhs through fake cryptocurrency scheme operated via WhatsApp.',
        'Real estate fraud. Forged documents used to sell same property to multiple buyers. ₹45 lakhs involved.',
        'Insurance fraud ring busted. Staged accidents to claim medical insurance. 8 persons involved.',
        'UPI fraud. Victim tricked into sharing OTP, ₹1.5 lakhs debited from account.',
    ],
    'Cybercrime': [
        'Phishing attack targeting bank customers. 200+ accounts compromised. International server traced.',
        'Ransomware attack on hospital network. Patient records encrypted. ₹50 lakh ransom demanded in Bitcoin.',
        'Social media impersonation. Fake profile used to extract money from victim\'s contacts.',
        'Sextortion case. Victim blackmailed through morphed photos. Suspect traced to different state.',
    ],
    'Drug Trafficking': [
        'Major drug bust at highway checkpoint. 10 kg ganja and 500 grams MDMA seized. Interstate racket busted.',
        'Drug peddling ring operating near college campus. 5 suspects arrested with synthetic drugs.',
        'Cannabis cultivation discovered in farmland. 2 acres of plantation destroyed. Owner arrested.',
        'Cocaine smuggling via courier service. International connection suspected. NCB informed.',
    ],
    'Vehicle Theft': [
        'Luxury car stolen from mall parking using relay attack on keyless entry. Vehicle tracked to chop shop.',
        'Organised bike theft gang busted. 25 stolen two-wheelers recovered. Vehicles were being re-registered.',
        'Auto-rickshaw stolen for use in chain snatching. Recovered with modified number plate.',
        'Car theft syndicate dismantled. Operating across 3 districts. 12 vehicles recovered.',
    ],
    'Chain Snatching': [
        'Gold chain snatched from elderly woman near temple. Two suspects on high-speed motorcycle identified.',
        'Series of chain snatchings in market area. 5 incidents in one week. Same MO — pillion rider snatches.',
        'Tourist targeted for chain snatching near heritage site. Suspects fled towards highway.',
        'Chain snatching attempt foiled by alert public. Suspect caught and handed over to police.',
    ],
    'Murder': [
        'Homicide linked to property dispute. Victim found with stab wounds. Family member is prime suspect.',
        'Contract killing suspected. Victim was a local businessman with pending litigation. Supari gang angle.',
        'Body found in lake. Post-mortem reveals blunt force trauma. Investigation ongoing.',
        'Murder during attempted robbery. Shop owner killed while resisting. Two suspects identified from CCTV.',
    ],
}


def weighted_crime_type(district):
    """Pick a crime type with district-specific weighting"""
    if district in DISTRICT_CRIME_WEIGHTS:
        weights = DISTRICT_CRIME_WEIGHTS[district]
        return random.choices(list(weights.keys()), weights=list(weights.values()))[0]
    return random.choice(CRIME_TYPES)


def generate_escalation_dates():
    """Generate dates with an escalation pattern for predictions to detect"""
    dates = []
    base = datetime(2024, 1, 1)
    # Increasing crime rate over months
    monthly_counts = [15, 18, 22, 28, 25, 30, 35, 32, 40, 38, 45, 50]
    for month_idx, count in enumerate(monthly_counts):
        for _ in range(count):
            day = random.randint(1, 28)
            dates.append(base + timedelta(days=month_idx * 30 + day))
    # Add 2025 data with continued trend
    for month_idx in range(6):
        count = 50 + month_idx * 5 + random.randint(-5, 5)
        for _ in range(count):
            day = random.randint(1, 28)
            dates.append(datetime(2025, month_idx + 1, 1) + timedelta(days=day))
    return dates


def load_data():
    conn = get_db_connection()
    if not conn:
        print("❌ Failed to connect to database.")
        return

    cur = conn.cursor()

    try:
        # ===== 1. Police Stations =====
        print("📍 Loading police stations...")
        station_id_map = {}
        station_id = 1
        for district, stations in POLICE_STATIONS.items():
            for station_name in stations:
                lat = 12.97 + random.uniform(-2.5, 2.5)
                lng = 77.59 + random.uniform(-2.5, 2.5)
                cur.execute(
                    "INSERT INTO police_stations (id, name, district, lat, lng) VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
                    (station_id, station_name, district, lat, lng)
                )
                station_id_map[(district, station_name)] = station_id
                station_id += 1

        # ===== 2. Criminals (with shared phones for networks) =====
        print("👤 Loading criminals...")
        criminals = []
        for i, name in enumerate(CRIMINAL_NAMES):
            age = random.randint(20, 55)
            gender = 'Female' if name.split()[0] in ['Priya', 'Lakshmi', 'Kavitha', 'Meena', 'Sunitha', 'Rekha', 'Savitha', 'Manjula', 'Shobha', 'Geeta'] else 'Male'
            history_count = random.choices([1, 2, 3, 5, 7, 10, 15], weights=[30, 20, 15, 12, 10, 8, 5])[0]
            is_repeat = history_count >= 5
            # Assign shared phones to create network links
            phone = SHARED_PHONES[i % len(SHARED_PHONES)] if i < 30 else f'98{random.randint(10000000, 99999999)}'
            first_offense = (datetime.now() - timedelta(days=random.randint(365, 2000))).strftime('%Y-%m-%d')

            cur.execute(
                """INSERT INTO criminals (id, name, age, gender, phone, criminal_history_count, is_repeat_offender, first_offense_date) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING""",
                (i + 1, name, age, gender, phone, history_count, is_repeat, first_offense)
            )
            criminals.append({
                'id': i + 1, 'name': name, 'history_count': history_count,
                'is_repeat': is_repeat, 'phone': phone
            })

        # ===== 3. Crimes (500 records with escalation pattern) =====
        print("🔍 Loading crimes...")
        crime_dates = generate_escalation_dates()
        statuses = ['Under Investigation', 'Closed', 'Solved', 'Pending', 'Cold Case']
        crimes_for_chroma = []

        for i in range(min(500, len(crime_dates))):
            district = random.choice(DISTRICTS)
            crime_type = weighted_crime_type(district)
            stations = POLICE_STATIONS.get(district, ['Town PS'])
            station_name = random.choice(stations)
            station_id = station_id_map.get((district, station_name), 1)
            crime_date = crime_dates[i].strftime('%Y-%m-%d')
            status = random.choices(statuses, weights=[30, 25, 20, 15, 10])[0]
            description = random.choice(DESCRIPTIONS[crime_type])
            is_resolved = status in ['Closed', 'Solved']
            resolution_date = (crime_dates[i] + timedelta(days=random.randint(5, 90))).strftime('%Y-%m-%d') if is_resolved else None
            case_id = f"KSP/2024/{str(i + 1).zfill(4)}"

            # Location near station
            lat = 12.97 + random.uniform(-2, 2)
            lng = 77.59 + random.uniform(-2, 2)

            cur.execute(
                """INSERT INTO crimes (id, case_id, crime_date, district, police_station_id, crime_type, description, status, lat, lng, is_resolved, resolution_date) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (case_id) DO NOTHING""",
                (i + 1, case_id, crime_date, district, station_id, crime_type, description, status, lat, lng, is_resolved, resolution_date)
            )

            crimes_for_chroma.append({
                'id': i + 1, 'case_id': case_id, 'crime_type': crime_type,
                'district': district, 'crime_date': crime_date,
                'description': description, 'status': status,
                'station': station_name
            })

        # ===== 4. Crime-Criminal Links (create networks) =====
        print("🕸️ Creating criminal networks...")
        link_id = 1
        roles = ['Accused', 'Suspect', 'Accomplice', 'Mastermind', 'Informant']

        # Create deliberate networks: groups of criminals linked to same crimes
        # Network 1: Amit Kumar + Ravi Sharma + Suresh Patil (Burglary gang in Mysuru)
        network_groups = [
            ([1, 2, 3], list(range(1, 30)), 'Mysuru Burglary Gang'),  # criminals 1-3 share crimes
            ([4, 5, 6], list(range(30, 55)), 'Hubli Theft Ring'),
            ([7, 8, 9, 10], list(range(55, 80)), 'Bengaluru Cyber Fraud Ring'),
            ([11, 12], list(range(80, 95)), 'Drug Trafficking Duo'),
            ([13, 14, 15], list(range(95, 115)), 'Chain Snatching Gang'),
        ]

        for criminal_ids, crime_range, gang_name in network_groups:
            for crime_id in crime_range:
                if crime_id > 500:
                    break
                # Each crime gets 1-3 criminals from the group
                involved = random.sample(criminal_ids, min(len(criminal_ids), random.randint(1, 3)))
                for crim_id in involved:
                    role = random.choice(roles)
                    cur.execute(
                        "INSERT INTO crime_criminal_links (id, crime_id, criminal_id, role) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING",
                        (link_id, crime_id, crim_id, role)
                    )
                    link_id += 1

        # Random links for remaining criminals
        for crim in criminals[15:]:
            num_crimes = random.randint(1, crim['history_count'])
            linked_crimes = random.sample(range(1, 501), min(num_crimes, 500))
            for crime_id in linked_crimes:
                cur.execute(
                    "INSERT INTO crime_criminal_links (id, crime_id, criminal_id, role) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING",
                    (link_id, crime_id, crim['id'], random.choice(roles))
                )
                link_id += 1

        conn.commit()
        print(f"✅ Loaded into Supabase: {station_id - 1} stations, {len(criminals)} criminals, 500 crimes, {link_id - 1} links")

        # ===== 5. Load into ChromaDB for RAG =====
        print("📚 Loading into ChromaDB for RAG pipeline...")
        df = pd.DataFrame(crimes_for_chroma)
        rag_pipeline.embed_and_store_crimes(df)
        print(f"✅ Loaded {len(df)} crime records into ChromaDB!")

        # Quick test
        print("\n🔍 Testing RAG retrieval...")
        results = rag_pipeline.retrieve_relevant_crimes("burglary hotspots in Mysuru")
        print(f"   Found {len(results['documents'][0])} relevant results for 'burglary hotspots in Mysuru'")

    except Exception as e:
        print(f"❌ Error loading data: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    load_data()
