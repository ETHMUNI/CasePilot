"""Establish PostgreSQL extensions required by CasePilot."""

import sqlalchemy as sa
from alembic import op

revision: str = "0001_postgres_baseline"
down_revision: str | None = None
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.execute(sa.text("CREATE EXTENSION IF NOT EXISTS vector"))


def downgrade() -> None:
    pass
