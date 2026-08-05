from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Practitioner
from app.schemas import (
    AvailabilityRead,
    AvailabilitySlot,
    PractitionerCreate,
    PractitionerRead,
    PractitionerUpdate,
)
from app.services import get_available_slots


router = APIRouter(prefix="/practitioners", tags=["Praticiens"])


@router.post("", response_model=PractitionerRead, status_code=status.HTTP_201_CREATED)
def create_practitioner(
    payload: PractitionerCreate,
    db: Session = Depends(get_db),
) -> Practitioner:
    practitioner = Practitioner(**payload.model_dump())

    try:
        db.add(practitioner)
        db.commit()
        db.refresh(practitioner)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un praticien possède déjà cette adresse e-mail.",
        ) from exc

    return practitioner


@router.get("", response_model=list[PractitionerRead])
def list_practitioners(
    active_only: bool = Query(default=False),
    specialty: str | None = Query(default=None, min_length=2),
    db: Session = Depends(get_db),
) -> list[Practitioner]:
    statement = select(Practitioner).order_by(
        Practitioner.last_name,
        Practitioner.first_name,
    )

    if active_only:
        statement = statement.where(Practitioner.is_active.is_(True))

    if specialty:
        statement = statement.where(
            Practitioner.specialty.ilike(f"%{specialty.strip()}%")
        )

    return list(db.scalars(statement).all())


@router.get("/{practitioner_id}", response_model=PractitionerRead)
def get_practitioner(
    practitioner_id: int,
    db: Session = Depends(get_db),
) -> Practitioner:
    practitioner = db.get(Practitioner, practitioner_id)

    if practitioner is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Praticien introuvable.",
        )

    return practitioner


@router.put("/{practitioner_id}", response_model=PractitionerRead)
def update_practitioner(
    practitioner_id: int,
    payload: PractitionerUpdate,
    db: Session = Depends(get_db),
) -> Practitioner:
    practitioner = db.get(Practitioner, practitioner_id)

    if practitioner is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Praticien introuvable.",
        )

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(practitioner, field, value)

    try:
        db.commit()
        db.refresh(practitioner)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un praticien possède déjà cette adresse e-mail.",
        ) from exc

    return practitioner


@router.patch(
    "/{practitioner_id}/deactivate",
    response_model=PractitionerRead,
)
def deactivate_practitioner(
    practitioner_id: int,
    db: Session = Depends(get_db),
) -> Practitioner:
    practitioner = db.get(Practitioner, practitioner_id)

    if practitioner is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Praticien introuvable.",
        )

    practitioner.is_active = False
    db.commit()
    db.refresh(practitioner)
    return practitioner


@router.get("/{practitioner_id}/availability", response_model=AvailabilityRead)
def practitioner_availability(
    practitioner_id: int,
    target_date: date = Query(alias="date"),
    slot_duration_minutes: int = Query(default=30, ge=10, le=120),
    db: Session = Depends(get_db),
) -> AvailabilityRead:
    practitioner = db.get(Practitioner, practitioner_id)

    if practitioner is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Praticien introuvable.",
        )

    slots = get_available_slots(
        db=db,
        practitioner_id=practitioner_id,
        target_date=target_date,
        slot_duration_minutes=slot_duration_minutes,
    )

    return AvailabilityRead(
        practitioner_id=practitioner_id,
        date=target_date,
        slot_duration_minutes=slot_duration_minutes,
        available_slots=[
            AvailabilitySlot(start_at=start_at, end_at=end_at)
            for start_at, end_at in slots
        ],
    )
