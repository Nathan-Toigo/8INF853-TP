from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import and_, select

from app.dependencies import DatabaseSession
from app.models import Appointment, AppointmentStatus, Patient, Practitioner
from app.schemas import (
    AppointmentCancel,
    AppointmentCreate,
    AppointmentRead,
    AvailabilityRead,
)
from app.time_utils import to_utc_naive

router = APIRouter(prefix="/appointments", tags=["Rendez-vous"])


def find_overlapping_appointment(
    db: DatabaseSession,
    practitioner_id: UUID,
    starts_at: datetime,
    ends_at: datetime,
) -> Optional[Appointment]:
    """
    Détecte un chevauchement selon la règle :
    rendez-vous_existant.début < nouveau.fin ET rendez-vous_existant.fin > nouveau.début.
    """
    statement = select(Appointment).where(
        and_(
            Appointment.practitioner_id == practitioner_id,
            Appointment.status != AppointmentStatus.CANCELLED,
            Appointment.starts_at < ends_at,
            Appointment.ends_at > starts_at,
        )
    )
    return db.scalars(statement).first()


@router.get("/availability", response_model=AvailabilityRead)
def check_availability(
    practitioner_id: UUID,
    starts_at: datetime,
    ends_at: datetime,
    db: DatabaseSession,
):
    try:
        normalized_start = to_utc_naive(starts_at)
        normalized_end = to_utc_naive(ends_at)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        )

    if normalized_end <= normalized_start:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La fin du créneau doit être postérieure à son début.",
        )

    practitioner = db.get(Practitioner, practitioner_id)
    if practitioner is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Praticien introuvable.",
        )

    overlap = find_overlapping_appointment(
        db,
        practitioner_id,
        normalized_start,
        normalized_end,
    )

    return AvailabilityRead(
        practitioner_id=practitioner_id,
        starts_at=normalized_start,
        ends_at=normalized_end,
        available=overlap is None,
    )


@router.post("", response_model=AppointmentRead, status_code=status.HTTP_201_CREATED)
def create_appointment(payload: AppointmentCreate, db: DatabaseSession):
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

    overlap = find_overlapping_appointment(
        db,
        payload.practitioner_id,
        payload.starts_at,
        payload.ends_at,
    )
    if overlap is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Le praticien possède déjà un rendez-vous actif "
                "sur ce créneau horaire."
            ),
        )

    appointment = Appointment(
        patient_id=payload.patient_id,
        practitioner_id=payload.practitioner_id,
        starts_at=payload.starts_at,
        ends_at=payload.ends_at,
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
    db: DatabaseSession,
    patient_id: Optional[UUID] = None,
    practitioner_id: Optional[UUID] = None,
    appointment_status: Optional[AppointmentStatus] = Query(default=None, alias="status"),
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
):
    statement = select(Appointment)

    if patient_id is not None:
        statement = statement.where(Appointment.patient_id == patient_id)

    if practitioner_id is not None:
        statement = statement.where(Appointment.practitioner_id == practitioner_id)

    if appointment_status is not None:
        statement = statement.where(Appointment.status == appointment_status)

    if from_date is not None:
        try:
            statement = statement.where(Appointment.starts_at >= to_utc_naive(from_date))
        except ValueError as error:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(error),
            )

    if to_date is not None:
        try:
            statement = statement.where(Appointment.ends_at <= to_utc_naive(to_date))
        except ValueError as error:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(error),
            )

    statement = (
        statement.order_by(Appointment.starts_at)
        .offset(max(skip, 0))
        .limit(min(max(limit, 1), 100))
    )

    return list(db.scalars(statement).all())


@router.get("/{appointment_id}", response_model=AppointmentRead)
def get_appointment(appointment_id: UUID, db: DatabaseSession):
    appointment = db.get(Appointment, appointment_id)
    if appointment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rendez-vous introuvable.",
        )
    return appointment


@router.post("/{appointment_id}/cancel", response_model=AppointmentRead)
def cancel_appointment(
    appointment_id: UUID,
    payload: AppointmentCancel,
    db: DatabaseSession,
):
    appointment = db.get(Appointment, appointment_id)
    if appointment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rendez-vous introuvable.",
        )

    if appointment.status == AppointmentStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ce rendez-vous est déjà annulé.",
        )

    if appointment.status == AppointmentStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un rendez-vous terminé ne peut pas être annulé.",
        )

    appointment.status = AppointmentStatus.CANCELLED
    appointment.cancelled_at = datetime.utcnow()

    if payload.cancellation_reason:
        previous_notes = appointment.notes or ""
        cancellation_note = f"Annulation : {payload.cancellation_reason}"
        appointment.notes = (
            f"{previous_notes}\n{cancellation_note}".strip()
            if previous_notes
            else cancellation_note
        )

    db.commit()
    db.refresh(appointment)
    return appointment
