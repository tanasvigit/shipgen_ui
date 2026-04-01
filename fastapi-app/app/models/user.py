from sqlalchemy import Integer, String, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    _key: Mapped[str | None] = mapped_column(String(255), nullable=True)
    uuid: Mapped[str | None] = mapped_column(String(191), unique=True, index=True)
    public_id: Mapped[str | None] = mapped_column(String(191), unique=True, index=True)
    company_uuid: Mapped[str | None] = mapped_column(String(191), index=True)
    avatar_uuid: Mapped[str | None] = mapped_column(String(191), index=True)
    username: Mapped[str | None] = mapped_column(String(191), unique=True)
    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(255))
    password: Mapped[str | None] = mapped_column(String(255))
    name: Mapped[str | None] = mapped_column(String(255))
    date_of_birth: Mapped[str | None] = mapped_column(String(255))
    timezone: Mapped[str | None] = mapped_column(String(255))
    country: Mapped[str | None] = mapped_column(String(255))
    ip_address: Mapped[str | None] = mapped_column(String(255))
    last_login: Mapped[str | None] = mapped_column(String(255))
    slug: Mapped[str | None] = mapped_column(String(255))
    type: Mapped[str | None] = mapped_column(String(191), index=True)
    status: Mapped[str | None] = mapped_column(String(255))
    meta: Mapped[dict | None] = mapped_column(JSON)
    remember_token: Mapped[str | None] = mapped_column(String(100))
    email_verified_at: Mapped[DateTime | None] = mapped_column(DateTime, index=True)
    phone_verified_at: Mapped[DateTime | None] = mapped_column(DateTime)
    deleted_at: Mapped[DateTime | None] = mapped_column(DateTime)
    created_at: Mapped[DateTime | None] = mapped_column(DateTime, index=True)
    updated_at: Mapped[DateTime | None] = mapped_column(DateTime)

    company_users: Mapped[list["CompanyUser"]] = relationship(
        "CompanyUser",
        primaryjoin="User.uuid==foreign(CompanyUser.user_uuid)",
        back_populates="user",
    )



