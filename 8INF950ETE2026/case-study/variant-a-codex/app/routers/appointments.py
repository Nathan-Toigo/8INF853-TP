from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app import schemas, crud, models

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.post("", response_model=schemas.AppointmentRead, status_code=201)
def create_appointment(payload: schemas.AppointmentCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_appointment(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=list[schemas.AppointmentRead])
def list_appointments(
    doctor_id: int | None = Query(default=None),
    patient_id: int | None = Query(default=None),
    status: schemas.AppointmentStatus | None = Query(default=None),
    db: Session = Depends(get_db),
):
    mapped_status = models.AppointmentStatus(status.value) if status else None
    return crud.list_appointments(db, doctor_id=doctor_id, patient_id=patient_id, status=mapped_status)


@router.get("/{appointment_id}", response_model=schemas.AppointmentRead)
def get_appointment(appointment_id: int, db: Session = Depends(get_db)):
    appt = crud.get_appointment(db, appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Rendez-vous introuvable")
    return appt


@router.patch("/{appointment_id}/cancel", response_model=schemas.AppointmentRead)
def cancel_appointment(appointment_id: int, db: Session = Depends(get_db)):
    appt = crud.cancel_appointment(db, appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Rendez-vous introuvable")
    return appt


@router.patch("/{appointment_id}/complete", response_model=schemas.AppointmentRead)
def complete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    appt = crud.complete_appointment(db, appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Rendez-vous introuvable")
    return appt
