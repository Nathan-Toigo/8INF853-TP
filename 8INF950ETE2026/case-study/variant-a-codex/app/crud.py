from datetime import timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from app import models, schemas


def create_patient(db: Session, payload: schemas.PatientCreate) -> models.Patient:
    patient = models.Patient(**payload.model_dump())
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


def list_patients(db: Session) -> list[models.Patient]:
    return list(db.scalars(select(models.Patient).order_by(models.Patient.id.desc())).all())


def get_patient(db: Session, patient_id: int) -> models.Patient | None:
    return db.get(models.Patient, patient_id)


def create_doctor(db: Session, payload: schemas.DoctorCreate) -> models.Doctor:
    doctor = models.Doctor(**payload.model_dump())
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor


def list_doctors(db: Session) -> list[models.Doctor]:
    return list(db.scalars(select(models.Doctor).order_by(models.Doctor.id.desc())).all())


def get_doctor(db: Session, doctor_id: int) -> models.Doctor | None:
    return db.get(models.Doctor, doctor_id)


def _doctor_has_conflict(
    db: Session, doctor_id: int, scheduled_at, duration_minutes: int
) -> bool:
    new_start = scheduled_at
    new_end = scheduled_at + timedelta(minutes=duration_minutes)

    q = select(models.Appointment).where(
        and_(
            models.Appointment.doctor_id == doctor_id,
            models.Appointment.status == models.AppointmentStatus.scheduled,
        )
    )
    existing = db.scalars(q).all()

    for appt in existing:
        old_start = appt.scheduled_at
        old_end = appt.scheduled_at + timedelta(minutes=appt.duration_minutes)
        if new_start < old_end and old_start < new_end:
            return True
    return False


def create_appointment(db: Session, payload: schemas.AppointmentCreate) -> models.Appointment:
    patient = db.get(models.Patient, payload.patient_id)
    if not patient:
        raise ValueError("Patient introuvable")

    doctor = db.get(models.Doctor, payload.doctor_id)
    if not doctor:
        raise ValueError("Médecin introuvable")

    if _doctor_has_conflict(db, payload.doctor_id, payload.scheduled_at, payload.duration_minutes):
        raise ValueError("Conflit d'horaire pour ce médecin")

    appt = models.Appointment(**payload.model_dump())
    db.add(appt)
    db.commit()
    db.refresh(appt)
    return appt


def list_appointments(
    db: Session,
    doctor_id: int | None = None,
    patient_id: int | None = None,
    status: models.AppointmentStatus | None = None,
) -> list[models.Appointment]:
    q = select(models.Appointment)

    if doctor_id is not None:
        q = q.where(models.Appointment.doctor_id == doctor_id)
    if patient_id is not None:
        q = q.where(models.Appointment.patient_id == patient_id)
    if status is not None:
        q = q.where(models.Appointment.status == status)

    q = q.order_by(models.Appointment.scheduled_at.asc())
    return list(db.scalars(q).all())


def get_appointment(db: Session, appointment_id: int) -> models.Appointment | None:
    return db.get(models.Appointment, appointment_id)


def cancel_appointment(db: Session, appointment_id: int) -> models.Appointment | None:
    appt = db.get(models.Appointment, appointment_id)
    if not appt:
        return None
    appt.status = models.AppointmentStatus.cancelled
    db.commit()
    db.refresh(appt)
    return appt


def complete_appointment(db: Session, appointment_id: int) -> models.Appointment | None:
    appt = db.get(models.Appointment, appointment_id)
    if not appt:
        return None
    appt.status = models.AppointmentStatus.completed
    db.commit()
    db.refresh(appt)
    return appt
