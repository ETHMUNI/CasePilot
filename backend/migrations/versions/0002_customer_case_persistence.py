"""Create customer and case tables."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002_customer_case_persistence"
down_revision: str | None = "0001_postgres_baseline"
branch_labels: str | None = None
depends_on: str | None = None


case_status = postgresql.ENUM(
    "open",
    "in_progress",
    "resolved",
    "closed",
    name="case_status",
    create_type=False,
)
case_priority = postgresql.ENUM(
    "low",
    "medium",
    "high",
    "urgent",
    name="case_priority",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    case_status.create(bind, checkfirst=True)
    case_priority.create(bind, checkfirst=True)

    op.create_table(
        "customers",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("external_id", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("length(trim(name)) > 0", name="name_not_blank"),
        sa.PrimaryKeyConstraint("id", name="pk_customers"),
    )
    op.create_table(
        "cases",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("external_id", sa.String(length=255), nullable=True),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", case_status, nullable=False),
        sa.Column("priority", case_priority, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("length(trim(title)) > 0", name="title_not_blank"),
        sa.ForeignKeyConstraint(
            ["customer_id"],
            ["customers.id"],
            name="fk_cases_customer_id_customers",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_cases"),
    )
    op.create_index("ix_cases_customer_id", "cases", ["customer_id"])


def downgrade() -> None:
    op.drop_index("ix_cases_customer_id", table_name="cases")
    op.drop_table("cases")
    op.drop_table("customers")
    case_priority.drop(op.get_bind(), checkfirst=True)
    case_status.drop(op.get_bind(), checkfirst=True)
