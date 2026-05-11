from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.websocket import router as websocket_router
from app.routes.auth import router as auth_router
from app.routes.users import router as users_router
from app.routes.messages import router as messages_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(messages_router)
app.include_router(websocket_router)

@app.get("/")
async def read_root():
    return {"message": "Fast API Rabbit Playground is Running"}
