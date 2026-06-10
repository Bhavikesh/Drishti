from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

class CrimeCreate(BaseModel):
    crime_date: date
    district: str
    police_station_id: int
    crime_type: str
    description: str
    status: str = "open"
    lat: float
    lng: float
    is_resolved: bool = False

class CrimeResponse(CrimeCreate):
    id: int
    case_id: str
    resolution_date: Optional[date] = None

class CrimeQuery(BaseModel):
    district: Optional[str] = None
    crime_type: Optional[str] = None
    status: Optional[str] = None
    
class CriminalResponse(BaseModel):
    id: int
    name: str
    age: int
    gender: str
    criminal_history_count: int
    is_repeat_offender: bool
    first_offense_date: date

class NetworkNode(BaseModel):
    id: str
    name: str
    crimeCount: int

class NetworkLink(BaseModel):
    source: str
    target: str

class NetworkData(BaseModel):
    nodes: List[NetworkNode]
    links: List[NetworkLink]
