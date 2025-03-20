from fastapi import APIRouter
from app.api.v1.endpoints import projects, chat, users, auth

api_router = APIRouter()

print("Registering routes...")



print("Available project routes:", [
    f"{route.path} [{route.methods}]" 
    for route in projects.router.routes
])

api_router.include_router(
    chat.router,
    prefix="/chat",
    tags=["chat"]
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["users"]
)

api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["auth"]
) 