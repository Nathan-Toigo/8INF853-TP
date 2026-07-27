from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.db import get_db
from app.models.doctor import Doctor
from app.schemas.doctor import DoctorOut

router = APIRouter()

@router.get("", response_model=list[DoctorOut])
def list_doctors(db: Session = Depends(get_db)):
    stmt = select(Doctor).order_by(Doctor.id)
    return list(db.execute(stmt).scalars().all())