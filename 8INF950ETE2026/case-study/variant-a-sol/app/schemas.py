from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

from app.models import AppointmentStatus


class PatientBase(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    birth_date: date
    phone: str = Field(min_length=5, max_length=30)
    email: EmailStr | None = None


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    birth_date: date | None = None
    phone: str | None = Field(default=None, min_length=5, max_length=30)
    email: EmailStr | None = None


class PatientRead(PatientBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class PractitionerBase(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    specialty: str = Field(min_length=2, max_length=150)
    email: EmailStr
    phone: str | None = Field(default=None, min_length=5, max_length=30)
    is_active: bool = True


class PractitionerCreate(PractitionerBase):
    pass


class PractitionerUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    specialty: str | None = Field(default=None, min_length=2, max_length=150)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, min_length=5, max_length=30)
    is_active: bool | None = None


class PractitionerRead(PractitionerBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class AppointmentCreate(BaseModel):
    patient_id: int = Field(gt=0)
    practitioner_id: int = Field(gt=0)
    start_at: datetime
    end_at: datetime
    reason: str | None = Field(default=None, max_length=500)
    notes: str | None = None

    @model_validator(mode="after")
    def validate_dates(self) -> "AppointmentCreate":
        if self.end_at <= self.start_at:
            raise ValueError(
                "La date de fin doit être strictement postérieure à la date de début."
            )
        return self


class AppointmentStatusUpdate(BaseModel):
    status: AppointmentStatus


class AppointmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int
    practitioner_id: int
    start_at: datetime
    end_at: datetime
    reason: str | None
    status: AppointmentStatus
    notes: str | None
    created_at: datetime
    updated_at: datetime


class AvailabilitySlot(BaseModel):
    start_at: datetime
    end_at: datetime


class AvailabilityRead(BaseModel):
    practitioner_id: int
    date: date
    slot_duration_minutes: int
    available_slots: list[AvailabilitySlot]
