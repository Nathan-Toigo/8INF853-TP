from app.models.user import UserRole
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    role: UserRole