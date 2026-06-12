from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from middlewares.rate_limiter import rate_limit_middleware
from middlewares.auth_middleware import auth_middleware
from routes import auth, chat, network, predictions, export, investigation
from starlette.middleware.base import BaseHTTPMiddleware

app = FastAPI(title="CrimeMind AI API", version="1.0.0",
              description="Intelligent Crime Investigation Copilot for Karnataka State Police")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(BaseHTTPMiddleware, dispatch=auth_middleware)
app.add_middleware(BaseHTTPMiddleware, dispatch=rate_limit_middleware)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(network.router, prefix="/api/network", tags=["network"])
app.include_router(predictions.router, prefix="/api/predictions", tags=["predictions"])
app.include_router(export.router, prefix="/api/export", tags=["export"])
app.include_router(investigation.router, prefix="/api/investigation", tags=["investigation"])

@app.get("/")
def root():
    return {
        "name": "CrimeMind AI",
        "version": "1.0.0",
        "description": "Intelligent Crime Investigation Copilot for Karnataka State Police",
        "status": "operational"
    }
