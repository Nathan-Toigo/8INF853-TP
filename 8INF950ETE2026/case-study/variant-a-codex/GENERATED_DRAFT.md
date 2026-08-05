## 1) Problème résolu et utilisateurs cibles

Le projet **« Gestion de rendez-vous médicaux »** permet d’organiser la prise de rendez-vous entre patients et médecins, avec des règles simples de disponibilité et de validation.

### Problème
Dans beaucoup de structures de santé, la prise de rendez-vous est encore semi-manuelle (téléphone, tableur, agendas séparés), ce qui provoque :
- des conflits d’horaires,
- des erreurs de saisie,
- une visibilité limitée pour les patients et les praticiens.

### Utilisateurs cibles
- **Patients** : consulter les médecins, réserver/annuler leurs rendez-vous.
- **Médecins** : visualiser leur planning, changer le statut des rendez-vous.
- **Personnel administratif** : créer les fiches patients/médecins, superviser les réservations.

---

## 2) Modèle de données (entités, attributs, relations)

### Entités

1. **Patient**
   - `id` (PK)
   - `first_name`
   - `last_name`
   - `email` (unique)
   - `phone`
   - `date_of_birth`
   - `created_at`

2. **Doctor**
   - `id` (PK)
   - `first_name`
   - `last_name`
   - `specialty`
   - `email` (unique)
   - `phone`
   - `created_at`

3. **Appointment**
   - `id` (PK)
   - `patient_id` (FK -> Patient.id)
   - `doctor_id` (FK -> Doctor.id)
   - `start_time` (datetime)
   - `end_time` (datetime)
   - `status` (`scheduled`, `completed`, `cancelled`)
   - `reason` (motif)
   - `notes` (optionnel)
   - `created_at`

### Relations
- Un **patient** peut avoir plusieurs **appointments** (1-N).
- Un **doctor** peut avoir plusieurs **appointments** (1-N).
- Un **appointment** appartient à exactement un patient et un médecin.

---

## 3) Fonctionnalités principales (API / cas d’usage)

### Patients
- `POST /patients` : créer un patient.
- `GET /patients` : lister les patients.
- `GET /patients/{patient_id}` : détail patient.

### Médecins
- `POST /doctors` : créer un médecin.
- `GET /doctors` : lister les médecins.
- `GET /doctors/{doctor_id}` : détail médecin.

### Rendez-vous
- `POST /appointments` : créer un rendez-vous (avec vérification de conflits d’horaires médecin/patient).
- `GET /appointments` : lister les rendez-vous (filtres optionnels `doctor_id`, `patient_id`, `status`).
- `GET /appointments/{appointment_id}` : détail rendez-vous.
- `PATCH /appointments/{appointment_id}/status` : mettre à jour le statut.
- `DELETE /appointments/{appointment_id}` : annuler/supprimer un rendez-vous.

### Santé de service
- `GET /health` : endpoint de vérification.

---

## 4) Proposition d’architecture technique

- **Langage** : Python 3.11+
- **Framework API** : FastAPI
- **ORM** : SQLAlchemy
- **Validation** : Pydantic
- **Base de données** : SQLite (par défaut, facilement remplaçable)
- **Tests** : Pytest + TestClient FastAPI

### Structure de dossiers
- `app/main.py` : point d’entrée FastAPI
- `app/core/config.py` : configuration
- `app/db/session.py` : connexion DB/session
- `app/db/base.py` : base SQLAlchemy
- `app/models/*.py` : modèles ORM
- `app/schemas/*.py` : schémas Pydantic
- `app/crud/*.py` : logique métier CRUD
- `app/api/routes/*.py` : routes API
- `tests/test_api.py` : tests principaux

---

## 5) Code source complet et exécutable

===FILE: requirements.txt===
```txt
fastapi==0.115.0
uvicorn==0.30.6
SQLAlchemy==2.0.35
pydantic==2.9.2
python-dateutil==2.9.0.post0
pytest==8.3.3
httpx==0.27.2
```

===FILE: app/__init__.py===
```python
```

===FILE: app/main.py===
```python
from fastapi import FastAPI
from app.db.session import engine
from app.db.base import Base
from app.api.routes import patients, doctors, appointments

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Gestion de rendez-vous médicaux", version="1.0.0")

app.include_router(patients.router, prefix="/patients", tags=["Patients"])
app.include_router(doctors.router, prefix="/doctors", tags=["Doctors"])
app.include_router(appointments.router, prefix="/appointments", tags=["Appointments"])


@app.get("/health")
def health():
    return {"status": "ok"}
```

===FILE: app/core/config.py===
```python
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./medical_appointments.db")
```

===FILE: app/db/base.py===
```python
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
```

===FILE: app/db/session.py===
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import DATABASE_URL

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

===FILE: app/db/deps.py===
```python
from app.db.session import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

===FILE: app/models/__init__.py===
```python
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.appointment import Appointment
```

===FILE: app/models/patient.py===
```python
from sqlalchemy import Integer, String, Date, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(30), nullable=False)
    date_of_birth: Mapped[Date] = mapped_column(Date, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    appointments = relationship("Appointment", back_populates="patient", cascade="all, delete-orphan")
```

===FILE: app/models/doctor.py===
```python
from sqlalchemy import Integer, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Doctor(Base):
    __tablename__ = "doctors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    specialty: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(30), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    appointments = relationship("Appointment", back_populates="doctor", cascade="all, delete-orphan")
```

===FILE: app/models/appointment.py===
```python
from sqlalchemy import Integer, String, DateTime, ForeignKey, func, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
import enum


class AppointmentStatus(str, enum.Enum):
    scheduled = "scheduled"
    completed = "completed"
    cancelled = "cancelled"


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), nullable=False, index=True)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.id"), nullable=False, index=True)
    start_time: Mapped[DateTime] = mapped_column(DateTime(timezone=False), nullable=False, index=True)
    end_time: Mapped[DateTime] = mapped_column(DateTime(timezone=False), nullable=False, index=True)
    status: Mapped[AppointmentStatus] = mapped_column(
        Enum(AppointmentStatus), default=AppointmentStatus.scheduled, nullable=False
    )
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
```

===FILE: app/schemas/patient.py===
```python
from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import date, datetime


class PatientBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    date_of_birth: date


class PatientCreate(PatientBase):
    pass


class PatientRead(PatientBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
```

===FILE: app/schemas/doctor.py===
```python
from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime


class DoctorBase(BaseModel):
    first_name: str
    last_name: str
    specialty: str
    email: EmailStr
    phone: str


class DoctorCreate(DoctorBase):
    pass


class DoctorRead(DoctorBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
```

===FILE: app/schemas/appointment.py===
```python
from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime
from app.models.appointment import AppointmentStatus


class AppointmentBase(BaseModel):
    patient_id: int
    doctor_id: int
    start_time: datetime
    end_time: datetime
    reason: str
    notes: str | None = None

    @field_validator("end_time")
    @classmethod
    def validate_end_after_start(cls, v, values):
        start_time = values.data.get("start_time")
        if start_time and v <= start_time:
            raise ValueError("end_time doit être postérieur à start_time.")
        return v


class AppointmentCreate(AppointmentBase):
    pass


class AppointmentStatusUpdate(BaseModel):
    status: AppointmentStatus


class AppointmentRead(AppointmentBase):
    id: int
    status: AppointmentStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
```

===FILE: app/schemas/__init__.py===
```python
from app.schemas.patient import PatientCreate, PatientRead
from app.schemas.doctor import DoctorCreate, DoctorRead
from app.schemas.appointment import AppointmentCreate, AppointmentRead, AppointmentStatusUpdate
```

===FILE: app/crud/patient.py===
```python
from sqlalchemy.orm import Session
from app.models.patient import Patient
from app.schemas.patient import PatientCreate


def create_patient(db: Session, payload: PatientCreate) -> Patient:
    patient = Patient(**payload.model_dump())
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


def get_patient(db: Session, patient_id: int) -> Patient | None:
    return db.query(Patient).filter(Patient.id == patient_id).first()


def list_patients(db: Session) -> list[Patient]:
    return db.query(Patient).order_by(Patient.id.desc()).all()
```

===FILE: app/crud/doctor.py===
```python
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
```

===FILE: app/crud/appointment.py===
```python
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
```

===FILE: app/api/routes/patients.py===
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db.deps import get_db
from app.schemas.patient import PatientCreate, PatientRead
from app.crud.patient import create_patient, get_patient, list_patients

router = APIRouter()


@router.post("", response_model=PatientRead, status_code=201)
def create_patient_endpoint(payload: PatientCreate, db: Session = Depends(get_db)):
    try:
        return create_patient(db, payload)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email patient déjà utilisé.")


@router.get("", response_model=list[PatientRead])
def list_patients_endpoint(db: Session = Depends(get_db)):
    return list_patients(db)


@router.get("/{patient_id}", response_model=PatientRead)
def get_patient_endpoint(patient_id: int, db: Session = Depends(get_db)):
    patient = get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient introuvable.")
    return patient
```

===FILE: app/api/routes/doctors.py===
```python
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
```

===FILE: app/api/routes/appointments.py===
```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.schemas.appointment import AppointmentCreate, AppointmentRead, AppointmentStatusUpdate
from app.models.appointment import AppointmentStatus
from app.crud.appointment import (
    create_appointment,
    get_appointment,
    list_appointments,
    has_time_conflict,
    update_status,
    delete_appointment,
)
from app.crud.patient import get_patient
from app.crud.doctor import get_doctor

router = APIRouter()


@router.post("", response_model=AppointmentRead, status_code=201)
def create_appointment_endpoint(payload: AppointmentCreate, db: Session = Depends(get_db)):
    if not get_patient(db, payload.patient_id):
        raise HTTPException(status_code=404, detail="Patient introuvable.")
    if not get_doctor(db, payload.doctor_id):
        raise HTTPException(status_code=404, detail="Médecin introuvable.")
    if has_time_conflict(db, payload.doctor_id, payload.patient_id, payload.start_time, payload.end_time):
        raise HTTPException(status_code=409, detail="Conflit horaire détecté pour le patient ou le médecin.")
    return create_appointment(db, payload)


@router.get("", response_model=list[AppointmentRead])
def list_appointments_endpoint(
    doctor_id: int | None = Query(default=None),
    patient_id: int | None = Query(default=None),
    status: AppointmentStatus | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return list_appointments(db, doctor_id, patient_id, status)


@router.get("/{appointment_id}", response_model=AppointmentRead)
def get_appointment_endpoint(appointment_id: int, db: Session = Depends(get_db)):
    appointment = get_appointment(db, appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Rendez-vous introuvable.")
    return appointment


@router.patch("/{appointment_id}/status", response_model=AppointmentRead)
def update_appointment_status_endpoint(appointment_id: int, payload: AppointmentStatusUpdate, db: Session = Depends(get_db)):
    appointment = get_appointment(db, appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Rendez-vous introuvable.")
    return update_status(db, appointment, payload.status)


@router.delete("/{appointment_id}", status_code=204)
def delete_appointment_endpoint(appointment_id: int, db: Session = Depends(get_db)):
    appointment = get_appointment(db, appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Rendez-vous introuvable.")
    delete_appointment(db, appointment)
    return None
```

===FILE: tests/test_api.py===
```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_entities_and_appointment_flow():
    patient_payload = {
        "first_name": "Alice",
        "last_name": "Martin",
        "email": "alice.martin@example.test",
        "phone": "0600000001",
        "date_of_birth": "1992-05-10"
    }
    doctor_payload = {
        "first_name": "Jean",
        "last_name": "Dupont",
        "specialty": "Cardiologie",
        "email": "jean.dupont@example.test",
        "phone": "0600000002"
    }

    p = client.post("/patients", json=patient_payload)
    d = client.post("/doctors", json=doctor_payload)
    assert p.status_code == 201, p.text
    assert d.status_code == 201, d.text

    patient_id = p.json()["id"]
    doctor_id = d.json()["id"]

    appt_payload = {
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "start_time": "2026-01-10T10:00:00",
        "end_time": "2026-01-10T10:30:00",
        "reason": "Consultation de contrôle",
        "notes": "Douleurs thoraciques légères"
    }

    a = client.post("/appointments", json=appt_payload)
    assert a.status_code == 201, a.text

    conflict_payload = {
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "start_time": "2026-01-10T10:15:00",
        "end_time": "2026-01-10T10:45:00",
        "reason": "Conflit",
        "notes": None
    }
    c = client.post("/appointments", json=conflict_payload)
    assert c.status_code == 409

    appt_id = a.json()["id"]
    upd = client.patch(f"/appointments/{appt_id}/status", json={"status": "completed"})
    assert upd.status_code == 200
    assert upd.json()["status"] == "completed"
```

===FILE: README.md===
```md
# Gestion de rendez-vous médicaux (FastAPI)

## Installation

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Lancer l'application

```bash
uvicorn app.main:app --reload
```

API docs:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Exécuter les tests

```bash
pytest -q
```

## Données

Le projet n'utilise aucune donnée réelle. Les tests et exemples reposent sur des données synthétiques.
```

---

## 6) Limites connues / hypothèses

- Authentification/autorisation non implémentées (MVP fonctionnel).
- Pas de gestion avancée des créneaux de disponibilité (horaires cabinet, jours fériés, etc.).
- Concurrence : pas de verrouillage transactionnel avancé (acceptable pour prototype SQLite).
- Suppression d’un rendez-vous = suppression physique (pas d’audit trail).
- Pas d’envoi de notifications (SMS/email).
- Fuseaux horaires simplifiés (datetime naïf côté API).
- Conforme à un prototype technique, pas à une solution certifiée réglementaire (HDS, RGPD complet, traçabilité médicale avancée).