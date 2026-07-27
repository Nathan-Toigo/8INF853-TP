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