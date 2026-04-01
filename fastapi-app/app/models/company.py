from sqlalchemy import Integer, String, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    _key: Mapped[str | None] = mapped_column(String(255), nullable=True)
    uuid: Mapped[str | None] = mapped_column(String(191), unique=True, index=True)
    public_id: Mapped[str | None] = mapped_column(String(191), unique=True, index=True)
    stripe_id: Mapped[str | None] = mapped_column(String(191), index=True)
    stripe_connect_id: Mapped[str | None] = mapped_column(String(191))
    trial_ends_at: Mapped[DateTime | None] = mapped_column(DateTime)
    card_last_four: Mapped[str | None] = mapped_column(String(4))
    card_brand: Mapped[str | None] = mapped_column(String(255))
    owner_uuid: Mapped[str | None] = mapped_column(String(191), index=True)
    logo_uuid: Mapped[str | None] = mapped_column(String(191), index=True)
    backdrop_uuid: Mapped[str | None] = mapped_column(String(191), index=True)
    name: Mapped[str | None] = mapped_column(String(255))
    website_url: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(String(255))
    options: Mapped[dict | None] = mapped_column(JSON)
    phone: Mapped[str | None] = mapped_column(String(255))
    currency: Mapped[str | None] = mapped_column(String(255))
    country: Mapped[str | None] = mapped_column(String(255))
    timezone: Mapped[str | None] = mapped_column(String(255))
    place_uuid: Mapped[str | None] = mapped_column(String(191), index=True)
    plan: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str | None] = mapped_column(String(255))
    type: Mapped[str | None] = mapped_column(String(191), index=True)
    slug: Mapped[str | None] = mapped_column(String(255))
    deleted_at: Mapped[DateTime | None] = mapped_column(DateTime)
    created_at: Mapped[DateTime | None] = mapped_column(DateTime, index=True)
    updated_at: Mapped[DateTime | None] = mapped_column(DateTime)

    company_users: Mapped[list["CompanyUser"]] = relationship(
        "CompanyUser",
        primaryjoin="Company.uuid==foreign(CompanyUser.company_uuid)",
        back_populates="company",
    )



