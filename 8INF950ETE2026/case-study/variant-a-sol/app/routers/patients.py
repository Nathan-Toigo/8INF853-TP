from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Patient
from app.schemas import PatientCreate, PatientRead, PatientUpdate


router = APIRouter(prefix="/patients", tags=["Patients"])


@router.post("", response_model=PatientRead, status_code=status.HTTP_201_CREATED)
def create_patient(payload: PatientCreate, db: Session = Depends(get_db)) -> Patient:
    patient = Patient(**payload.model_dump())

    try:
        db.add(patient)
        db.commit()
        db.refresh(patient)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un patient possède déjà cette adresse e-mail.",
        ) from exc

    return patient


@router.get("", response_model=list[PatientRead])
def list_patients(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    search: str | None = Query(default=None, min_length=1),
    db: Session = Depends(get_db),
) -> list[Patient]:
    statement = select(Patient).order_by(Patient.last_name, Patient.first_name)

    if search:
        normalized_search = f"%{search.strip()}%"
        statement = statement.where(
            (Patient.first_name.ilike(normalized_search))
            | (Patient.last_name.ilike(normalized_search))
        )

    return list(db.scalars(statement.offset(skip).limit(limit)).all())


@router.get("/{patient_id}", response_model=PatientRead)
def get_patient(patient_id: int, db: Session = Depends(get_db)) -> Patient:
    patient = db.get(Patient, patient_id)

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient introuvable.",
        )

    return patient


@router.put("/{patient_id}", response_model=PatientRead)
def update_patient(
    patient_id: int,
    payload: PatientUpdate,
    db: Session = Depends(get_db),
) -> Patient:
    patient = db.get(Patient, patient_id)

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient introuvable.",
        )

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(patient, field, value)

    try:
        db.commit()
        db.refresh(patient)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un patient possède déjà cette adresse e-mail.",
        ) from exc

    return patient
