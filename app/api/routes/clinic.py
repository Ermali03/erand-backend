from typing import List

from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import joinedload

from app.api.deps import CurrentUser, SessionDep
from app.core.roles import PATIENT_WRITE_ROLES, has_any_role, parse_roles, primary_role, serialize_roles
from app.models import Doctor, Patient
from app.schemas import domain

router = APIRouter()


def require_roles(current_user_roles: str, allowed_roles: set[str]) -> None:
    if not has_any_role(current_user_roles, allowed_roles):
        raise HTTPException(status_code=403, detail="Not enough privileges")


def doctor_to_response(doctor: Doctor) -> domain.Doctor:
    roles = parse_roles(doctor.role)
    return domain.Doctor(
        id=doctor.id,
        name=doctor.name,
        specialty=doctor.specialty,
        role=primary_role(roles),
        roles=roles,
    )


@router.get("/doctors", response_model=List[domain.Doctor])
def read_doctors(db: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100):
    doctors = db.query(Doctor).offset(skip).limit(limit).all()
    return [doctor_to_response(doctor) for doctor in doctors]


@router.post("/doctors", response_model=domain.Doctor)
def create_doctor(doctor: domain.DoctorCreate, db: SessionDep, current_user: CurrentUser):
    require_roles(current_user.role, {"Admin"})
    db_doctor = db.query(Doctor).filter(Doctor.id == doctor.id).first()
    if db_doctor:
        raise HTTPException(status_code=400, detail="Doctor already exists")
    db_doctor = Doctor(
        id=doctor.id,
        name=doctor.name,
        specialty=doctor.specialty,
        role=serialize_roles([doctor.role]),
    )
    db.add(db_doctor)
    db.commit()
    db.refresh(db_doctor)
    return doctor_to_response(db_doctor)


@router.get("/patients", response_model=List[domain.Patient])
def read_patients(db: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100):
    patients = db.query(Patient).offset(skip).limit(limit).all()
    return patients


@router.get("/patients/{patient_id}", response_model=domain.Patient)
def read_patient(patient_id: str, db: SessionDep, current_user: CurrentUser):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.post("/patients", response_model=domain.Patient)
def create_patient(patient: domain.PatientCreate, db: SessionDep, current_user: CurrentUser):
    require_roles(current_user.role, PATIENT_WRITE_ROLES)
    db_patient = db.query(Patient).filter(Patient.id == patient.id).first()
    if db_patient:
        raise HTTPException(status_code=400, detail="Patient already exists")
    db_patient = Patient(**patient.model_dump())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient


@router.put("/patients/{patient_id}", response_model=domain.Patient)
def update_patient(
    patient_id: str,
    patient_update: domain.PatientUpdate,
    db: SessionDep,
    current_user: CurrentUser,
):
    require_roles(current_user.role, PATIENT_WRITE_ROLES)
    db_patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")

    update_data = patient_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_patient, key, value)

    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient


@router.get("/patients/{patient_id}/full", response_model=domain.PatientFull)
def read_patient_full(patient_id: str, db: SessionDep, current_user: CurrentUser):
    patient = (
        db.query(Patient)
        .options(
            joinedload(Patient.anamnesis),
            joinedload(Patient.epicrisis),
            joinedload(Patient.surgery),
            joinedload(Patient.discharge_report),
        )
        .filter(Patient.id == patient_id)
        .first()
    )

    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient
