import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, Enum
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class UserRole(str, enum.Enum):
    researcher = "researcher"
    doctor = "doctor"
    student = "student"
    administrator = "administrator"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    full_name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    phone = Column(String(30), nullable=True)
    institution = Column(String(200), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.researcher, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    two_factor_enabled = Column(Boolean, default=False)
    profile_photo_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    patients = relationship("Patient", back_populates="owner")
    notifications = relationship("Notification", back_populates="user")


class Patient(Base):
    __tablename__ = "patients"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    patient_name = Column(String(150), nullable=False)
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=True)
    blood_group = Column(String(10), nullable=True)
    medical_history = Column(Text, nullable=True)
    disease_history = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="patients")
    mutations = relationship("Mutation", back_populates="patient")
    predictions = relationship("Prediction", back_populates="patient")
    files = relationship("UploadedFile", back_populates="patient")


class Mutation(Base):
    __tablename__ = "mutations"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    patient_id = Column(UUID(as_uuid=False), ForeignKey("patients.id"), nullable=False)
    gene_name = Column(String(100), nullable=False)
    chromosome = Column(String(20), nullable=True)
    mutation_type = Column(String(100), nullable=True)
    position = Column(String(50), nullable=True)
    reference_allele = Column(String(50), nullable=True)
    alternate_allele = Column(String(50), nullable=True)
    raw_data = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient", back_populates="mutations")


class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    patient_id = Column(UUID(as_uuid=False), ForeignKey("patients.id"), nullable=True)
    uploaded_by = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    original_filename = Column(String(300), nullable=False)
    stored_path = Column(String(500), nullable=False)
    file_type = Column(String(20), nullable=False)  # csv, xlsx, vcf, fasta, txt
    size_bytes = Column(Integer, nullable=True)
    status = Column(String(30), default="uploaded")  # uploaded, validated, processed, failed
    created_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient", back_populates="files")


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    patient_id = Column(UUID(as_uuid=False), ForeignKey("patients.id"), nullable=False)
    mutation_id = Column(UUID(as_uuid=False), ForeignKey("mutations.id"), nullable=True)
    disease = Column(String(150), nullable=False)
    risk_level = Column(String(20), nullable=True)  # low, moderate, high
    confidence = Column(Float, nullable=False)
    probability = Column(Float, nullable=False)
    recommended_drug = Column(String(150), nullable=True)
    model_version = Column(String(50), nullable=True)
    inference_time_ms = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient", back_populates="predictions")
    drug_recommendations = relationship("DrugRecommendation", back_populates="prediction")
    report = relationship("Report", back_populates="prediction", uselist=False)


class DrugRecommendation(Base):
    __tablename__ = "drug_recommendations"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    prediction_id = Column(UUID(as_uuid=False), ForeignKey("predictions.id"), nullable=False)
    drug_name = Column(String(150), nullable=False)
    effectiveness = Column(Float, nullable=True)
    dosage_suggestion = Column(String(200), nullable=True)
    side_effects = Column(Text, nullable=True)
    interactions = Column(Text, nullable=True)
    alternatives = Column(Text, nullable=True)
    risk_level = Column(String(20), nullable=True)

    prediction = relationship("Prediction", back_populates="drug_recommendations")


class Report(Base):
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    prediction_id = Column(UUID(as_uuid=False), ForeignKey("predictions.id"), nullable=False)
    pdf_path = Column(String(500), nullable=True)
    doctor_notes = Column(Text, nullable=True)
    qr_code_path = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    prediction = relationship("Prediction", back_populates="report")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=True)
    action = Column(String(200), nullable=False)
    entity_type = Column(String(100), nullable=True)
    entity_id = Column(String(100), nullable=True)
    ip_address = Column(String(50), nullable=True)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")
