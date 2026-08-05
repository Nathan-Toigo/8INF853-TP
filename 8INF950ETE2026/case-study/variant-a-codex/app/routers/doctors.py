from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.dependencies import get_db
from app import schemas, crud

router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.post("", response_model=schemas.DoctorRead, status_code=201)
def create_doctor(payload: schemas.DoctorCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_doctor(db, payload)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Téléphone ou email déjà utilisé")


@router.get("", response_model=list[schemas.DoctorRead])
def list_doctors(db: Session = Depends(get_db)):
    return crud.list_doctors(db)


@router.get("/{doctor_id}", response_model=schemas.DoctorRead)
def get_doctor(doctor_id: int, db: Session = Depends(get_db)):
    doctor = crud.get_doctor(db, doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Médecin introuvable")
    return doctor
