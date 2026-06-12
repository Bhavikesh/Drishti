"""
Load sample crime data into ChromaDB for RAG pipeline
"""
import pandas as pd
from datetime import datetime, timedelta
import random
import rag_pipeline

# Sample crime data for Karnataka State Police
crime_types = ['Theft', 'Burglary', 'Assault', 'Robbery', 'Fraud', 'Cybercrime', 'Drug Trafficking', 'Vehicle Theft', 'Chain Snatching', 'Murder']
districts = ['Bengaluru Urban', 'Mysuru', 'Mangaluru', 'Hubli', 'Belagavi', 'Kalaburagi', 'Vijayapura', 'Dharwad', 'Tumakuru', 'Shivamogga']
statuses = ['Under Investigation', 'Closed', 'Solved', 'Pending', 'Cold Case']

descriptions = {
    'Theft': [
        'Suspect broke into residential premises through window. Electronics and jewelry stolen.',
        'Shop theft reported. Cash drawer emptied during business hours.',
        'Bike theft from parking lot. CCTV footage shows two suspects.',
        'House burglary while owners were away. Forced entry through back door.'
    ],
    'Burglary': [
        'Commercial establishment broken into at night. Safe cracked open.',
        'Residential burglary. Multiple houses in the same street targeted.',
        'Warehouse burglary. Large quantity of goods stolen.',
        'ATM burglary attempt. Suspects fled after alarm triggered.'
    ],
    'Assault': [
        'Physical altercation between two individuals. Victim hospitalized.',
        'Domestic violence case reported. Suspect arrested.',
        'Street fight escalated. Multiple injuries reported.',
        'Bar brawl resulted in serious injuries. Three suspects identified.'
    ],
    'Robbery': [
        'Armed robbery at jewelry store. Two suspects with weapons.',
        'Bank robbery thwarted. Suspects arrested at scene.',
        'Street robbery. Victim attacked and phone stolen.',
        'Gas station robbery. Cashier threatened at gunpoint.'
    ],
    'Fraud': [
        'Online financial fraud. Victim lost money through fake investment scheme.',
        'Credit card fraud detected. Multiple unauthorized transactions.',
        'Insurance fraud investigation ongoing. Fabricated claim suspected.',
        'Property fraud case. Fake documents used in land transaction.'
    ],
    'Cybercrime': [
        'Phishing attack reported. Multiple victims banking credentials stolen.',
        'Social media account hacking. Personal information leaked.',
        'Online scam. Fake e-commerce website defrauded customers.',
        'Ransomware attack on local business. Data encrypted by attackers.'
    ],
    'Drug Trafficking': [
        'Drug peddling racket busted. 5kg of contraband seized.',
        'Interstate drug trafficking operation intercepted at checkpoint.',
        'Narcotic substances found during raid. Two suspects arrested.',
        'Drug distribution network dismantled. Multiple arrests made.'
    ],
    'Vehicle Theft': [
        'Car theft from residential area. Vehicle tracked and recovered.',
        'Multiple bike thefts reported in same locality. Pattern identified.',
        'Auto rickshaw theft. Suspect caught on CCTV.',
        'Luxury car stolen from mall parking. Investigation ongoing.'
    ],
    'Chain Snatching': [
        'Chain snatching on busy street. Two men on bike fled scene.',
        'Gold chain snatched from elderly woman. Suspects identified from CCTV.',
        'Series of chain snatchings reported in market area. Special patrol deployed.',
        'Chain snatching attempt foiled by public. Suspect caught and handed to police.'
    ],
    'Murder': [
        'Homicide case under investigation. Suspect in custody.',
        'Murder investigation reveals family dispute. Confession obtained.',
        'Body found in secluded area. Post-mortem conducted.',
        'Murder case solved. Accused arrested based on forensic evidence.'
    ]
}

# Generate sample crime records
crimes = []
for i in range(100):
    crime_type = random.choice(crime_types)
    district = random.choice(districts)
    status = random.choice(statuses)
    crime_date = (datetime.now() - timedelta(days=random.randint(1, 365))).strftime('%Y-%m-%d')
    description = random.choice(descriptions[crime_type])
    
    crimes.append({
        'id': i + 1,
        'case_id': f'KSP/{datetime.now().year}/{str(i+1).zfill(4)}',
        'crime_type': crime_type,
        'district': district,
        'crime_date': crime_date,
        'status': status,
        'description': description
    })

# Create DataFrame
df = pd.DataFrame(crimes)

# Load into ChromaDB
print("Loading sample crime data into ChromaDB...")
rag_pipeline.embed_and_store_crimes(df)
print(f"✅ Successfully loaded {len(df)} crime records into ChromaDB!")
print(f"📁 Database location: {rag_pipeline.CHROMA_PATH}")

# Test retrieval
print("\n🔍 Testing retrieval with sample query...")
results = rag_pipeline.retrieve_relevant_crimes("Tell me about theft cases in Bengaluru")
print(f"Found {len(results['documents'][0])} relevant results")
if results['documents'][0]:
    print("\nSample result:")
    print(results['documents'][0][0][:200] + "...")
