from fastapi import Request
from starlette.responses import JSONResponse
from jose import JWTError, jwt
from typing import Callable
import os

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-for-hackathon")
ALGORITHM = "HS256"

PUBLIC_PATHS = ["/api/auth/login", "/api/auth/register", "/docs", "/openapi.json"]

async def auth_middleware(request: Request, call_next: Callable):
    if request.url.path in PUBLIC_PATHS or request.method == "OPTIONS":
        return await call_next(request)

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(status_code=401, content={"detail": "Missing or invalid token"})

    token = auth_header.split(" ")[1]
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        role: str = payload.get("role")
        if user_id is None:
            return JSONResponse(status_code=401, content={"detail": "Invalid token"})
        
        request.state.user = {"id": user_id, "role": role}
        
    except JWTError:
        return JSONResponse(status_code=401, content={"detail": "Could not validate credentials"})

    response = await call_next(request)
    return response
