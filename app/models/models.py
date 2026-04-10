from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.db.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="Nurse")  # Admin, Main Surgeon, Doctor, Nurse

class Doctor(Base):
    __tablename__ = "doctors"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    specialty = Column(String, nullable=False, default="General Medicine")
    role = Column(String)
    
class Patient(Base):
    __tablename__ = "patients"
    
    id = Column(String, primary_key=True, index=True)
    full_name = Column(String, index=True)
    date_of_birth = Column(String, nullable=True)
    gender = Column(String, nullable=True, default="male")
    address = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    emergency_contact = Column(String, nullable=True)
    admission_source = Column(String, nullable=True, default="ED")
    admission_datetime = Column(String, nullable=True)
    reason_for_admission = Column(String, nullable=True)
    past_medical_history = Column(String, nullable=True)
    allergies = Column(String, nullable=True)
    current_medications = Column(String, nullable=True)
    status = Column(String, default="admitted")
    is_operated = Column(Boolean, default=False)
    
    anamnesis = relationship("AnamnesisRecord", back_populates="patient", uselist=False)
    epicrisis = relationship("EpicrisisRecord", back_populates="patient", uselist=False)
    surgery = relationship("SurgeryRecord", back_populates="patient", uselist=False)
    discharge_report = relationship("DischargeRecord", back_populates="patient", uselist=False)
    
class AnamnesisRecord(Base):
    __tablename__ = "anamnesis_records"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patients.id"), unique=True, nullable=False)
    chief_complaint = Column(String)
    medical_history = Column(String)
    
    patient = relationship("Patient", back_populates="anamnesis")
    
class EpicrisisRecord(Base):
    __tablename__ = "epicrisis_records"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patients.id"), unique=True, nullable=False)
    diagnosis = Column(String)
    treatment_plan = Column(String)
    structured_data = Column(Text, nullable=True)
    
    patient = relationship("Patient", back_populates="epicrisis")

class SurgeryRecord(Base):
    __tablename__ = "surgery_records"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patients.id"), unique=True, nullable=False)
    procedure_name = Column(String)
    surgeon_id = Column(String, ForeignKey("doctors.id"))
    date = Column(String)
    notes = Column(String)
    structured_data = Column(Text, nullable=True)
    
    patient = relationship("Patient", back_populates="surgery")
    surgeon = relationship("Doctor")

class DischargeRecord(Base):
    __tablename__ = "discharge_records"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patients.id"), unique=True, nullable=False)
    discharge_date = Column(String)
    instructions = Column(String)
    structured_data = Column(Text, nullable=True)
    
    patient = relationship("Patient", back_populates="discharge_report")
