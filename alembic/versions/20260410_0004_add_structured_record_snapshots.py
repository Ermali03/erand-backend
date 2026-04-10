"""add structured record snapshots

Revision ID: 20260410_0004
Revises: 20260410_0003
Create Date: 2026-04-10 18:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260410_0004"
down_revision: Union[str, Sequence[str], None] = "20260410_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "epicrisis_records",
        sa.Column("structured_data", sa.Text(), nullable=True),
    )
    op.add_column(
        "surgery_records",
        sa.Column("structured_data", sa.Text(), nullable=True),
    )
    op.add_column(
        "discharge_records",
        sa.Column("structured_data", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("discharge_records", "structured_data")
    op.drop_column("surgery_records", "structured_data")
    op.drop_column("epicrisis_records", "structured_data")
