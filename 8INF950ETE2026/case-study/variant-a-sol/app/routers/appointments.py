from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Appointment, AppointmentStatus, Patient, Practitioner
from app.schemas import (
    AppointmentCreate,
    AppointmentRead,
    AppointmentStatusUpdate,
)
from app.services import (
    get_appointment_conflict,
    practitioner_can_accept_appointments,
)


router = APIRouter(prefix="/appointments", tags=["Rendez-vous"])


@router.post("", response_model=AppointmentRead, status_code=status.HTTP_201_CREATED)
def create_appointment(
    payload: AppointmentCreate,
    db: Session = Depends(get_db),
) -> Appointment:
    patient = db.get(Patient, payload.patient_id)
    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient introuvable.",
        )

    practitioner = db.get(Practitioner, payload.practitioner_id)
    if practitioner is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Praticien introuvable.",
        )

    if not practitioner_can_accept_appointments(practitioner):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ce praticien est inactif et ne peut pas recevoir de rendez-vous.",
        )

    conflict = get_appointment_conflict(
        db=db,
        practitioner_id=payload.practitioner_id,
        start_at=payload.start_at,
        end_at=payload.end_at,
    )

    if conflict is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Le praticien possède déjà un rendez-vous actif "
                "sur ce créneau."
            ),
        )

    appointment = Appointment(
        patient_id=payload.patient_id,
        practitioner_id=payload.practitioner_id,
        start_at=payload.start_at,
        end_at=payload.end_at,
        reason=payload.reason,
        notes=payload.notes,
        status=AppointmentStatus.SCHEDULED,
    )

    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment


@router.get("", response_model=list[AppointmentRead])
def list_appointments(
    patient_id: int | None = Query(default=None, gt=0),
    practitioner_id: int | None = Query(default=None, gt=0),
    appointment_status: AppointmentStatus | None = Query(
        default=None,
        alias="status",
    ),
    start_from: datetime | None = Query(default=None),
    end_to: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[Appointment]:
    statement = select(Appointment).order_by(Appointment.start_at)

    if patient_id is not None:
        statement = statement.where(Appointment.patient_id == patient_id)

    if practitioner_id is not None:
        statement = statement.where(
            Appointment.practitioner_id == practitioner_id
        )

    if appointment_status is not None:
        statement = statement.where(Appointment.status == appointment_status)

    if start_from is not None:
        statement = statement.where(Appointment.start_at >= start_from)

    if end_to is not None:
        statement = statement.where(Appointment.end_at <= end_to)

    return list(db.scalars(statement).all())


@router.get("/{appointment_id}", response_model=AppointmentRead)
def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
) -> Appointment:
    appointment = db.get(Appointment, appointment_id)

    if appointment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rendez-vous introuvable.",
        )

    return appointment


@router.patch("/{appointment_id}/status", response_model=AppointmentRead)
def update_appointment_status(
    appointment_id: int,
    payload: AppointmentStatusUpdate,
    db: Session = Depends(get_db),
) -> Appointment:
    appointment = db.get(Appointment, appointment_id)

    if appointment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rendez-vous introuvable.",
        )

    if payload.status in (
        AppointmentStatus.SCHEDULED,
        AppointmentStatus.CONFIRMED,
    ):
        conflict = get_appointment_conflict(
            db=db,
            practitioner_id=appointment.practitioner_id,
            start_at=appointment.start_at,
            end_at=appointment.end_at,
            excluded_appointment_id=appointment.id,
        )

        if conflict is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Impossible d'activer ce rendez-vous : "
                    "le créneau est déjà occupé."
                ),
            )

    appointment.status = payload.status
    db.commit()
    db.refresh(appointment)
    return appointment


@router.post("/{appointment_id}/cancel", response_model=AppointmentRead)
def cancel_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
) -> Appointment:
    appointment = db.get(Appointment, appointment_id)

    if appointment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rendez-vous introuvable.",
        )

    appointment.status = AppointmentStatus.CANCELLED
    db.commit()
    db.refresh(appointment)
    return appointment
