from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db.deps import get_db
from app.schemas.patient import PatientCreate, PatientRead
from app.crud.patient import create_patient, get_patient, list_patients

router = APIRouter()


@router.post("", response_model=PatientRead, status_code=201)
def create_patient_endpoint(payload: PatientCreate, db: Session = Depends(get_db)):
    try:
        return create_patient(db, payload)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email patient déjà utilisé.")


@router.get("", response_model=list[PatientRead])
def list_patients_endpoint(db: Session = Depends(get_db)):
    return list_patients(db)


@router.get("/{patient_id}", response_model=PatientRead)
def get_patient_endpoint(patient_id: int, db: Session = Depends(get_db)):
    patient = get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient introuvable.")
    return patient
