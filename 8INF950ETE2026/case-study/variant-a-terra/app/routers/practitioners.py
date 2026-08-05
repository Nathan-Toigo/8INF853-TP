from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.dependencies import DatabaseSession
from app.models import Practitioner
from app.schemas import PractitionerCreate, PractitionerRead

router = APIRouter(prefix="/practitioners", tags=["Praticiens"])


@router.post("", response_model=PractitionerRead, status_code=status.HTTP_201_CREATED)
def create_practitioner(payload: PractitionerCreate, db: DatabaseSession):
    practitioner = Practitioner(**payload.model_dump())
    db.add(practitioner)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un praticien avec cette adresse e-mail existe déjà.",
        )

    db.refresh(practitioner)
    return practitioner


@router.get("", response_model=list[PractitionerRead])
def list_practitioners(db: DatabaseSession, skip: int = 0, limit: int = 100):
    limit = min(max(limit, 1), 100)
    statement = (
        select(Practitioner)
        .order_by(Practitioner.last_name, Practitioner.first_name)
        .offset(max(skip, 0))
        .limit(limit)
    )
    return list(db.scalars(statement).all())


@router.get("/{practitioner_id}", response_model=PractitionerRead)
def get_practitioner(practitioner_id: str, db: DatabaseSession):
    practitioner = db.get(Practitioner, practitioner_id)
    if practitioner is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Praticien introuvable.",
        )
    return practitioner
