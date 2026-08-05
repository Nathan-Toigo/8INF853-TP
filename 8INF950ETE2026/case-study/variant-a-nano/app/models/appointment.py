import enum
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Enum, String, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

class AppointmentStatus(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    CANCELED = "CANCELED"
    COMPLETED = "COMPLETED"

class Appointment(Base):
    __tablename__ = "appointments"
    __table_args__ = (
        Index("ix_appointments_doctor_start", "doctor_id", "start_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.id"), index=True, nullable=False)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), index=True, nullable=False)

    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)

    status: Mapped[AppointmentStatus] = mapped_column(Enum(AppointmentStatus), nullable=False, index=True)
    reason: Mapped[str] = mapped_column(String(255), nullable=True)

    doctor = relationship("Doctor", lazy="joined")
    patient = relationship("Patient", lazy="joined")