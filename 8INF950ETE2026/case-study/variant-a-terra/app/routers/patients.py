from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.dependencies import DatabaseSession
from app.models import Patient
from app.schemas import PatientCreate, PatientRead

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.post("", response_model=PatientRead, status_code=status.HTTP_201_CREATED)
def create_patient(payload: PatientCreate, db: DatabaseSession):
    patient = Patient(**payload.model_dump())
    db.add(patient)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un patient avec cette adresse e-mail existe déjà.",
        )

    db.refresh(patient)
    return patient


@router.get("", response_model=list[PatientRead])
def list_patients(db: DatabaseSession, skip: int = 0, limit: int = 100):
    limit = min(max(limit, 1), 100)
    statement = (
        select(Patient)
        .order_by(Patient.last_name, Patient.first_name)
        .offset(max(skip, 0))
        .limit(limit)
    )
    return list(db.scalars(statement).all())


@router.get("/{patient_id}", response_model=PatientRead)
def get_patient(patient_id: str, db: DatabaseSession):
    patient = db.get(Patient, patient_id)
    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient introuvable.",
        )
    return patient
