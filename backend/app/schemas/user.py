from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    created_at: datetime
    is_active: bool
    is_staff: bool = False
    is_superuser: bool = False
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    class Config:
        from_attributes = True 