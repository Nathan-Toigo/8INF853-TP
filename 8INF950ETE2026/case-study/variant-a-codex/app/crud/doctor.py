from sqlalchemy.orm import Session
from app.models.doctor import Doctor
from app.schemas.doctor import DoctorCreate


def create_doctor(db: Session, payload: DoctorCreate) -> Doctor:
    doctor = Doctor(**payload.model_dump())
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor


def get_doctor(db: Session, doctor_id: int) -> Doctor | None:
    return db.query(Doctor).filter(Doctor.id == doctor_id).first()


def list_doctors(db: Session) -> list[Doctor]:
    return db.query(Doctor).order_by(Doctor.id.desc()).all()
