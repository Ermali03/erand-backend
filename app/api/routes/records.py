from typing import List

from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser, SessionDep
from app.core.roles import RECORD_WRITE_ROLES, has_any_role
from app.models import (
    AnamnesisRecord,
    DischargeRecord,
    EpicrisisRecord,
    Patient,
    SurgeryRecord,
)
from app.schemas import domain

router = APIRouter()


def require_record_write_role(roles: str) -> None:
    if not has_any_role(roles, RECORD_WRITE_ROLES):
        raise HTTPException(status_code=403, detail="Not enough privileges")


def get_patient_or_404(db: SessionDep, patient_id: str) -> Patient:
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.post("/anamnesis", response_model=domain.Anamnesis)
def create_anamnesis(anamnesis: domain.AnamnesisCreate, db: SessionDep, current_user: CurrentUser):
    require_record_write_role(current_user.role)
    get_patient_or_404(db, anamnesis.patient_id)
    existing = (
        db.query(AnamnesisRecord)
        .filter(AnamnesisRecord.patient_id == anamnesis.patient_id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Anamnesis already exists for patient")

    db_anamnesis = AnamnesisRecord(**anamnesis.model_dump())
    db.add(db_anamnesis)
    db.commit()
    db.refresh(db_anamnesis)
    return db_anamnesis


@router.put("/anamnesis/{patient_id}", response_model=domain.Anamnesis)
def update_anamnesis(
    patient_id: str,
    anamnesis: domain.AnamnesisBase,
    db: SessionDep,
    current_user: CurrentUser,
):
    require_record_write_role(current_user.role)
    get_patient_or_404(db, patient_id)
    existing = (
        db.query(AnamnesisRecord)
        .filter(AnamnesisRecord.patient_id == patient_id)
        .first()
    )

    if existing is None:
        existing = AnamnesisRecord(patient_id=patient_id)
        db.add(existing)

    existing.chief_complaint = anamnesis.chief_complaint
    existing.medical_history = anamnesis.medical_history
    db.commit()
    db.refresh(existing)
    return existing


@router.get("/anamnesis/{patient_id}", response_model=List[domain.Anamnesis])
def read_anamnesis(patient_id: str, db: SessionDep, current_user: CurrentUser):
    records = db.query(AnamnesisRecord).filter(AnamnesisRecord.patient_id == patient_id).all()
    return records


@router.post("/epicrisis", response_model=domain.Epicrisis)
def create_epicrisis(epicrisis: domain.EpicrisisCreate, db: SessionDep, current_user: CurrentUser):
    require_record_write_role(current_user.role)
    patient = get_patient_or_404(db, epicrisis.patient_id)
    existing = (
        db.query(EpicrisisRecord)
        .filter(EpicrisisRecord.patient_id == epicrisis.patient_id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Epicrisis already exists for patient")

    db_epicrisis = EpicrisisRecord(**epicrisis.model_dump())
    db.add(db_epicrisis)
    patient.status = "in-treatment"
    db.commit()
    db.refresh(db_epicrisis)
    return db_epicrisis


@router.get("/epicrisis/{patient_id}", response_model=List[domain.Epicrisis])
def read_epicrisis(patient_id: str, db: SessionDep, current_user: CurrentUser):
    records = db.query(EpicrisisRecord).filter(EpicrisisRecord.patient_id == patient_id).all()
    return records


@router.put("/epicrisis/{patient_id}", response_model=domain.Epicrisis)
def update_epicrisis(
    patient_id: str,
    epicrisis: domain.EpicrisisBase,
    db: SessionDep,
    current_user: CurrentUser,
):
    require_record_write_role(current_user.role)
    patient = get_patient_or_404(db, patient_id)
    existing = (
        db.query(EpicrisisRecord)
        .filter(EpicrisisRecord.patient_id == patient_id)
        .first()
    )

    if existing is None:
        existing = EpicrisisRecord(patient_id=patient_id)
        db.add(existing)

    existing.diagnosis = epicrisis.diagnosis
    existing.treatment_plan = epicrisis.treatment_plan
    existing.structured_data = epicrisis.structured_data
    if patient.status not in {"operated", "discharged"}:
        patient.status = "in-treatment"
    db.commit()
    db.refresh(existing)
    return existing


@router.post("/surgery", response_model=domain.Surgery)
def create_surgery(surgery: domain.SurgeryCreate, db: SessionDep, current_user: CurrentUser):
    require_record_write_role(current_user.role)
    patient = get_patient_or_404(db, surgery.patient_id)
    existing = db.query(SurgeryRecord).filter(SurgeryRecord.patient_id == surgery.patient_id).first()
    if existing:
        raise HTTPException(status_code=409, detail="Surgery record already exists for patient")

    db_surgery = SurgeryRecord(**surgery.model_dump())
    db.add(db_surgery)
    patient.is_operated = True
    patient.status = "operated"
    db.commit()
    db.refresh(db_surgery)
    return db_surgery


@router.get("/surgery/{patient_id}", response_model=List[domain.Surgery])
def read_surgery(patient_id: str, db: SessionDep, current_user: CurrentUser):
    records = db.query(SurgeryRecord).filter(SurgeryRecord.patient_id == patient_id).all()
    return records


@router.put("/surgery/{patient_id}", response_model=domain.Surgery)
def update_surgery(
    patient_id: str,
    surgery: domain.SurgeryCreate,
    db: SessionDep,
    current_user: CurrentUser,
):
    require_record_write_role(current_user.role)
    patient = get_patient_or_404(db, patient_id)
    existing = (
        db.query(SurgeryRecord)
        .filter(SurgeryRecord.patient_id == patient_id)
        .first()
    )

    if existing is None:
        existing = SurgeryRecord(patient_id=patient_id)
        db.add(existing)

    existing.procedure_name = surgery.procedure_name
    existing.surgeon_id = surgery.surgeon_id
    existing.date = surgery.date
    existing.notes = surgery.notes
    existing.structured_data = surgery.structured_data
    patient.is_operated = True
    if patient.status != "discharged":
        patient.status = "operated"
    db.commit()
    db.refresh(existing)
    return existing


@router.post("/discharge", response_model=domain.Discharge)
def create_discharge(discharge: domain.DischargeCreate, db: SessionDep, current_user: CurrentUser):
    require_record_write_role(current_user.role)
    patient = get_patient_or_404(db, discharge.patient_id)
    existing = (
        db.query(DischargeRecord)
        .filter(DischargeRecord.patient_id == discharge.patient_id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Discharge record already exists for patient")

    db_discharge = DischargeRecord(**discharge.model_dump())
    db.add(db_discharge)
    patient.status = "discharged"
    db.commit()
    db.refresh(db_discharge)
    return db_discharge


@router.get("/discharge/{patient_id}", response_model=List[domain.Discharge])
def read_discharge(patient_id: str, db: SessionDep, current_user: CurrentUser):
    records = db.query(DischargeRecord).filter(DischargeRecord.patient_id == patient_id).all()
    return records


@router.put("/discharge/{patient_id}", response_model=domain.Discharge)
def update_discharge(
    patient_id: str,
    discharge: domain.DischargeBase,
    db: SessionDep,
    current_user: CurrentUser,
):
    require_record_write_role(current_user.role)
    patient = get_patient_or_404(db, patient_id)
    existing = (
        db.query(DischargeRecord)
        .filter(DischargeRecord.patient_id == patient_id)
        .first()
    )

    if existing is None:
        existing = DischargeRecord(patient_id=patient_id)
        db.add(existing)

    existing.discharge_date = discharge.discharge_date
    existing.instructions = discharge.instructions
    existing.structured_data = discharge.structured_data
    patient.status = "discharged"
    db.commit()
    db.refresh(existing)
    return existing
