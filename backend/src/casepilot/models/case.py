from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    Text,
    Uuid,
    func,
)
from sqlalchemy import (
    Enum as SqlEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from casepilot.models.base import Base
from casepilot.models.case_priority import CasePriority
from casepilot.models.case_status import CaseStatus

if TYPE_CHECKING:
    from casepilot.models.customer import Customer


class Case(Base):
    __tablename__ = "cases"
    __table_args__ = (
        CheckConstraint("length(trim(title)) > 0", name="title_not_blank"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    external_id: Mapped[str | None] = mapped_column(String(255))
    customer_id: Mapped[UUID] = mapped_column(
        ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[CaseStatus] = mapped_column(
        SqlEnum(
            CaseStatus,
            name="case_status",
            values_callable=lambda values: [value.value for value in values],
            validate_strings=True,
        ),
        nullable=False,
    )
    priority: Mapped[CasePriority] = mapped_column(
        SqlEnum(
            CasePriority,
            name="case_priority",
            values_callable=lambda values: [value.value for value in values],
            validate_strings=True,
        ),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    customer: Mapped[Customer] = relationship("Customer", back_populates="cases")
