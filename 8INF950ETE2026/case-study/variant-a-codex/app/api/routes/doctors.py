from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db.deps import get_db
from app.schemas.doctor import DoctorCreate, DoctorRead
from app.crud.doctor import create_doctor, get_doctor, list_doctors

router = APIRouter()


@router.post("", response_model=DoctorRead, status_code=201)
def create_doctor_endpoint(payload: DoctorCreate, db: Session = Depends(get_db)):
    try:
        return create_doctor(db, payload)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email médecin déjà utilisé.")


@router.get("", response_model=list[DoctorRead])
def list_doctors_endpoint(db: Session = Depends(get_db)):
    return list_doctors(db)


@router.get("/{doctor_id}", response_model=DoctorRead)
def get_doctor_endpoint(doctor_id: int, db: Session = Depends(get_db)):
    doctor = get_doctor(db, doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Médecin introuvable.")
    return doctor
