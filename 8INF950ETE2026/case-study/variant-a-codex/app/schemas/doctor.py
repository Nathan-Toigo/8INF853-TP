from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime


class DoctorBase(BaseModel):
    first_name: str
    last_name: str
    specialty: str
    email: EmailStr
    phone: str


class DoctorCreate(DoctorBase):
    pass


class DoctorRead(DoctorBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
