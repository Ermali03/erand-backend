from pydantic import BaseModel
from typing import Optional

class DoctorBase(BaseModel):
    name: str
    specialty: str
    role: str

class DoctorCreate(DoctorBase):
    id: str

class Doctor(DoctorBase):
    id: str
    roles: list[str] = []

    model_config = {"from_attributes": True}

class PatientBase(BaseModel):
    full_name: str
    date_of_birth: Optional[str] = None
    gender: Optional[str] = "male"
    address: Optional[str] = None
    phone: Optional[str] = None
    emergency_contact: Optional[str] = None
    admission_source: Optional[str] = "ED"
    admission_datetime: Optional[str] = None
    reason_for_admission: Optional[str] = None
    past_medical_history: Optional[str] = None
    allergies: Optional[str] = None
    current_medications: Optional[str] = None
    status: str = "admitted"
    is_operated: bool = False

class PatientCreate(PatientBase):
    id: str

class PatientUpdate(BaseModel):
    full_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    emergency_contact: Optional[str] = None
    admission_source: Optional[str] = None
    admission_datetime: Optional[str] = None
    reason_for_admission: Optional[str] = None
    past_medical_history: Optional[str] = None
    allergies: Optional[str] = None
    current_medications: Optional[str] = None
    status: Optional[str] = None
    is_operated: Optional[bool] = None

class Patient(PatientBase):
    id: str

    model_config = {"from_attributes": True}

class AnamnesisBase(BaseModel):
    chief_complaint: str
    medical_history: str

class AnamnesisCreate(AnamnesisBase):
    patient_id: str

class Anamnesis(AnamnesisBase):
    id: int
    patient_id: str

    model_config = {"from_attributes": True}

class EpicrisisBase(BaseModel):
    diagnosis: str
    treatment_plan: str
    structured_data: Optional[str] = None

class EpicrisisCreate(EpicrisisBase):
    patient_id: str

class Epicrisis(EpicrisisBase):
    id: int
    patient_id: str

    model_config = {"from_attributes": True}

class SurgeryBase(BaseModel):
    procedure_name: str
    date: str
    notes: str
    structured_data: Optional[str] = None

class SurgeryCreate(SurgeryBase):
    patient_id: str
    surgeon_id: str

class Surgery(SurgeryBase):
    id: int
    patient_id: str
    surgeon_id: str

    model_config = {"from_attributes": True}

class DischargeBase(BaseModel):
    discharge_date: str
    instructions: str
    structured_data: Optional[str] = None

class DischargeCreate(DischargeBase):
    patient_id: str

class Discharge(DischargeBase):
    id: int
    patient_id: str

    model_config = {"from_attributes": True}

class PatientFull(Patient):
    anamnesis: Optional[Anamnesis] = None
    epicrisis: Optional[Epicrisis] = None
    surgery: Optional[Surgery] = None
    discharge_report: Optional[Discharge] = None

    model_config = {"from_attributes": True}
