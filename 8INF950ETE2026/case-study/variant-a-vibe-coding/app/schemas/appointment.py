from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from app.models.appointment import AppointmentStatus
from app.schemas.common import BaseSchema

class AppointmentCreate(BaseSchema):
    doctor_id: int
    patient_id: int
    start_at: datetime
    duration_minutes: int = Field(ge=5, le=480)
    reason: Optional[str] = None

class AppointmentUpdate(BaseSchema):
    start_at: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(default=None, ge=5, le=480)
    reason: Optional[str] = None
    status: Optional[AppointmentStatus] = None

class AppointmentOut(BaseSchema):
    id: int
    doctor_id: int
    patient_id: int
    start_at: datetime
    end_at: datetime
    status: AppointmentStatus
    reason: Optional[str] = None

class AppointmentSearchResponse(BaseSchema):
    items: list[AppointmentOut]
    total: int