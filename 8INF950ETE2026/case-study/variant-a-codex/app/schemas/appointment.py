from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime
from app.models.appointment import AppointmentStatus


class AppointmentBase(BaseModel):
    patient_id: int
    doctor_id: int
    start_time: datetime
    end_time: datetime
    reason: str
    notes: str | None = None

    @field_validator("end_time")
    @classmethod
    def validate_end_after_start(cls, v, values):
        start_time = values.data.get("start_time")
        if start_time and v <= start_time:
            raise ValueError("end_time doit être postérieur à start_time.")
        return v


class AppointmentCreate(AppointmentBase):
    pass


class AppointmentStatusUpdate(BaseModel):
    status: AppointmentStatus


class AppointmentRead(AppointmentBase):
    id: int
    status: AppointmentStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
