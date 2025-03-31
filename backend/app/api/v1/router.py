from fastapi import APIRouter
from app.api.v1.endpoints import chat

api_router = APIRouter()

print("Registering routes...")



# print("Available project routes:", [
#     f"{route.path} [{route.methods}]" 
#     for route in projects.router.routes
# ])

api_router.include_router(
    chat.router,
    prefix="/chat",
    tags=["chat"]
)


