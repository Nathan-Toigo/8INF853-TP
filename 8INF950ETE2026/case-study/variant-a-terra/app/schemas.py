import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_serializer, field_validator, model_validator

from app.models import AppointmentStatus
from app.time_utils import to_utc_naive, utc_naive_to_iso


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class PatientCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    phone: str = Field(min_length=5, max_length=30)
    date_of_birth: date


class PatientRead(APIModel):
    id: uuid.UUID
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    date_of_birth: date
    created_at: datetime


class PractitionerCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    specialty: str = Field(min_length=2, max_length=150)
    email: EmailStr
    phone: str = Field(min_length=5, max_length=30)


class PractitionerRead(APIModel):
    id: uuid.UUID
    first_name: str
    last_name: str
    specialty: str
    email: EmailStr
    phone: str
    created_at: datetime


class AppointmentCreate(BaseModel):
    patient_id: uuid.UUID
    practitioner_id: uuid.UUID
    starts_at: datetime
    ends_at: datetime
    reason: str = Field(min_length=2, max_length=500)
    notes: Optional[str] = Field(default=None, max_length=5000)

    @field_validator("starts_at", "ends_at")
    @classmethod
    def require_timezone_and_normalize(cls, value: datetime) -> datetime:
        return to_utc_naive(value)

    @model_validator(mode="after")
    def validate_dates(self):
        if self.ends_at <= self.starts_at:
            raise ValueError("La fin du rendez-vous doit être postérieure à son début.")
        return self


class AppointmentRead(APIModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    practitioner_id: uuid.UUID
    starts_at: datetime
    ends_at: datetime
    reason: str
    status: AppointmentStatus
    notes: Optional[str]
    created_at: datetime
    cancelled_at: Optional[datetime]

    @field_serializer("starts_at", "ends_at", "created_at", "cancelled_at")
    def serialize_utc_datetimes(self, value: Optional[datetime]) -> Optional[str]:
        if value is None:
            return None
        return utc_naive_to_iso(value)


class AppointmentCancel(BaseModel):
    cancellation_reason: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Motif administratif facultatif de l'annulation.",
    )


class AvailabilityRead(BaseModel):
    practitioner_id: uuid.UUID
    starts_at: datetime
    ends_at: datetime
    available: bool

    @field_serializer("starts_at", "ends_at")
    def serialize_utc_datetimes(self, value: datetime) -> str:
        return utc_naive_to_iso(value)
