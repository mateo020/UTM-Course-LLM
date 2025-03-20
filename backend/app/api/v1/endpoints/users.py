from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.user import UserResponse
from app.services.users import UserService

router = APIRouter()

@router.get("/", response_model=List[UserResponse])
async def get_all_users():
    """
    Get all users
    """
    try:
        return await UserService.get_all_users()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """
    Get a specific user
    """
    try:
        user = await UserService.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 