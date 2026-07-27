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