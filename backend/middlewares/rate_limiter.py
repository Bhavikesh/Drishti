from fastapi import Request
from starlette.responses import JSONResponse
import time
from typing import Callable

# In-memory dictionary for rate limiting
request_counts = {}
RATE_LIMIT = 50
TIME_WINDOW = 60  # seconds

async def rate_limit_middleware(request: Request, call_next: Callable):
    # Use user IP as the key. If authenticated, could use user ID.
    client_ip = request.client.host
    current_time = time.time()
    
    if client_ip not in request_counts:
        request_counts[client_ip] = []
        
    # Filter out timestamps older than the time window
    request_counts[client_ip] = [timestamp for timestamp in request_counts[client_ip] 
                                 if current_time - timestamp < TIME_WINDOW]
                                 
    if len(request_counts[client_ip]) >= RATE_LIMIT:
        return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded. Maximum 50 requests per minute."})
        
    request_counts[client_ip].append(current_time)
    
    response = await call_next(request)
    return response
