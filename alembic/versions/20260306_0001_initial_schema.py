"""initial schema

Revision ID: 20260306_0001
Revises:
Create Date: 2026-03-06 23:59:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260306_0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "doctors",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("role", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_doctors_id"), "doctors", ["id"], unique=False)
    op.create_index(op.f("ix_doctors_name"), "doctors", ["name"], unique=False)

    op.create_table(
        "patients",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("full_name", sa.String(), nullable=True),
        sa.Column("date_of_birth", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=True),
        sa.Column("is_operated", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_patients_full_name"), "patients", ["full_name"], unique=False)
    op.create_index(op.f("ix_patients_id"), "patients", ["id"], unique=False)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

    op.create_table(
        "anamnesis_records",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("patient_id", sa.String(), nullable=False),
        sa.Column("chief_complaint", sa.String(), nullable=True),
        sa.Column("medical_history", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("patient_id"),
    )
    op.create_index(op.f("ix_anamnesis_records_id"), "anamnesis_records", ["id"], unique=False)

    op.create_table(
        "discharge_records",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("patient_id", sa.String(), nullable=False),
        sa.Column("discharge_date", sa.String(), nullable=True),
        sa.Column("instructions", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("patient_id"),
    )
    op.create_index(op.f("ix_discharge_records_id"), "discharge_records", ["id"], unique=False)

    op.create_table(
        "epicrisis_records",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("patient_id", sa.String(), nullable=False),
        sa.Column("diagnosis", sa.String(), nullable=True),
        sa.Column("treatment_plan", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("patient_id"),
    )
    op.create_index(op.f("ix_epicrisis_records_id"), "epicrisis_records", ["id"], unique=False)

    op.create_table(
        "surgery_records",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("patient_id", sa.String(), nullable=False),
        sa.Column("procedure_name", sa.String(), nullable=True),
        sa.Column("surgeon_id", sa.String(), nullable=True),
        sa.Column("date", sa.String(), nullable=True),
        sa.Column("notes", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"]),
        sa.ForeignKeyConstraint(["surgeon_id"], ["doctors.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("patient_id"),
    )
    op.create_index(op.f("ix_surgery_records_id"), "surgery_records", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_surgery_records_id"), table_name="surgery_records")
    op.drop_table("surgery_records")

    op.drop_index(op.f("ix_epicrisis_records_id"), table_name="epicrisis_records")
    op.drop_table("epicrisis_records")

    op.drop_index(op.f("ix_discharge_records_id"), table_name="discharge_records")
    op.drop_table("discharge_records")

    op.drop_index(op.f("ix_anamnesis_records_id"), table_name="anamnesis_records")
    op.drop_table("anamnesis_records")

    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")

    op.drop_index(op.f("ix_patients_id"), table_name="patients")
    op.drop_index(op.f("ix_patients_full_name"), table_name="patients")
    op.drop_table("patients")

    op.drop_index(op.f("ix_doctors_name"), table_name="doctors")
    op.drop_index(op.f("ix_doctors_id"), table_name="doctors")
    op.drop_table("doctors")
