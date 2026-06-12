from fastapi import APIRouter, HTTPException, Depends, Request
from jose import jwt
from datetime import datetime, timedelta
from schemas.user_schema import UserLogin, UserCreate, UserResponse, TokenData
import os
import hashlib

router = APIRouter()

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-for-hackathon")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day

def hash_password(password: str) -> str:
    """Simple SHA256 hash for demo purposes"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password using SHA256"""
    return hash_password(plain_password) == hashed_password

# Mock database for hackathon
# Password: Admin@123 (hashed with SHA256)
users_db = {
    "admin@ksp.gov.in": {
        "id": 1,
        "email": "admin@ksp.gov.in",
        "password_hash": "e86f78a8a3caf0b60d8e74e5942aa6d86dc150cd3c03338aef25b7d2d7e3acc7",  # Admin@123
        "role": "admin",
        "assigned_district": None,
        "assigned_station_id": None
    }
}

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/login", response_model=TokenData)
async def login(user_data: UserLogin):
    user = users_db.get(user_data.email)
    if not user or not verify_password(user_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
        
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user["id"]), "role": user["role"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register")
async def register(request: Request, user_data: UserCreate):
    # Only admins can register users
    current_user = getattr(request.state, "user", None)
    if not current_user or current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
        
    if user_data.email in users_db:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    # Generate mock ID
    new_id = len(users_db) + 1
    users_db[user_data.email] = {
        "id": new_id,
        "email": user_data.email,
        "password_hash": hash_password(user_data.password),
        "role": user_data.role,
        "assigned_district": user_data.assigned_district,
        "assigned_station_id": user_data.assigned_station_id
    }
    
    return {"message": "User registered successfully"}

@router.get("/me", response_model=UserResponse)
async def me(request: Request):
    current_user = getattr(request.state, "user", None)
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
        
    # Find user in mock db
    for email, user in users_db.items():
        if str(user["id"]) == current_user["id"]:
            return user
            
    raise HTTPException(status_code=404, detail="User not found")

@router.get("/verify")
async def verify(request: Request):
    current_user = getattr(request.state, "user", None)
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {"valid": True, "user": current_user}
