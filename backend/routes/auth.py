from fastapi import APIRouter, HTTPException, Depends, Request
from jose import jwt
from datetime import datetime, timedelta
from schemas.user_schema import UserLogin, UserCreate, UserResponse, TokenData
import os
import hashlib
from database import get_db_connection

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
    print(f"Login attempt for: {user_data.email}")
    conn = get_db_connection()
    if not conn:
        print("Login failed: Could not connect to database")
        raise HTTPException(status_code=500, detail="Database connection error")
        
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, email, password_hash, role FROM users WHERE email = %s", (user_data.email,))
        user_record = cur.fetchone()
        
        if not user_record:
            print("Login failed: User not found in database")
            raise HTTPException(status_code=401, detail="Incorrect email or password")
            
        print(f"User found. Expected hash: {user_record[2]}")
        print(f"Provided hash: {hash_password(user_data.password)}")
            
        if not verify_password(user_data.password, user_record[2]):
            print("Login failed: Password hash mismatch")
            raise HTTPException(status_code=401, detail="Incorrect email or password")
            
        print("Login successful!")
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user_record[0]), "role": user_record[3]}, 
            expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    finally:
        cur.close()
        conn.close()

@router.post("/register")
async def register(request: Request, user_data: UserCreate):
    # Only admins can register users
    current_user = getattr(request.state, "user", None)
    if not current_user or current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
        
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")
        
    try:
        cur = conn.cursor()
        # Check if exists
        cur.execute("SELECT id FROM users WHERE email = %s", (user_data.email,))
        if cur.fetchone():
            raise HTTPException(status_code=400, detail="Email already registered")
            
        cur.execute(
            "INSERT INTO users (email, password_hash, role, assigned_district, assigned_station_id) VALUES (%s, %s, %s, %s, %s)",
            (user_data.email, hash_password(user_data.password), user_data.role, user_data.assigned_district, user_data.assigned_station_id)
        )
        conn.commit()
        return {"message": "User registered successfully"}
    finally:
        cur.close()
        conn.close()

@router.get("/me", response_model=UserResponse)
async def me(request: Request):
    current_user = getattr(request.state, "user", None)
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
        
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")
        
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, email, role, assigned_district, assigned_station_id FROM users WHERE id = %s", (current_user["id"],))
        user_record = cur.fetchone()
        
        if not user_record:
            raise HTTPException(status_code=404, detail="User not found")
            
        return {
            "id": user_record[0],
            "email": user_record[1],
            "role": user_record[2],
            "assigned_district": user_record[3],
            "assigned_station_id": user_record[4]
        }
    finally:
        cur.close()
        conn.close()

@router.get("/verify")
async def verify(request: Request):
    current_user = getattr(request.state, "user", None)
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {"valid": True, "user": current_user}
