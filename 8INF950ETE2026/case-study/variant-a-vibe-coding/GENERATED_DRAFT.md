## 1) Problème résolu et utilisateurs cibles

**Problème :** organiser efficacement des **rendez-vous médicaux** : création, modification, annulation, recherche, gestion de disponibilités et réduction des conflits de planning (double réservation).

**Utilisateurs cibles :**
- **Secrétaires médicales / assistants administratifs** : création et planification des rendez-vous, recherche par patient ou médecin.
- **Médecins** : consulter leurs rendez-vous à venir, gérer les changements et annulations.
- **Patients (côté portail)** : demander/consulter leurs rendez-vous (données fictives dans cette démo).
- **Administrateurs du cabinet** : configurer des médecins, plages horaires et règles simples de disponibilité.

Dans cette proposition, l’API expose des cas d’utilisation typiques via **FastAPI** et un modèle de données relationnel (SQLite).

---

## 2) Modèle de données (entités, attributs, relations)

### Entités
1. **Utilisateur (User)** *(optionnel pour la démo, mais utile pour la cohérence)*  
   - `id` (PK)  
   - `email` (unique)  
   - `role` : `ADMIN | SECRETARY | DOCTOR | PATIENT`

2. **Patient**  
   - `id` (PK)  
   - `user_id` (FK vers User, unique)  
   - `first_name`, `last_name`  
   - `phone`

3. **Médecin (Doctor)**  
   - `id` (PK)  
   - `user_id` (FK vers User, unique)  
   - `specialty`

4. **PlageHoraire (TimeSlot)** *(disponibilité de base)*  
   - `id` (PK)  
   - `doctor_id` (FK vers Doctor)  
   - `start_at` (datetime)  
   - `end_at` (datetime)

5. **RendezVous (Appointment)**  
   - `id` (PK)  
   - `doctor_id` (FK)  
   - `patient_id` (FK)  
   - `start_at` (datetime)  
   - `end_at` (datetime)  
   - `status` : `SCHEDULED | CANCELED | COMPLETED`  
   - `reason` (texte court)

### Relations
- Un **Patient** appartient à un **User** (1–1).
- Un **Médecin** appartient à un **User** (1–1).
- Un **RendezVous** relie **un patient** et **un médecin** (N–1 vers chacun).
- Un **Médecin** possède plusieurs **plages horaires** (1–N).
- Un **RendezVous** doit être inclus dans une **plage horaire** du médecin et ne doit pas chevaucher un autre rendez-vous planifié.

---

## 3) Fonctionnalités principales (endpoints / cas d’utilisation)

1. **Seed de données fictives** : créer médecins/patients/plages horaires de démonstration  
   - `POST /admin/seed`

2. **Gestion médecins** : lister les médecins  
   - `GET /doctors`

3. **Gestion patients (fictif)** : lister les patients  
   - `GET /patients`

4. **Plages horaires (disponibilité)**  
   - `POST /doctors/{doctor_id}/slots` : créer une plage horaire
   - `GET /doctors/{doctor_id}/slots?from=...&to=...` : consulter plages

5. **Rendez-vous : CRUD**
   - `POST /appointments` : créer un rendez-vous (contrôle chevauchement + inclusion dans slots)
   - `GET /appointments?doctor_id=...&patient_id=...&from=...&to=...&status=...` : rechercher
   - `PATCH /appointments/{appointment_id}` : modifier (date/durée/motif)
   - `POST /appointments/{appointment_id}/cancel` : annuler
   - `POST /appointments/{appointment_id}/complete` : terminer

6. **Calendrier patient**
   - `GET /patients/{patient_id}/appointments?from=...&to=...` : rendez-vous d’un patient

---

## 4) Proposition d’architecture technique

- **Langage** : Python  
- **Framework** : FastAPI  
- **ORM** : SQLAlchemy (avec SQLite)  
- **Validation** : Pydantic  
- **Migration** : non incluse (démo), base créée au démarrage via `create_all`  
- **Tests** : pytest + httpx (TestClient)  
- **Structure de dossiers :**
  - `app/main.py` : application FastAPI
  - `app/core/config.py` : configuration
  - `app/core/db.py` : connexion DB + session
  - `app/models/*` : modèles SQLAlchemy
  - `app/schemas/*` : schémas Pydantic
  - `app/routes/*` : routes par domaine
  - `app/services/appointment_service.py` : logique métier (conflits/slots)
  - `app/tests/*` : tests

---

## 5) Code source complet et exécutable (multi-fichiers)

===FILE: requirements.txt===
```txt
fastapi==0.115.0
uvicorn==0.30.6
SQLAlchemy==2.0.36
pydantic==2.8.2
pydantic-settings==2.4.0
python-dotenv==1.0.1
httpx==0.27.2
pytest==8.3.2
```

===FILE: app/main.py===
```python
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.db import init_db
from app.routes.admin import router as admin_router
from app.routes.doctors import router as doctors_router
from app.routes.patients import router as patients_router
from app.routes.slots import router as slots_router
from app.routes.appointments import router as appointments_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="Gestion de rendez-vous médicaux",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(admin_router, prefix="/admin", tags=["admin"])
app.include_router(doctors_router, prefix="/doctors", tags=["doctors"])
app.include_router(patients_router, prefix="/patients", tags=["patients"])
app.include_router(slots_router, prefix="/doctors", tags=["slots"])
app.include_router(appointments_router, prefix="", tags=["appointments"])


@app.get("/health")
def health():
    return {"status": "ok"}
```

===FILE: app/core/config.py===
```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    db_url: str = "sqlite:///./app.db"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
```

===FILE: app/core/db.py===
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.core.config import settings

engine = create_engine(
    settings.db_url,
    connect_args={"check_same_thread": False} if settings.db_url.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def init_db():
    # Import late to avoid circular imports
    from app.models.user import User
    from app.models.patient import Patient
    from app.models.doctor import Doctor
    from app.models.slot import TimeSlot
    from app.models.appointment import Appointment

    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

===FILE: app/models/user.py===
```python
import enum
from sqlalchemy import String, Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base

class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    SECRETARY = "SECRETARY"
    DOCTOR = "DOCTOR"
    PATIENT = "PATIENT"

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False, index=True)
```

===FILE: app/models/patient.py===
```python
from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

class Patient(Base):
    __tablename__ = "patients"
    __table_args__ = (UniqueConstraint("user_id", name="uq_patients_user_id"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(30), nullable=True)

    user = relationship("User", lazy="joined")
```

===FILE: app/models/doctor.py===
```python
from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

class Doctor(Base):
    __tablename__ = "doctors"
    __table_args__ = (UniqueConstraint("user_id", name="uq_doctors_user_id"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    specialty: Mapped[str] = mapped_column(String(120), nullable=False)

    user = relationship("User", lazy="joined")
```

===FILE: app/models/slot.py===
```python
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

class TimeSlot(Base):
    __tablename__ = "time_slots"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.id"), index=True, nullable=False)
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)

    doctor = relationship("Doctor", lazy="joined")

    __table_args__ = (
        Index("ix_time_slots_doctor_start", "doctor_id", "start_at"),
    )
```

===FILE: app/models/appointment.py===
```python
import enum
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Enum, String, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

class AppointmentStatus(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    CANCELED = "CANCELED"
    COMPLETED = "COMPLETED"

class Appointment(Base):
    __tablename__ = "appointments"
    __table_args__ = (
        Index("ix_appointments_doctor_start", "doctor_id", "start_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.id"), index=True, nullable=False)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), index=True, nullable=False)

    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)

    status: Mapped[AppointmentStatus] = mapped_column(Enum(AppointmentStatus), nullable=False, index=True)
    reason: Mapped[str] = mapped_column(String(255), nullable=True)

    doctor = relationship("Doctor", lazy="joined")
    patient = relationship("Patient", lazy="joined")
```

===FILE: app/schemas/common.py===
```python
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class DateRangeQuery(BaseModel):
    from_: datetime | None = None
    to: datetime | None = None
```

===FILE: app/schemas/user.py===
```python
from app.models.user import UserRole
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    role: UserRole
```

===FILE: app/schemas/patient.py===
```python
from typing import Optional
from pydantic import BaseModel

from app.schemas.common import BaseSchema

class PatientCreate(BaseSchema):
    first_name: str
    last_name: str
    phone: Optional[str] = None

class PatientOut(BaseSchema):
    id: int
    first_name: str
    last_name: str
    phone: Optional[str] = None
```

===FILE: app/schemas/doctor.py===
```python
from pydantic import BaseModel

from app.schemas.common import BaseSchema

class DoctorOut(BaseSchema):
    id: int
    specialty: str

class DoctorCreate(BaseSchema):
    specialty: str
```

===FILE: app/schemas/slot.py===
```python
from datetime import datetime
from pydantic import BaseModel
from app.schemas.common import BaseSchema

class TimeSlotCreate(BaseSchema):
    start_at: datetime
    end_at: datetime

class TimeSlotOut(BaseSchema):
    id: int
    doctor_id: int
    start_at: datetime
    end_at: datetime
```

===FILE: app/schemas/appointment.py===
```python
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from app.models.appointment import AppointmentStatus
from app.schemas.common import BaseSchema

class AppointmentCreate(BaseSchema):
    doctor_id: int
    patient_id: int
    start_at: datetime
    duration_minutes: int = Field(ge=5, le=480)
    reason: Optional[str] = None

class AppointmentUpdate(BaseSchema):
    start_at: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(default=None, ge=5, le=480)
    reason: Optional[str] = None
    status: Optional[AppointmentStatus] = None

class AppointmentOut(BaseSchema):
    id: int
    doctor_id: int
    patient_id: int
    start_at: datetime
    end_at: datetime
    status: AppointmentStatus
    reason: Optional[str] = None

class AppointmentSearchResponse(BaseSchema):
    items: list[AppointmentOut]
    total: int
```

===FILE: app/services/appointment_service.py===
```python
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
```

===FILE: app/routes/admin.py===
```python
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
```

===FILE: app/routes/doctors.py===
```python
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
```

===FILE: app/routes/patients.py===
```python
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from app.core.db import get_db
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.appointment import AppointmentStatus
from app.schemas.patient import PatientOut
from app.schemas.appointment import AppointmentOut

router = APIRouter()

@router.get("", response_model=list[PatientOut])
def list_patients(db: Session = Depends(get_db)):
    stmt = select(Patient).order_by(Patient.id)
    return list(db.execute(stmt).scalars().all())

@router.get("/{patient_id}/appointments", response_model=list[AppointmentOut])
def patient_appointments(
    patient_id: int,
    from_: datetime | None = Query(default=None),
    to: datetime | None = Query(default=None),
    status: AppointmentStatus | None = Query(default=None),
    db: Session = Depends(get_db),
):
    stmt = select(Appointment).where(Appointment.patient_id == patient_id)

    if from_ is not None:
        stmt = stmt.where(Appointment.start_at >= from_)
    if to is not None:
        stmt = stmt.where(Appointment.end_at <= to)
    if status is not None:
        stmt = stmt.where(Appointment.status == status)

    stmt = stmt.order_by(Appointment.start_at)
    return list(db.execute(stmt).scalars().all())
```

===FILE: app/routes/slots.py===
```python
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
```

===FILE: app/routes/appointments.py===
```python
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from app.core.db import get_db
from app.models.appointment import Appointment, AppointmentStatus
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentOut,
    AppointmentSearchResponse,
    AppointmentUpdate,
)
from app.services.appointment_service import (
    create_appointment,
    update_appointment,
    cancel_appointment,
    complete_appointment,
    AppointmentConflictError,
    SlotNotFoundError,
)

router = APIRouter()

@router.post("/appointments", response_model=AppointmentOut)
def create_appointment_endpoint(payload: AppointmentCreate, db: Session = Depends(get_db)):
    try:
        appt = create_appointment(
            db,
            doctor_id=payload.doctor_id,
            patient_id=payload.patient_id,
            start_at=payload.start_at,
            duration_minutes=payload.duration_minutes,
            reason=payload.reason,
        )
        return appt
    except SlotNotFoundError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except AppointmentConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur: {e}")

@router.get("/appointments", response_model=AppointmentSearchResponse)
def search_appointments(
    doctor_id: int | None = Query(default=None),
    patient_id: int | None = Query(default=None),
    from_: datetime | None = Query(default=None),
    to: datetime | None = Query(default=None),
    status: AppointmentStatus | None = Query(default=None),
    db: Session = Depends(get_db),
):
    stmt = select(Appointment)

    if doctor_id is not None:
        stmt = stmt.where(Appointment.doctor_id == doctor_id)
    if patient_id is not None:
        stmt = stmt.where(Appointment.patient_id == patient_id)
    if from_ is not None:
        stmt = stmt.where(Appointment.start_at >= from_)
    if to is not None:
        stmt = stmt.where(Appointment.end_at <= to)
    if status is not None:
        stmt = stmt.where(Appointment.status == status)

    stmt = stmt.order_by(Appointment.start_at)
    items = list(db.execute(stmt).scalars().all())
    return {"items": items, "total": len(items)}

@router.patch("/appointments/{appointment_id}", response_model=AppointmentOut)
def update_appointment_endpoint(
    appointment_id: int,
    payload: AppointmentUpdate,
    db: Session = Depends(get_db),
):
    try:
        appt = update_appointment(
            db,
            appointment_id=appointment_id,
            start_at=payload.start_at,
            duration_minutes=payload.duration_minutes,
            reason=payload.reason,
            status=payload.status,
        )
        return appt
    except SlotNotFoundError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except AppointmentConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur: {e}")

@router.post("/appointments/{appointment_id}/cancel", response_model=AppointmentOut)
def cancel_appointment_endpoint(appointment_id: int, db: Session = Depends(get_db)):
    try:
        return cancel_appointment(db, appointment_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/appointments/{appointment_id}/complete", response_model=AppointmentOut)
def complete_appointment_endpoint(appointment_id: int, db: Session = Depends(get_db)):
    try:
        return complete_appointment(db, appointment_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
```

===FILE: app/tests/test_appointments.py===
```python
from datetime import datetime, timedelta

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_seed_and_create_and_conflict():
    # Seed data
    r = client.post("/admin/seed")
    assert r.status_code in (200, 201)
    data = r.json()
    assert "message" in data

    # List doctors/patients
    doctors = client.get("/doctors").json()
    patients = client.get("/patients").json()
    assert len(doctors) >= 2
    assert len(patients) >= 2

    doctor_id = doctors[0]["id"]
    patient_id = patients[0]["id"]

    # Get slots for doctor 1
    slots = client.get(f"/doctors/{doctor_id}/slots").json()
    assert len(slots) >= 2

    slot0 = slots[0]
    start_at = datetime.fromisoformat(slot0["start_at"])
    # Create appointment within first slot
    payload = {
        "doctor_id": doctor_id,
        "patient_id": patient_id,
        "start_at": (start_at + timedelta(minutes=30)).isoformat(),
        "duration_minutes": 30,
        "reason": "Douleur temporaire (fictif)",
    }
    r1 = client.post("/appointments", json=payload)
    assert r1.status_code == 200, r1.text
    appt1 = r1.json()
    assert appt1["status"] == "SCHEDULED"

    # Try create overlapping appointment (conflict)
    payload2 = {
        "doctor_id": doctor_id,
        "patient_id": patients[1]["id"],
        "start_at": (start_at + timedelta(minutes=45)).isoformat(),  # overlaps with appt1
        "duration_minutes": 30,
        "reason": "Visite de contrôle (fictif)",
    }
    r2 = client.post("/appointments", json=payload2)
    assert r2.status_code == 409
    assert "Conflit" in r2.json()["detail"] or "chevauchement" in r2.json()["detail"]

def test_cancel():
    doctors = client.get("/doctors").json()
    patients = client.get("/patients").json()
    doctor_id = doctors[0]["id"]
    patient_id = patients[0]["id"]

    slots = client.get(f"/doctors/{doctor_id}/slots").json()
    slot0 = slots[1]
    start_at = datetime.fromisoformat(slot0["start_at"])

    payload = {
        "doctor_id": doctor_id,
        "patient_id": patient_id,
        "start_at": (start_at + timedelta(minutes=10)).isoformat(),
        "duration_minutes": 20,
        "reason": "Test annulation (fictif)",
    }
    r1 = client.post("/appointments", json=payload)
    assert r1.status_code == 200
    appt_id = r1.json()["id"]

    rc = client.post(f"/appointments/{appt_id}/cancel")
    assert rc.status_code == 200
    assert rc.json()["status"] == "CANCELED"
```

===FILE: pytest.ini===
```txt
[pytest]
testpaths = app/tests
addopts = -q
```

---

## 6) Limites connues ou hypothèses

- **Authentification/autorisation** non implémentées : l’API ne gère pas de profils utilisateurs réels ; c’est une démo fonctionnelle.
- **Fuseau horaire** : datetimes stockés sans timezone (`DateTime(timezone=False)`), donc supposés dans un même fuseau horaire côté serveur.
- **Sélection des plages horaires** : la création d’un rendez-vous exige qu’une **plage couvre entièrement** l’intervalle (pas de découpage automatique des slots).
- **Conflits** : seuls les rendez-vous au statut `SCHEDULED` sont considérés pour les chevauchements.
- **Données fictives uniquement** : le seed génère des noms/phones synthétiques.
- **Pas de migrations** : la base est créée via `create_all()` au démarrage ; pour production, il faudrait Alembic.
- **Pas de UI** : uniquement une API REST.

--- 

### Lancer le projet (rapide)
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Exemple d’usage
1. Seed :
```bash
curl -X POST http://127.0.0.1:8000/admin/seed
```
2. Créer un rendez-vous :
```bash
curl -X POST http://127.0.0.1:8000/appointments \
  -H "Content-Type: application/json" \
  -d '{"doctor_id":1,"patient_id":1,"start_at":"2026-07-26T10:30:00","duration_minutes":30,"reason":"Consultation (fictif)"}'
```

Si un créneau chevauche ou sort des plages horaires, l’API renverra une erreur `409`.