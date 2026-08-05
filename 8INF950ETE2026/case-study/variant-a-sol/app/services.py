from datetime import date, datetime, time, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Appointment, AppointmentStatus, Practitioner


ACTIVE_APPOINTMENT_STATUSES = (
    AppointmentStatus.SCHEDULED,
    AppointmentStatus.CONFIRMED,
)


def get_appointment_conflict(
    db: Session,
    practitioner_id: int,
    start_at: datetime,
    end_at: datetime,
    excluded_appointment_id: int | None = None,
) -> Appointment | None:
    statement = select(Appointment).where(
        Appointment.practitioner_id == practitioner_id,
        Appointment.status.in_(ACTIVE_APPOINTMENT_STATUSES),
        Appointment.start_at < end_at,
        Appointment.end_at > start_at,
    )

    if excluded_appointment_id is not None:
        statement = statement.where(Appointment.id != excluded_appointment_id)

    return db.scalar(statement)


def get_available_slots(
    db: Session,
    practitioner_id: int,
    target_date: date,
    slot_duration_minutes: int,
) -> list[tuple[datetime, datetime]]:
    day_start = datetime.combine(
        target_date,
        time(hour=settings.workday_start_hour),
    )
    day_end = datetime.combine(
        target_date,
        time(hour=settings.workday_end_hour),
    )
    duration = timedelta(minutes=slot_duration_minutes)

    appointments = db.scalars(
        select(Appointment)
        .where(
            Appointment.practitioner_id == practitioner_id,
            Appointment.status.in_(ACTIVE_APPOINTMENT_STATUSES),
            Appointment.start_at < day_end,
            Appointment.end_at > day_start,
        )
        .order_by(Appointment.start_at)
    ).all()

    slots: list[tuple[datetime, datetime]] = []
    current_start = day_start

    while current_start + duration <= day_end:
        current_end = current_start + duration
        has_conflict = any(
            appointment.start_at < current_end
            and appointment.end_at > current_start
            for appointment in appointments
        )

        if not has_conflict:
            slots.append((current_start, current_end))

        current_start = current_end

    return slots


def practitioner_can_accept_appointments(practitioner: Practitioner) -> bool:
    return practitioner.is_active
