from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum

class RoleEnum(str, Enum):
    constable = "constable"
    inspector = "inspector"
    sp = "sp"
    admin = "admin"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: RoleEnum
    assigned_district: Optional[str] = None
    assigned_station_id: Optional[int] = None

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: RoleEnum
    assigned_district: Optional[str]
    assigned_station_id: Optional[int]

class TokenData(BaseModel):
    access_token: str
    token_type: str = "bearer"
