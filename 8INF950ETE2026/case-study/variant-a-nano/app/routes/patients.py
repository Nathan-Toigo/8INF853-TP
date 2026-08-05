from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from app.core.db import get_db
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.appointment import AppointmentStatus
from app.schemas.patient import PatientOut
from app.schemas.appointment import AppointmentOut

router = APIRouter()

@router.get("", response_model=list[PatientOut])
def list_patients(db: Session = Depends(get_db)):
    stmt = select(Patient).order_by(Patient.id)
    return list(db.execute(stmt).scalars().all())

@router.get("/{patient_id}/appointments", response_model=list[AppointmentOut])
def patient_appointments(
    patient_id: int,
    from_: datetime | None = Query(default=None),
    to: datetime | None = Query(default=None),
    status: AppointmentStatus | None = Query(default=None),
    db: Session = Depends(get_db),
):
    stmt = select(Appointment).where(Appointment.patient_id == patient_id)

    if from_ is not None:
        stmt = stmt.where(Appointment.start_at >= from_)
    if to is not None:
        stmt = stmt.where(Appointment.end_at <= to)
    if status is not None:
        stmt = stmt.where(Appointment.status == status)

    stmt = stmt.order_by(Appointment.start_at)
    return list(db.execute(stmt).scalars().all())