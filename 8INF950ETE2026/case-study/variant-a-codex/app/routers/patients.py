from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.dependencies import get_db
from app import schemas, crud

router = APIRouter(prefix="/patients", tags=["patients"])


@router.post("", response_model=schemas.PatientRead, status_code=201)
def create_patient(payload: schemas.PatientCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_patient(db, payload)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Téléphone ou email déjà utilisé")


@router.get("", response_model=list[schemas.PatientRead])
def list_patients(db: Session = Depends(get_db)):
    return crud.list_patients(db)


@router.get("/{patient_id}", response_model=schemas.PatientRead)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = crud.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient introuvable")
    return patient
