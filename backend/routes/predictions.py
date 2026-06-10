from fastapi import APIRouter
from prophet import Prophet
import pandas as pd
import numpy as np

router = APIRouter()

@router.get("/forecast")
async def get_forecast(district: str = "Bengaluru", days: int = 30):
    # Mock prophet forecast for hackathon
    # Create a simple df
    dates = pd.date_range(start='1/1/2023', periods=100)
    data = np.random.randint(1, 20, size=100)
    df = pd.DataFrame({'ds': dates, 'y': data})
    
    try:
        m = Prophet()
        m.fit(df)
        future = m.make_future_dataframe(periods=days)
        forecast = m.predict(future)
        
        # Return recent history + forecast
        results = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(days).to_dict('records')
        return {"district": district, "forecast": results}
    except Exception as e:
        return {"error": str(e), "message": "Prophet model failed to generate forecast"}

@router.get("/hotspots")
async def get_hotspots(crime_type: str = "theft"):
    # Mock data
    hotspots = [
        {"station": "Indiranagar PS", "count": 145, "lat": 12.9784, "lng": 77.6408},
        {"station": "Koramangala PS", "count": 120, "lat": 12.9352, "lng": 77.6245},
        {"station": "Whitefield PS", "count": 95, "lat": 12.9698, "lng": 77.7499}
    ]
    return {"crime_type": crime_type, "hotspots": hotspots}

@router.get("/alerts")
async def get_alerts():
    # Mock alerts
    alerts = [
        {"district": "Mysore", "severity": "high", "message": "Unusual spike in vehicle thefts expected this weekend."},
        {"district": "Bengaluru Urban", "severity": "medium", "message": "Chain snatching incidents rising in South Zone."}
    ]
    return {"alerts": alerts}
