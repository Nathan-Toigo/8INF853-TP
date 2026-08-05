from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from app.models.appointment import Appointment, AppointmentStatus
from app.models.slot import TimeSlot

class AppointmentConflictError(Exception):
    pass

class SlotNotFoundError(Exception):
    pass

def compute_end_at(start_at: datetime, duration_minutes: int) -> datetime:
    return start_at + timedelta(minutes=duration_minutes)

def ensure_within_slot(db: Session, doctor_id: int, start_at: datetime, end_at: datetime) -> None:
    # Need a slot that fully covers the appointment interval
    stmt = select(TimeSlot).where(
        and_(
            TimeSlot.doctor_id == doctor_id,
            TimeSlot.start_at <= start_at,
            TimeSlot.end_at >= end_at,
        )
    )
    slot = db.execute(stmt).scalars().first()
    if not slot:
        raise SlotNotFoundError("Aucune plage horaire ne couvre l'intervalle demandé.")

def ensure_no_conflict(db: Session, doctor_id: int, start_at: datetime, end_at: datetime, exclude_appointment_id: int | None = None) -> None:
    # Overlap condition: [a,b) overlaps [c,d) if a < d and c < b
    stmt = select(Appointment).where(
        and_(
            Appointment.doctor_id == doctor_id,
            Appointment.status == AppointmentStatus.SCHEDULED,
            Appointment.start_at < end_at,
            Appointment.end_at > start_at,
        )
    )
    if exclude_appointment_id is not None:
        stmt = stmt.where(Appointment.id != exclude_appointment_id)

    conflict = db.execute(stmt).scalars().first()
    if conflict:
        raise AppointmentConflictError("Conflit de planning : chevauchement avec un rendez-vous existant.")

def create_appointment(
    db: Session,
    *,
    doctor_id: int,
    patient_id: int,
    start_at: datetime,
    duration_minutes: int,
    reason: str | None,
) -> Appointment:
    end_at = compute_end_at(start_at, duration_minutes)
    ensure_within_slot(db, doctor_id, start_at, end_at)
    ensure_no_conflict(db, doctor_id, start_at, end_at)

    appt = Appointment(
        doctor_id=doctor_id,
        patient_id=patient_id,
        start_at=start_at,
        end_at=end_at,
        status=AppointmentStatus.SCHEDULED,
        reason=reason,
    )
    db.add(appt)
    db.commit()
    db.refresh(appt)
    return appt

def update_appointment(
    db: Session,
    *,
    appointment_id: int,
    start_at: datetime | None,
    duration_minutes: int | None,
    reason: str | None,
    status: AppointmentStatus | None,
) -> Appointment:
    appt = db.get(Appointment, appointment_id)
    if not appt:
        raise ValueError("Rendez-vous introuvable.")

    new_start = start_at if start_at is not None else appt.start_at
    dur = duration_minutes if duration_minutes is not None else int((appt.end_at - appt.start_at).total_seconds() // 60)
    new_end = compute_end_at(new_start, dur)

    # Only enforce constraints if scheduled (or if status explicitly keeps scheduled)
    new_status = status if status is not None else appt.status

    if new_status == AppointmentStatus.SCHEDULED:
        ensure_within_slot(db, appt.doctor_id, new_start, new_end)
        ensure_no_conflict(db, appt.doctor_id, new_start, new_end, exclude_appointment_id=appt.id)

    if start_at is not None:
        appt.start_at = new_start
    if duration_minutes is not None:
        appt.end_at = new_end
    if reason is not None:
        appt.reason = reason
    if status is not None:
        appt.status = status

    db.commit()
    db.refresh(appt)
    return appt

def cancel_appointment(db: Session, appointment_id: int) -> Appointment:
    appt = db.get(Appointment, appointment_id)
    if not appt:
        raise ValueError("Rendez-vous introuvable.")
    appt.status = AppointmentStatus.CANCELED
    db.commit()
    db.refresh(appt)
    return appt

def complete_appointment(db: Session, appointment_id: int) -> Appointment:
    appt = db.get(Appointment, appointment_id)
    if not appt:
        raise ValueError("Rendez-vous introuvable.")
    appt.status = AppointmentStatus.COMPLETED
    db.commit()
    db.refresh(appt)
    return appt