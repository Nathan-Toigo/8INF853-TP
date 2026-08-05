# 1. Description du problème résolu et utilisateurs cibles

Le projet **« Gestion de rendez-vous médicaux »** permet de centraliser la gestion des rendez-vous entre patients et praticiens dans un établissement de santé.

Il couvre notamment :

- l’enregistrement des patients ;
- la gestion des praticiens et de leurs spécialités ;
- la création de rendez-vous ;
- la détection des conflits de planning pour un praticien ;
- la consultation des rendez-vous selon différents critères ;
- la confirmation, l’annulation ou le marquage d’un rendez-vous comme terminé ;
- la consultation des créneaux disponibles d’un praticien sur une journée donnée.

Utilisateurs cibles :

- **Secrétaires médicales** : création et modification des rendez-vous ;
- **Praticiens** : consultation de leur agenda et mise à jour du statut des consultations ;
- **Personnel administratif** : gestion des patients et professionnels de santé ;
- **Patients** : indirectement, via une future interface de prise de rendez-vous connectée à cette API.

---

# 2. Modèle de données

## Entité `Patient`

| Attribut | Type | Description |
|---|---|---|
| `id` | entier | Identifiant unique |
| `first_name` | texte | Prénom |
| `last_name` | texte | Nom |
| `birth_date` | date | Date de naissance |
| `phone` | texte | Numéro de téléphone |
| `email` | texte | Adresse e-mail, unique |
| `created_at` | date/heure | Date de création du dossier |

Relations :

- Un patient peut posséder plusieurs rendez-vous.
- Un rendez-vous appartient à un seul patient.

## Entité `Practitioner`

| Attribut | Type | Description |
|---|---|---|
| `id` | entier | Identifiant unique |
| `first_name` | texte | Prénom |
| `last_name` | texte | Nom |
| `specialty` | texte | Spécialité médicale |
| `email` | texte | Adresse e-mail professionnelle, unique |
| `phone` | texte | Numéro de téléphone |
| `is_active` | booléen | Indique si le praticien peut recevoir des rendez-vous |
| `created_at` | date/heure | Date de création |

Relations :

- Un praticien peut posséder plusieurs rendez-vous.
- Un rendez-vous concerne un seul praticien.

## Entité `Appointment`

| Attribut | Type | Description |
|---|---|---|
| `id` | entier | Identifiant unique |
| `patient_id` | entier | Référence vers le patient |
| `practitioner_id` | entier | Référence vers le praticien |
| `start_at` | date/heure | Début du rendez-vous |
| `end_at` | date/heure | Fin du rendez-vous |
| `reason` | texte | Motif facultatif du rendez-vous |
| `status` | énumération | `scheduled`, `confirmed`, `cancelled`, `completed` |
| `notes` | texte | Notes administratives ou médicales non sensibles dans cette démonstration |
| `created_at` | date/heure | Date de création |
| `updated_at` | date/heure | Date de dernière modification |

Règle métier principale :

- Deux rendez-vous actifs (`scheduled` ou `confirmed`) ne peuvent pas se chevaucher pour un même praticien.
- Les rendez-vous annulés et terminés ne bloquent plus les créneaux.

---

# 3. Fonctionnalités principales

## Patients

- `POST /patients` : créer un patient ;
- `GET /patients` : lister les patients ;
- `GET /patients/{patient_id}` : consulter un patient ;
- `PUT /patients/{patient_id}` : mettre à jour un patient.

## Praticiens

- `POST /practitioners` : créer un praticien ;
- `GET /practitioners` : lister les praticiens ;
- `GET /practitioners/{practitioner_id}` : consulter un praticien ;
- `PUT /practitioners/{practitioner_id}` : mettre à jour un praticien ;
- `PATCH /practitioners/{practitioner_id}/deactivate` : désactiver un praticien.

## Rendez-vous

- `POST /appointments` : créer un rendez-vous ;
- `GET /appointments` : lister les rendez-vous avec filtres ;
- `GET /appointments/{appointment_id}` : consulter un rendez-vous ;
- `PATCH /appointments/{appointment_id}/status` : modifier le statut ;
- `POST /appointments/{appointment_id}/cancel` : annuler un rendez-vous ;
- `GET /practitioners/{practitioner_id}/availability` : consulter les créneaux disponibles pour une date donnée.

## Documentation

- `GET /docs` : interface Swagger générée automatiquement par FastAPI ;
- `GET /health` : contrôle simple de disponibilité de l’API.

---

# 4. Proposition d’architecture technique

## Technologies

- **Python 3.12+**
- **FastAPI** : API REST performante et documentation OpenAPI automatique
- **SQLAlchemy 2.x** : ORM et accès à la base de données
- **SQLite** : base de données locale simple pour le démarrage
- **Pydantic v2** : validation des entrées et sérialisation des réponses
- **Pytest** : tests automatisés
- **Uvicorn** : serveur ASGI

## Organisation des dossiers

```text
gestion-rendez-vous-medicaux/
├── requirements.txt
├── README.md
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── services.py
│   └── routers/
│       ├── __init__.py
│       ├── appointments.py
│       ├── patients.py
│       └── practitioners.py
└── tests/
    ├── __init__.py
    ├── conftest.py
    └── test_appointments.py
```

---

# 5. Code source complet et exécutable

===FILE: requirements.txt===
```txt
fastapi==0.115.12
uvicorn[standard]==0.34.2
sqlalchemy==2.0.40
pydantic==2.11.4
email-validator==2.2.0
pytest==8.3.5
httpx==0.28.1
```

===FILE: README.md===
```md
# Gestion de rendez-vous médicaux

API REST de démonstration pour gérer des patients, des praticiens et leurs rendez-vous médicaux.

## Prérequis

- Python 3.12 ou version supérieure
- pip

## Installation

```bash
python -m venv .venv
```

Sous Linux ou macOS :

```bash
source .venv/bin/activate
```

Sous Windows PowerShell :

```powershell
.venv\Scripts\Activate.ps1
```

Installer les dépendances :

```bash
pip install -r requirements.txt
```

## Lancement

```bash
uvicorn app.main:app --reload
```

L'API est disponible sur :

- API : http://127.0.0.1:8000
- Documentation Swagger : http://127.0.0.1:8000/docs
- Documentation ReDoc : http://127.0.0.1:8000/redoc

La base SQLite est créée automatiquement dans le fichier `medical_appointments.db`.

## Tests

```bash
pytest
```

## Exemple de création d'un patient

```bash
curl -X POST "http://127.0.0.1:8000/patients" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Alice",
    "last_name": "Martin",
    "birth_date": "1990-05-12",
    "phone": "+33612345678",
    "email": "alice.martin@example.test"
  }'
```

## Exemple de création d'un praticien

```bash
curl -X POST "http://127.0.0.1:8000/practitioners" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Jean",
    "last_name": "Dupont",
    "specialty": "Médecine générale",
    "email": "jean.dupont@cabinet.test",
    "phone": "+33144556677"
  }'
```

## Exemple de création d'un rendez-vous

```bash
curl -X POST "http://127.0.0.1:8000/appointments" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": 1,
    "practitioner_id": 1,
    "start_at": "2030-01-15T09:00:00",
    "end_at": "2030-01-15T09:30:00",
    "reason": "Consultation de suivi"
  }'
```
```

===FILE: app/__init__.py===
```python
```

===FILE: app/config.py===
```python
import os


class Settings:
    app_name: str = "Gestion de rendez-vous médicaux"
    database_url: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./medical_appointments.db",
    )
    default_appointment_duration_minutes: int = 30
    workday_start_hour: int = 8
    workday_end_hour: int = 18


settings = Settings()
```

===FILE: app/database.py===
```python
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings


connect_args = (
    {"check_same_thread": False}
    if settings.database_url.startswith("sqlite")
    else {}
)

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    future=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

===FILE: app/models.py===
```python
import enum
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class AppointmentStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    phone: Mapped[str] = mapped_column(String(30), nullable=False)
    email: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    appointments: Mapped[list["Appointment"]] = relationship(
        back_populates="patient",
    )


class Practitioner(Base):
    __tablename__ = "practitioners"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    specialty: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    appointments: Mapped[list["Appointment"]] = relationship(
        back_populates="practitioner",
    )


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patients.id"),
        nullable=False,
        index=True,
    )
    practitioner_id: Mapped[int] = mapped_column(
        ForeignKey("practitioners.id"),
        nullable=False,
        index=True,
    )
    start_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    end_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[AppointmentStatus] = mapped_column(
        Enum(AppointmentStatus, native_enum=False),
        default=AppointmentStatus.SCHEDULED,
        nullable=False,
        index=True,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    patient: Mapped[Patient] = relationship(back_populates="appointments")
    practitioner: Mapped[Practitioner] = relationship(
        back_populates="appointments",
    )
```

===FILE: app/schemas.py===
```python
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

from app.models import AppointmentStatus


class PatientBase(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    birth_date: date
    phone: str = Field(min_length=5, max_length=30)
    email: EmailStr | None = None


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    birth_date: date | None = None
    phone: str | None = Field(default=None, min_length=5, max_length=30)
    email: EmailStr | None = None


class PatientRead(PatientBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class PractitionerBase(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    specialty: str = Field(min_length=2, max_length=150)
    email: EmailStr
    phone: str | None = Field(default=None, min_length=5, max_length=30)
    is_active: bool = True


class PractitionerCreate(PractitionerBase):
    pass


class PractitionerUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    specialty: str | None = Field(default=None, min_length=2, max_length=150)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, min_length=5, max_length=30)
    is_active: bool | None = None


class PractitionerRead(PractitionerBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class AppointmentCreate(BaseModel):
    patient_id: int = Field(gt=0)
    practitioner_id: int = Field(gt=0)
    start_at: datetime
    end_at: datetime
    reason: str | None = Field(default=None, max_length=500)
    notes: str | None = None

    @model_validator(mode="after")
    def validate_dates(self) -> "AppointmentCreate":
        if self.end_at <= self.start_at:
            raise ValueError(
                "La date de fin doit être strictement postérieure à la date de début."
            )
        return self


class AppointmentStatusUpdate(BaseModel):
    status: AppointmentStatus


class AppointmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int
    practitioner_id: int
    start_at: datetime
    end_at: datetime
    reason: str | None
    status: AppointmentStatus
    notes: str | None
    created_at: datetime
    updated_at: datetime


class AvailabilitySlot(BaseModel):
    start_at: datetime
    end_at: datetime


class AvailabilityRead(BaseModel):
    practitioner_id: int
    date: date
    slot_duration_minutes: int
    available_slots: list[AvailabilitySlot]
```

===FILE: app/services.py===
```python
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
```

===FILE: app/routers/__init__.py===
```python
```

===FILE: app/routers/patients.py===
```python
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Patient
from app.schemas import PatientCreate, PatientRead, PatientUpdate


router = APIRouter(prefix="/patients", tags=["Patients"])


@router.post("", response_model=PatientRead, status_code=status.HTTP_201_CREATED)
def create_patient(payload: PatientCreate, db: Session = Depends(get_db)) -> Patient:
    patient = Patient(**payload.model_dump())

    try:
        db.add(patient)
        db.commit()
        db.refresh(patient)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un patient possède déjà cette adresse e-mail.",
        ) from exc

    return patient


@router.get("", response_model=list[PatientRead])
def list_patients(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    search: str | None = Query(default=None, min_length=1),
    db: Session = Depends(get_db),
) -> list[Patient]:
    statement = select(Patient).order_by(Patient.last_name, Patient.first_name)

    if search:
        normalized_search = f"%{search.strip()}%"
        statement = statement.where(
            (Patient.first_name.ilike(normalized_search))
            | (Patient.last_name.ilike(normalized_search))
        )

    return list(db.scalars(statement.offset(skip).limit(limit)).all())


@router.get("/{patient_id}", response_model=PatientRead)
def get_patient(patient_id: int, db: Session = Depends(get_db)) -> Patient:
    patient = db.get(Patient, patient_id)

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient introuvable.",
        )

    return patient


@router.put("/{patient_id}", response_model=PatientRead)
def update_patient(
    patient_id: int,
    payload: PatientUpdate,
    db: Session = Depends(get_db),
) -> Patient:
    patient = db.get(Patient, patient_id)

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient introuvable.",
        )

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(patient, field, value)

    try:
        db.commit()
        db.refresh(patient)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un patient possède déjà cette adresse e-mail.",
        ) from exc

    return patient
```

===FILE: app/routers/practitioners.py===
```python
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Practitioner
from app.schemas import (
    AvailabilityRead,
    AvailabilitySlot,
    PractitionerCreate,
    PractitionerRead,
    PractitionerUpdate,
)
from app.services import get_available_slots


router = APIRouter(prefix="/practitioners", tags=["Praticiens"])


@router.post("", response_model=PractitionerRead, status_code=status.HTTP_201_CREATED)
def create_practitioner(
    payload: PractitionerCreate,
    db: Session = Depends(get_db),
) -> Practitioner:
    practitioner = Practitioner(**payload.model_dump())

    try:
        db.add(practitioner)
        db.commit()
        db.refresh(practitioner)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un praticien possède déjà cette adresse e-mail.",
        ) from exc

    return practitioner


@router.get("", response_model=list[PractitionerRead])
def list_practitioners(
    active_only: bool = Query(default=False),
    specialty: str | None = Query(default=None, min_length=2),
    db: Session = Depends(get_db),
) -> list[Practitioner]:
    statement = select(Practitioner).order_by(
        Practitioner.last_name,
        Practitioner.first_name,
    )

    if active_only:
        statement = statement.where(Practitioner.is_active.is_(True))

    if specialty:
        statement = statement.where(
            Practitioner.specialty.ilike(f"%{specialty.strip()}%")
        )

    return list(db.scalars(statement).all())


@router.get("/{practitioner_id}", response_model=PractitionerRead)
def get_practitioner(
    practitioner_id: int,
    db: Session = Depends(get_db),
) -> Practitioner:
    practitioner = db.get(Practitioner, practitioner_id)

    if practitioner is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Praticien introuvable.",
        )

    return practitioner


@router.put("/{practitioner_id}", response_model=PractitionerRead)
def update_practitioner(
    practitioner_id: int,
    payload: PractitionerUpdate,
    db: Session = Depends(get_db),
) -> Practitioner:
    practitioner = db.get(Practitioner, practitioner_id)

    if practitioner is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Praticien introuvable.",
        )

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(practitioner, field, value)

    try:
        db.commit()
        db.refresh(practitioner)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un praticien possède déjà cette adresse e-mail.",
        ) from exc

    return practitioner


@router.patch(
    "/{practitioner_id}/deactivate",
    response_model=PractitionerRead,
)
def deactivate_practitioner(
    practitioner_id: int,
    db: Session = Depends(get_db),
) -> Practitioner:
    practitioner = db.get(Practitioner, practitioner_id)

    if practitioner is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Praticien introuvable.",
        )

    practitioner.is_active = False
    db.commit()
    db.refresh(practitioner)
    return practitioner


@router.get("/{practitioner_id}/availability", response_model=AvailabilityRead)
def practitioner_availability(
    practitioner_id: int,
    target_date: date = Query(alias="date"),
    slot_duration_minutes: int = Query(default=30, ge=10, le=120),
    db: Session = Depends(get_db),
) -> AvailabilityRead:
    practitioner = db.get(Practitioner, practitioner_id)

    if practitioner is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Praticien introuvable.",
        )

    slots = get_available_slots(
        db=db,
        practitioner_id=practitioner_id,
        target_date=target_date,
        slot_duration_minutes=slot_duration_minutes,
    )

    return AvailabilityRead(
        practitioner_id=practitioner_id,
        date=target_date,
        slot_duration_minutes=slot_duration_minutes,
        available_slots=[
            AvailabilitySlot(start_at=start_at, end_at=end_at)
            for start_at, end_at in slots
        ],
    )
```

===FILE: app/routers/appointments.py===
```python
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Appointment, AppointmentStatus, Patient, Practitioner
from app.schemas import (
    AppointmentCreate,
    AppointmentRead,
    AppointmentStatusUpdate,
)
from app.services import (
    get_appointment_conflict,
    practitioner_can_accept_appointments,
)


router = APIRouter(prefix="/appointments", tags=["Rendez-vous"])


@router.post("", response_model=AppointmentRead, status_code=status.HTTP_201_CREATED)
def create_appointment(
    payload: AppointmentCreate,
    db: Session = Depends(get_db),
) -> Appointment:
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

    if not practitioner_can_accept_appointments(practitioner):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ce praticien est inactif et ne peut pas recevoir de rendez-vous.",
        )

    conflict = get_appointment_conflict(
        db=db,
        practitioner_id=payload.practitioner_id,
        start_at=payload.start_at,
        end_at=payload.end_at,
    )

    if conflict is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Le praticien possède déjà un rendez-vous actif "
                "sur ce créneau."
            ),
        )

    appointment = Appointment(
        patient_id=payload.patient_id,
        practitioner_id=payload.practitioner_id,
        start_at=payload.start_at,
        end_at=payload.end_at,
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
    patient_id: int | None = Query(default=None, gt=0),
    practitioner_id: int | None = Query(default=None, gt=0),
    appointment_status: AppointmentStatus | None = Query(
        default=None,
        alias="status",
    ),
    start_from: datetime | None = Query(default=None),
    end_to: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[Appointment]:
    statement = select(Appointment).order_by(Appointment.start_at)

    if patient_id is not None:
        statement = statement.where(Appointment.patient_id == patient_id)

    if practitioner_id is not None:
        statement = statement.where(
            Appointment.practitioner_id == practitioner_id
        )

    if appointment_status is not None:
        statement = statement.where(Appointment.status == appointment_status)

    if start_from is not None:
        statement = statement.where(Appointment.start_at >= start_from)

    if end_to is not None:
        statement = statement.where(Appointment.end_at <= end_to)

    return list(db.scalars(statement).all())


@router.get("/{appointment_id}", response_model=AppointmentRead)
def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
) -> Appointment:
    appointment = db.get(Appointment, appointment_id)

    if appointment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rendez-vous introuvable.",
        )

    return appointment


@router.patch("/{appointment_id}/status", response_model=AppointmentRead)
def update_appointment_status(
    appointment_id: int,
    payload: AppointmentStatusUpdate,
    db: Session = Depends(get_db),
) -> Appointment:
    appointment = db.get(Appointment, appointment_id)

    if appointment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rendez-vous introuvable.",
        )

    if payload.status in (
        AppointmentStatus.SCHEDULED,
        AppointmentStatus.CONFIRMED,
    ):
        conflict = get_appointment_conflict(
            db=db,
            practitioner_id=appointment.practitioner_id,
            start_at=appointment.start_at,
            end_at=appointment.end_at,
            excluded_appointment_id=appointment.id,
        )

        if conflict is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Impossible d'activer ce rendez-vous : "
                    "le créneau est déjà occupé."
                ),
            )

    appointment.status = payload.status
    db.commit()
    db.refresh(appointment)
    return appointment


@router.post("/{appointment_id}/cancel", response_model=AppointmentRead)
def cancel_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
) -> Appointment:
    appointment = db.get(Appointment, appointment_id)

    if appointment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rendez-vous introuvable.",
        )

    appointment.status = AppointmentStatus.CANCELLED
    db.commit()
    db.refresh(appointment)
    return appointment
```

===FILE: app/main.py===
```python
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, engine
from app.routers import appointments, patients, practitioners


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Gestion de rendez-vous médicaux",
    description=(
        "API REST de gestion des patients, praticiens et rendez-vous médicaux."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(patients.router)
app.include_router(practitioners.router)
app.include_router(appointments.router)


@app.get("/health", tags=["Système"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
```

===FILE: tests/__init__.py===
```python
```

===FILE: tests/conftest.py===
```python
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


TEST_DATABASE_PATH = Path("test_medical_appointments.db")
os.environ["DATABASE_URL"] = f"sqlite:///./{TEST_DATABASE_PATH}"


from app.database import Base, engine
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def prepare_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

    if TEST_DATABASE_PATH.exists():
        TEST_DATABASE_PATH.unlink()


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client
```

===FILE: tests/test_appointments.py===
```python
from fastapi.testclient import TestClient


def create_patient(client: TestClient) -> int:
    response = client.post(
        "/patients",
        json={
            "first_name": "Alice",
            "last_name": "Martin",
            "birth_date": "1990-05-12",
            "phone": "+33612345678",
            "email": "alice.martin@example.test",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def create_practitioner(client: TestClient) -> int:
    response = client.post(
        "/practitioners",
        json={
            "first_name": "Jean",
            "last_name": "Dupont",
            "specialty": "Médecine générale",
            "email": "jean.dupont@cabinet.test",
            "phone": "+33144556677",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_create_appointment(client: TestClient):
    patient_id = create_patient(client)
    practitioner_id = create_practitioner(client)

    response = client.post(
        "/appointments",
        json={
            "patient_id": patient_id,
            "practitioner_id": practitioner_id,
            "start_at": "2030-01-15T09:00:00",
            "end_at": "2030-01-15T09:30:00",
            "reason": "Consultation de suivi fictive",
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["patient_id"] == patient_id
    assert payload["practitioner_id"] == practitioner_id
    assert payload["status"] == "scheduled"


def test_reject_overlapping_appointment(client: TestClient):
    patient_id = create_patient(client)
    practitioner_id = create_practitioner(client)

    first_response = client.post(
        "/appointments",
        json={
            "patient_id": patient_id,
            "practitioner_id": practitioner_id,
            "start_at": "2030-02-20T10:00:00",
            "end_at": "2030-02-20T10:30:00",
            "reason": "Contrôle fictif",
        },
    )
    assert first_response.status_code == 201

    conflict_response = client.post(
        "/appointments",
        json={
            "patient_id": patient_id,
            "practitioner_id": practitioner_id,
            "start_at": "2030-02-20T10:15:00",
            "end_at": "2030-02-20T10:45:00",
            "reason": "Créneau conflictuel fictif",
        },
    )

    assert conflict_response.status_code == 409
    assert "créneau" in conflict_response.json()["detail"].lower()


def test_cancelled_appointment_frees_slot(client: TestClient):
    patient_id = create_patient(client)
    practitioner_id = create_practitioner(client)

    appointment_response = client.post(
        "/appointments",
        json={
            "patient_id": patient_id,
            "practitioner_id": practitioner_id,
            "start_at": "2030-03-10T14:00:00",
            "end_at": "2030-03-10T14:30:00",
            "reason": "Rendez-vous fictif à annuler",
        },
    )
    assert appointment_response.status_code == 201

    appointment_id = appointment_response.json()["id"]
    cancel_response = client.post(f"/appointments/{appointment_id}/cancel")
    assert cancel_response.status_code == 200
    assert cancel_response.json()["status"] == "cancelled"

    replacement_response = client.post(
        "/appointments",
        json={
            "patient_id": patient_id,
            "practitioner_id": practitioner_id,
            "start_at": "2030-03-10T14:00:00",
            "end_at": "2030-03-10T14:30:00",
            "reason": "Nouveau rendez-vous fictif",
        },
    )

    assert replacement_response.status_code == 201
```

---

# 6. Limites connues et hypothèses

- L’application utilise SQLite pour simplifier le démarrage. En production, PostgreSQL est recommandé.
- Aucun mécanisme d’authentification ou de gestion des rôles n’est inclus. Une version de production devrait intégrer OAuth2, JWT, SSO ou une solution d’identité compatible avec les exigences de l’établissement.
- Les données présentées dans les exemples et les tests sont entièrement fictives.
- Les dates sont stockées sous forme de dates/heures sans fuseau horaire. L’hypothèse retenue est que tous les utilisateurs opèrent dans le même fuseau, idéalement UTC en production.
- Les horaires d’ouverture sont fixes : de 08h00 à 18h00, configurés dans `app/config.py`.
- Les créneaux disponibles sont calculés avec une durée par défaut de 30 minutes.
- La détection des conflits est applicative. Pour des déploiements fortement concurrents, PostgreSQL avec contraintes d’exclusion ou mécanismes transactionnels renforcés est recommandé.
- Les notes de rendez-vous ne doivent pas contenir de données médicales sensibles dans cette démonstration. Un système réel doit appliquer les exigences réglementaires applicables, notamment RGPD, chiffrement, journalisation, gestion des accès et politique de conservation des données.
