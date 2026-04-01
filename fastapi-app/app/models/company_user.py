from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class CompanyUser(Base):
    __tablename__ = "company_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    _key: Mapped[str | None] = mapped_column(String(255), nullable=True)
    uuid: Mapped[str] = mapped_column(String(36), unique=True, index=True)
    company_uuid: Mapped[str | None] = mapped_column(String(36), index=True)
    user_uuid: Mapped[str | None] = mapped_column(String(36), index=True)
    status: Mapped[str] = mapped_column(String(255), default="active")
    deleted_at: Mapped[DateTime | None] = mapped_column(DateTime)
    created_at: Mapped[DateTime | None] = mapped_column(DateTime, index=True)
    updated_at: Mapped[DateTime | None] = mapped_column(DateTime)

    company: Mapped["Company"] = relationship(
        "Company",
        primaryjoin="foreign(CompanyUser.company_uuid)==Company.uuid",
        back_populates="company_users",
    )
    user: Mapped["User"] = relationship(
        "User",
        primaryjoin="foreign(CompanyUser.user_uuid)==User.uuid",
        back_populates="company_users",
    )



