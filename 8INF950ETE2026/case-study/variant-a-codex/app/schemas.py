from datetime import date, datetime
from enum import Enum
from pydantic import BaseModel, EmailStr, Field


class AppointmentStatus(str, Enum):
    scheduled = "scheduled"
    cancelled = "cancelled"
    completed = "completed"


class PatientBase(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    date_of_birth: date
    phone: str = Field(min_length=6, max_length=30)
    email: EmailStr | None = None


class PatientCreate(PatientBase):
    pass


class PatientRead(PatientBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class DoctorBase(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    specialty: str = Field(min_length=2, max_length=120)
    phone: str = Field(min_length=6, max_length=30)
    email: EmailStr | None = None


class DoctorCreate(DoctorBase):
    pass


class DoctorRead(DoctorBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    scheduled_at: datetime
    duration_minutes: int = Field(default=30, ge=5, le=240)
    reason: str | None = Field(default=None, max_length=255)
    notes: str | None = None


class AppointmentRead(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    scheduled_at: datetime
    duration_minutes: int
    reason: str | None
    status: AppointmentStatus
    notes: str | None
    created_at: datetime

    class Config:
        from_attributes = True
