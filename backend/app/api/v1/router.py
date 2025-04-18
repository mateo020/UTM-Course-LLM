from fastapi import APIRouter
from app.api.v1.endpoints import chat
from app.api.v1.endpoints import search

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


api_router.include_router(
    search.router,
    prefix="/search",
    tags=["search"]
)