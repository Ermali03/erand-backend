"""expand patient admission fields

Revision ID: 20260410_0003
Revises: 20260407_0002
Create Date: 2026-04-10 11:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260410_0003"
down_revision: Union[str, Sequence[str], None] = "20260407_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "patients",
        sa.Column("gender", sa.String(), nullable=True, server_default="male"),
    )
    op.add_column("patients", sa.Column("address", sa.String(), nullable=True))
    op.add_column("patients", sa.Column("phone", sa.String(), nullable=True))
    op.add_column(
        "patients",
        sa.Column("emergency_contact", sa.String(), nullable=True),
    )
    op.add_column(
        "patients",
        sa.Column("admission_source", sa.String(), nullable=True, server_default="ED"),
    )
    op.add_column(
        "patients",
        sa.Column("admission_datetime", sa.String(), nullable=True),
    )
    op.add_column(
        "patients",
        sa.Column("reason_for_admission", sa.String(), nullable=True),
    )
    op.add_column(
        "patients",
        sa.Column("past_medical_history", sa.String(), nullable=True),
    )
    op.add_column("patients", sa.Column("allergies", sa.String(), nullable=True))
    op.add_column(
        "patients",
        sa.Column("current_medications", sa.String(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("patients", "current_medications")
    op.drop_column("patients", "allergies")
    op.drop_column("patients", "past_medical_history")
    op.drop_column("patients", "reason_for_admission")
    op.drop_column("patients", "admission_datetime")
    op.drop_column("patients", "admission_source")
    op.drop_column("patients", "emergency_contact")
    op.drop_column("patients", "phone")
    op.drop_column("patients", "address")
    op.drop_column("patients", "gender")
