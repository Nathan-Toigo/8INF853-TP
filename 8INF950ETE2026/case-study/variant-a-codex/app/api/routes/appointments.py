from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.schemas.appointment import AppointmentCreate, AppointmentRead, AppointmentStatusUpdate
from app.models.appointment import AppointmentStatus
from app.crud.appointment import (
    create_appointment,
    get_appointment,
    list_appointments,
    has_time_conflict,
    update_status,
    delete_appointment,
)
from app.crud.patient import get_patient
from app.crud.doctor import get_doctor

router = APIRouter()


@router.post("", response_model=AppointmentRead, status_code=201)
def create_appointment_endpoint(payload: AppointmentCreate, db: Session = Depends(get_db)):
    if not get_patient(db, payload.patient_id):
        raise HTTPException(status_code=404, detail="Patient introuvable.")
    if not get_doctor(db, payload.doctor_id):
        raise HTTPException(status_code=404, detail="Médecin introuvable.")
    if has_time_conflict(db, payload.doctor_id, payload.patient_id, payload.start_time, payload.end_time):
        raise HTTPException(status_code=409, detail="Conflit horaire détecté pour le patient ou le médecin.")
    return create_appointment(db, payload)


@router.get("", response_model=list[AppointmentRead])
def list_appointments_endpoint(
    doctor_id: int | None = Query(default=None),
    patient_id: int | None = Query(default=None),
    status: AppointmentStatus | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return list_appointments(db, doctor_id, patient_id, status)


@router.get("/{appointment_id}", response_model=AppointmentRead)
def get_appointment_endpoint(appointment_id: int, db: Session = Depends(get_db)):
    appointment = get_appointment(db, appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Rendez-vous introuvable.")
    return appointment


@router.patch("/{appointment_id}/status", response_model=AppointmentRead)
def update_appointment_status_endpoint(appointment_id: int, payload: AppointmentStatusUpdate, db: Session = Depends(get_db)):
    appointment = get_appointment(db, appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Rendez-vous introuvable.")
    return update_status(db, appointment, payload.status)


@router.delete("/{appointment_id}", status_code=204)
def delete_appointment_endpoint(appointment_id: int, db: Session = Depends(get_db)):
    appointment = get_appointment(db, appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Rendez-vous introuvable.")
    delete_appointment(db, appointment)
    return None
