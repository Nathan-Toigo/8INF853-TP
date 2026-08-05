from datetime import datetime, timedelta
from random import randint

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.user import User, UserRole
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.slot import TimeSlot

router = APIRouter()

def _create_user(db: Session, *, email: str, role: UserRole) -> User:
    user = User(email=email, role=role)
    db.add(user)
    db.flush()  # get id
    return user

@router.post("/seed")
def seed(db: Session = Depends(get_db)):
    """
    Crée des données synthétiques (fictives) : 2 médecins, 2 patients, et des plages horaires couvrant la semaine.
    """
    # Avoid reseeding too much: if already have doctors, don't duplicate.
    if db.query(Doctor).count() > 0:
        return {"message": "Données de démonstration déjà présentes."}

    now = datetime.now().replace(minute=0, second=0, microsecond=0)

    doctors = []
    for i, specialty in enumerate(["Médecine générale", "Dermatologie"], start=1):
        user = _create_user(db, email=f"doctor{i}@example.com", role=UserRole.DOCTOR)
        doc = Doctor(user_id=user.id, specialty=specialty)
        db.add(doc)
        db.flush()
        doctors.append(doc)

    patients = []
    for i, name in enumerate([("Alice", "Martin"), ("Bruno", "Durand")], start=1):
        user = _create_user(db, email=f"patient{i}@example.com", role=UserRole.PATIENT)
        p = Patient(
            user_id=user.id,
            first_name=name[0],
            last_name=name[1],
            phone=f"+33 6 {randint(10,99)}{randint(10,99)}{randint(10,99)}{randint(10,99)}{randint(10,99)}",
        )
        db.add(p)
        db.flush()
        patients.append(p)

    # Create time slots for next 7 days
    for doc in doctors:
        for day in range(0, 7):
            base = now + timedelta(days=day)
            # Morning slot 09:00-12:00, Afternoon slot 14:00-17:00
            morning_start = base.replace(hour=9)
            morning_end = base.replace(hour=12)
            afternoon_start = base.replace(hour=14)
            afternoon_end = base.replace(hour=17)

            db.add(TimeSlot(doctor_id=doc.id, start_at=morning_start, end_at=morning_end))
            db.add(TimeSlot(doctor_id=doc.id, start_at=afternoon_start, end_at=afternoon_end))

    db.commit()
    return {"message": "Données de démonstration créées.", "doctors": len(doctors), "patients": len(patients)}