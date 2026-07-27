from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from app.core.db import get_db
from app.models.appointment import Appointment, AppointmentStatus
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentOut,
    AppointmentSearchResponse,
    AppointmentUpdate,
)
from app.services.appointment_service import (
    create_appointment,
    update_appointment,
    cancel_appointment,
    complete_appointment,
    AppointmentConflictError,
    SlotNotFoundError,
)

router = APIRouter()

@router.post("/appointments", response_model=AppointmentOut)
def create_appointment_endpoint(payload: AppointmentCreate, db: Session = Depends(get_db)):
    try:
        appt = create_appointment(
            db,
            doctor_id=payload.doctor_id,
            patient_id=payload.patient_id,
            start_at=payload.start_at,
            duration_minutes=payload.duration_minutes,
            reason=payload.reason,
        )
        return appt
    except SlotNotFoundError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except AppointmentConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur: {e}")

@router.get("/appointments", response_model=AppointmentSearchResponse)
def search_appointments(
    doctor_id: int | None = Query(default=None),
    patient_id: int | None = Query(default=None),
    from_: datetime | None = Query(default=None),
    to: datetime | None = Query(default=None),
    status: AppointmentStatus | None = Query(default=None),
    db: Session = Depends(get_db),
):
    stmt = select(Appointment)

    if doctor_id is not None:
        stmt = stmt.where(Appointment.doctor_id == doctor_id)
    if patient_id is not None:
        stmt = stmt.where(Appointment.patient_id == patient_id)
    if from_ is not None:
        stmt = stmt.where(Appointment.start_at >= from_)
    if to is not None:
        stmt = stmt.where(Appointment.end_at <= to)
    if status is not None:
        stmt = stmt.where(Appointment.status == status)

    stmt = stmt.order_by(Appointment.start_at)
    items = list(db.execute(stmt).scalars().all())
    return {"items": items, "total": len(items)}

@router.patch("/appointments/{appointment_id}", response_model=AppointmentOut)
def update_appointment_endpoint(
    appointment_id: int,
    payload: AppointmentUpdate,
    db: Session = Depends(get_db),
):
    try:
        appt = update_appointment(
            db,
            appointment_id=appointment_id,
            start_at=payload.start_at,
            duration_minutes=payload.duration_minutes,
            reason=payload.reason,
            status=payload.status,
        )
        return appt
    except SlotNotFoundError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except AppointmentConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur: {e}")

@router.post("/appointments/{appointment_id}/cancel", response_model=AppointmentOut)
def cancel_appointment_endpoint(appointment_id: int, db: Session = Depends(get_db)):
    try:
        return cancel_appointment(db, appointment_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/appointments/{appointment_id}/complete", response_model=AppointmentOut)
def complete_appointment_endpoint(appointment_id: int, db: Session = Depends(get_db)):
    try:
        return complete_appointment(db, appointment_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))