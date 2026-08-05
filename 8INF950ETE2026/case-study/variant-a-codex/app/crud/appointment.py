from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.appointment import Appointment, AppointmentStatus
from app.schemas.appointment import AppointmentCreate


def has_time_conflict(db: Session, doctor_id: int, patient_id: int, start_time, end_time) -> bool:
    overlap_filter = and_(
        Appointment.start_time < end_time,
        Appointment.end_time > start_time,
        Appointment.status != AppointmentStatus.cancelled,
    )
    doctor_conflict = db.query(Appointment).filter(Appointment.doctor_id == doctor_id).filter(overlap_filter).first()
    patient_conflict = db.query(Appointment).filter(Appointment.patient_id == patient_id).filter(overlap_filter).first()
    return bool(doctor_conflict or patient_conflict)


def create_appointment(db: Session, payload: AppointmentCreate) -> Appointment:
    appointment = Appointment(**payload.model_dump())
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment


def get_appointment(db: Session, appointment_id: int) -> Appointment | None:
    return db.query(Appointment).filter(Appointment.id == appointment_id).first()


def list_appointments(db: Session, doctor_id: int | None, patient_id: int | None, status: AppointmentStatus | None):
    q = db.query(Appointment)
    if doctor_id is not None:
        q = q.filter(Appointment.doctor_id == doctor_id)
    if patient_id is not None:
        q = q.filter(Appointment.patient_id == patient_id)
    if status is not None:
        q = q.filter(Appointment.status == status)
    return q.order_by(Appointment.start_time.asc()).all()


def update_status(db: Session, appointment: Appointment, status: AppointmentStatus) -> Appointment:
    appointment.status = status
    db.commit()
    db.refresh(appointment)
    return appointment


def delete_appointment(db: Session, appointment: Appointment) -> None:
    db.delete(appointment)
    db.commit()
