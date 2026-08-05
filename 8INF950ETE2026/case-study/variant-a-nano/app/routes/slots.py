from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.db import get_db
from app.models.slot import TimeSlot
from app.schemas.slot import TimeSlotCreate, TimeSlotOut

router = APIRouter()

@router.post("/{doctor_id}/slots", response_model=TimeSlotOut)
def create_slot(doctor_id: int, payload: TimeSlotCreate, db: Session = Depends(get_db)):
    if payload.end_at <= payload.start_at:
        raise HTTPException(status_code=400, detail="end_at doit être > start_at")

    slot = TimeSlot(
        doctor_id=doctor_id,
        start_at=payload.start_at,
        end_at=payload.end_at,
    )
    db.add(slot)
    db.commit()
    db.refresh(slot)
    return slot

@router.get("/{doctor_id}/slots", response_model=list[TimeSlotOut])
def list_slots(
    doctor_id: int,
    from_: datetime | None = None,
    to: datetime | None = None,
    db: Session = Depends(get_db),
):
    stmt = select(TimeSlot).where(TimeSlot.doctor_id == doctor_id)
    if from_ is not None:
        stmt = stmt.where(TimeSlot.end_at >= from_)
    if to is not None:
        stmt = stmt.where(TimeSlot.start_at <= to)

    stmt = stmt.order_by(TimeSlot.start_at)
    return list(db.execute(stmt).scalars().all())