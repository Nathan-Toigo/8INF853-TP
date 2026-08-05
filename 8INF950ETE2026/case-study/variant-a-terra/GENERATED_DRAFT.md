# 1. Problème résolu et utilisateurs cibles

**Gestion de rendez-vous médicaux** est une API REST permettant de centraliser la planification de consultations médicales.

Elle permet de :

- enregistrer des patients avec des données administratives minimales ;
- enregistrer des praticiens et leurs spécialités ;
- créer des rendez-vous ;
- empêcher les chevauchements de créneaux pour un même praticien ;
- consulter l’agenda d’un praticien ;
- annuler un rendez-vous sans supprimer son historique ;
- vérifier la disponibilité d’un praticien sur une plage horaire.

Utilisateurs cibles :

- secrétaires médicales ;
- personnel d’accueil ;
- praticiens ;
- applications web ou mobiles de prise de rendez-vous ;
- systèmes administratifs internes de cabinets, cliniques ou centres médicaux.

Les données utilisées par les tests sont uniquement fictives.

# 2. Modèle de données

## Entité `Patient`

| Attribut | Type | Description |
|---|---|---|
| `id` | UUID | Identifiant unique du patient |
| `first_name` | texte | Prénom |
| `last_name` | texte | Nom |
| `email` | texte | Adresse e-mail, unique |
| `phone` | texte | Numéro de téléphone |
| `date_of_birth` | date | Date de naissance |
| `created_at` | datetime | Date de création de la fiche |

Relation :

- un patient peut avoir plusieurs rendez-vous.

## Entité `Practitioner`

| Attribut | Type | Description |
|---|---|---|
| `id` | UUID | Identifiant unique du praticien |
| `first_name` | texte | Prénom |
| `last_name` | texte | Nom |
| `specialty` | texte | Spécialité médicale |
| `email` | texte | Adresse e-mail professionnelle, unique |
| `phone` | texte | Téléphone professionnel |
| `created_at` | datetime | Date de création |

Relation :

- un praticien peut avoir plusieurs rendez-vous.

## Entité `Appointment`

| Attribut | Type | Description |
|---|---|---|
| `id` | UUID | Identifiant unique du rendez-vous |
| `patient_id` | UUID | Référence vers le patient |
| `practitioner_id` | UUID | Référence vers le praticien |
| `starts_at` | datetime | Début du rendez-vous, en UTC |
| `ends_at` | datetime | Fin du rendez-vous, en UTC |
| `reason` | texte | Motif administratif ou libellé du rendez-vous |
| `status` | enum | `scheduled`, `cancelled`, `completed` |
| `notes` | texte nullable | Notes administratives facultatives |
| `created_at` | datetime | Date de création |
| `cancelled_at` | datetime nullable | Date d’annulation |

Relations :

- un rendez-vous appartient à un seul patient ;
- un rendez-vous appartient à un seul praticien ;
- un rendez-vous actif ne doit pas chevaucher un autre rendez-vous actif du même praticien.

# 3. Fonctionnalités principales

## Patients

- `POST /patients` : créer un patient.
- `GET /patients` : lister les patients.
- `GET /patients/{patient_id}` : consulter un patient.

## Praticiens

- `POST /practitioners` : créer un praticien.
- `GET /practitioners` : lister les praticiens.
- `GET /practitioners/{practitioner_id}` : consulter un praticien.

## Rendez-vous

- `POST /appointments` : créer un rendez-vous.
- `GET /appointments` : lister les rendez-vous avec filtres possibles.
- `GET /appointments/{appointment_id}` : consulter un rendez-vous.
- `POST /appointments/{appointment_id}/cancel` : annuler un rendez-vous.
- `GET /appointments/availability` : vérifier la disponibilité d’un praticien sur un créneau.

## Supervision

- `GET /health` : vérifier l’état de fonctionnement de l’API.
- Documentation OpenAPI disponible via `/docs`.

# 4. Proposition d’architecture technique

## Technologies

- **Python 3.11+**
- **FastAPI** pour l’API REST
- **SQLAlchemy 2** pour l’ORM
- **SQLite** par défaut pour une exécution immédiate
- **Pydantic v2** pour la validation des entrées et sorties
- **Pytest** pour les tests automatisés

## Structure de dossiers

```text
gestion-rendez-vous-medicaux/
├── requirements.txt
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── dependencies.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── time_utils.py
│   └── routers/
│       ├── __init__.py
│       ├── appointments.py
│       ├── patients.py
│       └── practitioners.py
└── tests/
    └── test_api.py
```

## Exécution

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

L’API sera accessible sur :

```text
http://127.0.0.1:8000
```

Documentation interactive :

```text
http://127.0.0.1:8000/docs
```

# 5. Code source complet

===FILE: requirements.txt===
```txt
fastapi==0.115.8
uvicorn[standard]==0.34.0
sqlalchemy==2.0.38
pydantic==2.10.6
email-validator==2.2.0
pytest==8.3.4
httpx==0.28.1
```

===FILE: app/__init__.py===
```python
"""Package principal de l'application Gestion de rendez-vous médicaux."""
```

===FILE: app/config.py===
```python
import os


class Settings:
    """Configuration centralisée de l'application."""

    app_name: str = "Gestion de rendez-vous médicaux"
    app_version: str = "1.0.0"
    database_url: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./medical_appointments.db",
    )


settings = Settings()
```

===FILE: app/database.py===
```python
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

connect_args = {}
if settings.database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
)

if settings.database_url.startswith("sqlite"):

    @event.listens_for(Engine, "connect")
    def enable_sqlite_foreign_keys(dbapi_connection, connection_record):
        del connection_record
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Classe de base des modèles SQLAlchemy."""


def get_db():
    """Fournit une session de base de données pour une requête HTTP."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

===FILE: app/dependencies.py===
```python
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db

DatabaseSession = Annotated[Session, Depends(get_db)]
```

===FILE: app/time_utils.py===
```python
from datetime import datetime, timezone


def to_utc_naive(value: datetime) -> datetime:
    """
    Convertit une date timezone-aware en date UTC naïve.

    SQLite ne préserve pas systématiquement le fuseau horaire. L'application
    stocke donc les instants en UTC sans information de fuseau dans la base.
    """
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(
            "La date et l'heure doivent inclure un fuseau horaire, par exemple Z ou +01:00."
        )

    return value.astimezone(timezone.utc).replace(tzinfo=None)


def utc_naive_to_iso(value: datetime) -> str:
    """Sérialise une date UTC naïve sous la forme ISO 8601 avec suffixe Z."""
    return value.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
```

===FILE: app/models.py===
```python
import enum
import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import Date, DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.database import Base


class AppointmentStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    first_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    phone: Mapped[str] = mapped_column(String(30), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    appointments: Mapped[list["Appointment"]] = relationship(
        back_populates="patient",
        cascade="all, delete-orphan",
    )


class Practitioner(Base):
    __tablename__ = "practitioners"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    first_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    specialty: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    phone: Mapped[str] = mapped_column(String(30), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    appointments: Mapped[list["Appointment"]] = relationship(
        back_populates="practitioner",
        cascade="all, delete-orphan",
    )


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("patients.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    practitioner_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("practitioners.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    starts_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    ends_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[AppointmentStatus] = mapped_column(
        Enum(AppointmentStatus, native_enum=False),
        nullable=False,
        default=AppointmentStatus.SCHEDULED,
        index=True,
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    patient: Mapped[Patient] = relationship(back_populates="appointments")
    practitioner: Mapped[Practitioner] = relationship(back_populates="appointments")
```

===FILE: app/schemas.py===
```python
import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_serializer, field_validator, model_validator

from app.models import AppointmentStatus
from app.time_utils import to_utc_naive, utc_naive_to_iso


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class PatientCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    phone: str = Field(min_length=5, max_length=30)
    date_of_birth: date


class PatientRead(APIModel):
    id: uuid.UUID
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    date_of_birth: date
    created_at: datetime


class PractitionerCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    specialty: str = Field(min_length=2, max_length=150)
    email: EmailStr
    phone: str = Field(min_length=5, max_length=30)


class PractitionerRead(APIModel):
    id: uuid.UUID
    first_name: str
    last_name: str
    specialty: str
    email: EmailStr
    phone: str
    created_at: datetime


class AppointmentCreate(BaseModel):
    patient_id: uuid.UUID
    practitioner_id: uuid.UUID
    starts_at: datetime
    ends_at: datetime
    reason: str = Field(min_length=2, max_length=500)
    notes: Optional[str] = Field(default=None, max_length=5000)

    @field_validator("starts_at", "ends_at")
    @classmethod
    def require_timezone_and_normalize(cls, value: datetime) -> datetime:
        return to_utc_naive(value)

    @model_validator(mode="after")
    def validate_dates(self):
        if self.ends_at <= self.starts_at:
            raise ValueError("La fin du rendez-vous doit être postérieure à son début.")
        return self


class AppointmentRead(APIModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    practitioner_id: uuid.UUID
    starts_at: datetime
    ends_at: datetime
    reason: str
    status: AppointmentStatus
    notes: Optional[str]
    created_at: datetime
    cancelled_at: Optional[datetime]

    @field_serializer("starts_at", "ends_at", "created_at", "cancelled_at")
    def serialize_utc_datetimes(self, value: Optional[datetime]) -> Optional[str]:
        if value is None:
            return None
        return utc_naive_to_iso(value)


class AppointmentCancel(BaseModel):
    cancellation_reason: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Motif administratif facultatif de l'annulation.",
    )


class AvailabilityRead(BaseModel):
    practitioner_id: uuid.UUID
    starts_at: datetime
    ends_at: datetime
    available: bool

    @field_serializer("starts_at", "ends_at")
    def serialize_utc_datetimes(self, value: datetime) -> str:
        return utc_naive_to_iso(value)
```

===FILE: app/routers/__init__.py===
```python
"""Routeurs HTTP de l'application."""
```

===FILE: app/routers/patients.py===
```python
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.dependencies import DatabaseSession
from app.models import Patient
from app.schemas import PatientCreate, PatientRead

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.post("", response_model=PatientRead, status_code=status.HTTP_201_CREATED)
def create_patient(payload: PatientCreate, db: DatabaseSession):
    patient = Patient(**payload.model_dump())
    db.add(patient)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un patient avec cette adresse e-mail existe déjà.",
        )

    db.refresh(patient)
    return patient


@router.get("", response_model=list[PatientRead])
def list_patients(db: DatabaseSession, skip: int = 0, limit: int = 100):
    limit = min(max(limit, 1), 100)
    statement = (
        select(Patient)
        .order_by(Patient.last_name, Patient.first_name)
        .offset(max(skip, 0))
        .limit(limit)
    )
    return list(db.scalars(statement).all())


@router.get("/{patient_id}", response_model=PatientRead)
def get_patient(patient_id: str, db: DatabaseSession):
    patient = db.get(Patient, patient_id)
    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient introuvable.",
        )
    return patient
```

===FILE: app/routers/practitioners.py===
```python
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.dependencies import DatabaseSession
from app.models import Practitioner
from app.schemas import PractitionerCreate, PractitionerRead

router = APIRouter(prefix="/practitioners", tags=["Praticiens"])


@router.post("", response_model=PractitionerRead, status_code=status.HTTP_201_CREATED)
def create_practitioner(payload: PractitionerCreate, db: DatabaseSession):
    practitioner = Practitioner(**payload.model_dump())
    db.add(practitioner)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un praticien avec cette adresse e-mail existe déjà.",
        )

    db.refresh(practitioner)
    return practitioner


@router.get("", response_model=list[PractitionerRead])
def list_practitioners(db: DatabaseSession, skip: int = 0, limit: int = 100):
    limit = min(max(limit, 1), 100)
    statement = (
        select(Practitioner)
        .order_by(Practitioner.last_name, Practitioner.first_name)
        .offset(max(skip, 0))
        .limit(limit)
    )
    return list(db.scalars(statement).all())


@router.get("/{practitioner_id}", response_model=PractitionerRead)
def get_practitioner(practitioner_id: str, db: DatabaseSession):
    practitioner = db.get(Practitioner, practitioner_id)
    if practitioner is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Praticien introuvable.",
        )
    return practitioner
```

===FILE: app/routers/appointments.py===
```python
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import and_, select

from app.dependencies import DatabaseSession
from app.models import Appointment, AppointmentStatus, Patient, Practitioner
from app.schemas import (
    AppointmentCancel,
    AppointmentCreate,
    AppointmentRead,
    AvailabilityRead,
)
from app.time_utils import to_utc_naive

router = APIRouter(prefix="/appointments", tags=["Rendez-vous"])


def find_overlapping_appointment(
    db: DatabaseSession,
    practitioner_id: UUID,
    starts_at: datetime,
    ends_at: datetime,
) -> Optional[Appointment]:
    """
    Détecte un chevauchement selon la règle :
    rendez-vous_existant.début < nouveau.fin ET rendez-vous_existant.fin > nouveau.début.
    """
    statement = select(Appointment).where(
        and_(
            Appointment.practitioner_id == practitioner_id,
            Appointment.status != AppointmentStatus.CANCELLED,
            Appointment.starts_at < ends_at,
            Appointment.ends_at > starts_at,
        )
    )
    return db.scalars(statement).first()


@router.get("/availability", response_model=AvailabilityRead)
def check_availability(
    practitioner_id: UUID,
    starts_at: datetime,
    ends_at: datetime,
    db: DatabaseSession,
):
    try:
        normalized_start = to_utc_naive(starts_at)
        normalized_end = to_utc_naive(ends_at)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        )

    if normalized_end <= normalized_start:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La fin du créneau doit être postérieure à son début.",
        )

    practitioner = db.get(Practitioner, practitioner_id)
    if practitioner is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Praticien introuvable.",
        )

    overlap = find_overlapping_appointment(
        db,
        practitioner_id,
        normalized_start,
        normalized_end,
    )

    return AvailabilityRead(
        practitioner_id=practitioner_id,
        starts_at=normalized_start,
        ends_at=normalized_end,
        available=overlap is None,
    )


@router.post("", response_model=AppointmentRead, status_code=status.HTTP_201_CREATED)
def create_appointment(payload: AppointmentCreate, db: DatabaseSession):
    patient = db.get(Patient, payload.patient_id)
    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient introuvable.",
        )

    practitioner = db.get(Practitioner, payload.practitioner_id)
    if practitioner is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Praticien introuvable.",
        )

    overlap = find_overlapping_appointment(
        db,
        payload.practitioner_id,
        payload.starts_at,
        payload.ends_at,
    )
    if overlap is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Le praticien possède déjà un rendez-vous actif "
                "sur ce créneau horaire."
            ),
        )

    appointment = Appointment(
        patient_id=payload.patient_id,
        practitioner_id=payload.practitioner_id,
        starts_at=payload.starts_at,
        ends_at=payload.ends_at,
        reason=payload.reason,
        notes=payload.notes,
        status=AppointmentStatus.SCHEDULED,
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment


@router.get("", response_model=list[AppointmentRead])
def list_appointments(
    db: DatabaseSession,
    patient_id: Optional[UUID] = None,
    practitioner_id: Optional[UUID] = None,
    appointment_status: Optional[AppointmentStatus] = Query(default=None, alias="status"),
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
):
    statement = select(Appointment)

    if patient_id is not None:
        statement = statement.where(Appointment.patient_id == patient_id)

    if practitioner_id is not None:
        statement = statement.where(Appointment.practitioner_id == practitioner_id)

    if appointment_status is not None:
        statement = statement.where(Appointment.status == appointment_status)

    if from_date is not None:
        try:
            statement = statement.where(Appointment.starts_at >= to_utc_naive(from_date))
        except ValueError as error:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(error),
            )

    if to_date is not None:
        try:
            statement = statement.where(Appointment.ends_at <= to_utc_naive(to_date))
        except ValueError as error:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(error),
            )

    statement = (
        statement.order_by(Appointment.starts_at)
        .offset(max(skip, 0))
        .limit(min(max(limit, 1), 100))
    )

    return list(db.scalars(statement).all())


@router.get("/{appointment_id}", response_model=AppointmentRead)
def get_appointment(appointment_id: UUID, db: DatabaseSession):
    appointment = db.get(Appointment, appointment_id)
    if appointment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rendez-vous introuvable.",
        )
    return appointment


@router.post("/{appointment_id}/cancel", response_model=AppointmentRead)
def cancel_appointment(
    appointment_id: UUID,
    payload: AppointmentCancel,
    db: DatabaseSession,
):
    appointment = db.get(Appointment, appointment_id)
    if appointment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rendez-vous introuvable.",
        )

    if appointment.status == AppointmentStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ce rendez-vous est déjà annulé.",
        )

    if appointment.status == AppointmentStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un rendez-vous terminé ne peut pas être annulé.",
        )

    appointment.status = AppointmentStatus.CANCELLED
    appointment.cancelled_at = datetime.utcnow()

    if payload.cancellation_reason:
        previous_notes = appointment.notes or ""
        cancellation_note = f"Annulation : {payload.cancellation_reason}"
        appointment.notes = (
            f"{previous_notes}\n{cancellation_note}".strip()
            if previous_notes
            else cancellation_note
        )

    db.commit()
    db.refresh(appointment)
    return appointment
```

===FILE: app/main.py===
```python
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.database import Base, engine
from app.routers import appointments, patients, practitioners


@asynccontextmanager
async def lifespan(app: FastAPI):
    del app
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "API de gestion de patients, praticiens et rendez-vous médicaux. "
        "Les dates et heures doivent être transmises avec un fuseau horaire "
        "et sont stockées en UTC."
    ),
    lifespan=lifespan,
)

app.include_router(patients.router)
app.include_router(practitioners.router)
app.include_router(appointments.router)


@app.get("/health", tags=["Supervision"])
def health_check():
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.app_version,
    }
```

===FILE: tests/test_api.py===
```python
from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def teardown_function():
    Base.metadata.drop_all(bind=engine)


def create_patient(client: TestClient) -> dict:
    response = client.post(
        "/patients",
        json={
            "first_name": "Alice",
            "last_name": "Martin",
            "email": "alice.martin@example.test",
            "phone": "+33102030405",
            "date_of_birth": "1988-04-12",
        },
    )
    assert response.status_code == 201
    return response.json()


def create_practitioner(client: TestClient) -> dict:
    response = client.post(
        "/practitioners",
        json={
            "first_name": "Julien",
            "last_name": "Durand",
            "specialty": "Médecine générale",
            "email": "julien.durand@cabinet-example.test",
            "phone": "+33106070809",
        },
    )
    assert response.status_code == 201
    return response.json()


def test_health_endpoint():
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_appointment_and_detect_conflict():
    with TestClient(app) as client:
        patient = create_patient(client)
        practitioner = create_practitioner(client)

        first_appointment = client.post(
            "/appointments",
            json={
                "patient_id": patient["id"],
                "practitioner_id": practitioner["id"],
                "starts_at": "2026-05-10T09:00:00Z",
                "ends_at": "2026-05-10T09:30:00Z",
                "reason": "Consultation de suivi fictive",
            },
        )

        assert first_appointment.status_code == 201
        assert first_appointment.json()["status"] == "scheduled"

        conflicting_appointment = client.post(
            "/appointments",
            json={
                "patient_id": patient["id"],
                "practitioner_id": practitioner["id"],
                "starts_at": "2026-05-10T09:15:00Z",
                "ends_at": "2026-05-10T09:45:00Z",
                "reason": "Créneau fictif en conflit",
            },
        )

        assert conflicting_appointment.status_code == 409
        assert "déjà un rendez-vous actif" in conflicting_appointment.json()["detail"]


def test_cancelled_appointment_releases_slot():
    with TestClient(app) as client:
        patient = create_patient(client)
        practitioner = create_practitioner(client)

        creation = client.post(
            "/appointments",
            json={
                "patient_id": patient["id"],
                "practitioner_id": practitioner["id"],
                "starts_at": "2026-06-15T14:00:00Z",
                "ends_at": "2026-06-15T14:30:00Z",
                "reason": "Consultation fictive à annuler",
            },
        )
        assert creation.status_code == 201

        appointment_id = creation.json()["id"]

        cancellation = client.post(
            f"/appointments/{appointment_id}/cancel",
            json={"cancellation_reason": "Patient fictif indisponible"},
        )
        assert cancellation.status_code == 200
        assert cancellation.json()["status"] == "cancelled"

        replacement = client.post(
            "/appointments",
            json={
                "patient_id": patient["id"],
                "practitioner_id": practitioner["id"],
                "starts_at": "2026-06-15T14:00:00Z",
                "ends_at": "2026-06-15T14:30:00Z",
                "reason": "Nouveau rendez-vous fictif",
            },
        )

        assert replacement.status_code == 201


def test_availability_endpoint():
    with TestClient(app) as client:
        practitioner = create_practitioner(client)

        response = client.get(
            "/appointments/availability",
            params={
                "practitioner_id": practitioner["id"],
                "starts_at": "2026-07-01T10:00:00Z",
                "ends_at": "2026-07-01T10:30:00Z",
            },
        )

        assert response.status_code == 200
        assert response.json()["available"] is True
```

# 6. Limites connues et hypothèses

- L’authentification et la gestion des rôles ne sont pas implémentées. En production, il faudrait prévoir des rôles tels que `administrateur`, `secrétaire`, `praticien` et éventuellement `patient`.
- SQLite est utilisé par défaut pour simplifier l’exécution locale. Une base PostgreSQL est recommandée pour la production.
- La prévention des chevauchements est assurée au niveau applicatif. Dans un contexte fortement concurrent, il faudrait renforcer cette protection avec des transactions adaptées ou une contrainte d’exclusion PostgreSQL.
- Les horaires sont obligatoirement fournis avec un fuseau horaire, puis normalisés et stockés en UTC.
- Les champs patients restent volontairement minimaux : aucun dossier médical, diagnostic, traitement, document médical ou information clinique sensible n’est géré.
- La solution ne remplace pas un logiciel certifié de gestion médicale ni un système conforme à toutes les obligations réglementaires de santé.
- Aucun système de notification par e-mail, SMS ou calendrier externe n’est inclus.
- Il n’existe pas encore de gestion de disponibilités récurrentes, de congés praticiens, de salles de consultation ou de listes d’attente.