"""add doctor specialty

Revision ID: 20260407_0002
Revises: 20260306_0001
Create Date: 2026-04-07 12:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260407_0002"
down_revision: Union[str, Sequence[str], None] = "20260306_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "doctors",
        sa.Column("email", sa.String(), nullable=True),
    )
    op.create_index(op.f("ix_doctors_email"), "doctors", ["email"], unique=True)
    op.add_column(
        "doctors",
        sa.Column(
            "specialty",
            sa.String(),
            nullable=False,
            server_default="General Medicine",
        ),
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_doctors_email"), table_name="doctors")
    op.drop_column("doctors", "email")
    op.drop_column("doctors", "specialty")
