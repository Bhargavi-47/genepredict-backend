from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models import UserRole


# ---------- Auth / Users ----------

class SignupRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str
    phone: Optional[str] = None
    institution: Optional[str] = None
    role: UserRole = UserRole.researcher

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v, info):
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Passwords do not match")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: str
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    institution: Optional[str] = None
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    institution: Optional[str] = None
    profile_photo_url: Optional[str] = None


# ---------- Patients ----------

class PatientCreate(BaseModel):
    patient_name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    medical_history: Optional[str] = None
    disease_history: Optional[str] = None


class PatientUpdate(BaseModel):
    patient_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    medical_history: Optional[str] = None
    disease_history: Optional[str] = None


class PatientOut(BaseModel):
    id: str
    patient_name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    medical_history: Optional[str] = None
    disease_history: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Mutations ----------

class MutationCreate(BaseModel):
    patient_id: str
    gene_name: str
    chromosome: Optional[str] = None
    mutation_type: Optional[str] = None
    position: Optional[str] = None
    reference_allele: Optional[str] = None
    alternate_allele: Optional[str] = None


class MutationOut(BaseModel):
    id: str
    patient_id: str
    gene_name: str
    chromosome: Optional[str] = None
    mutation_type: Optional[str] = None
    position: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Predictions ----------

class PredictionRequest(BaseModel):
    patient_id: str
    mutation_id: Optional[str] = None
    gene_name: str
    mutation_type: Optional[str] = None
    chromosome: Optional[str] = None
    position: Optional[str] = None


class DrugRecommendationOut(BaseModel):
    drug_name: str
    effectiveness: Optional[float] = None
    dosage_suggestion: Optional[str] = None
    side_effects: Optional[str] = None
    interactions: Optional[str] = None
    alternatives: Optional[str] = None
    risk_level: Optional[str] = None

    class Config:
        from_attributes = True


class PredictionOut(BaseModel):
    id: str
    patient_id: str
    disease: str
    risk_level: Optional[str] = None
    confidence: float
    probability: float
    recommended_drug: Optional[str] = None
    model_version: Optional[str] = None
    inference_time_ms: Optional[float] = None
    created_at: datetime
    drug_recommendations: List[DrugRecommendationOut] = []

    class Config:
        from_attributes = True


# ---------- Reports ----------

class ReportCreate(BaseModel):
    prediction_id: str
    doctor_notes: Optional[str] = None


class ReportOut(BaseModel):
    id: str
    prediction_id: str
    pdf_path: Optional[str] = None
    doctor_notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Dashboard / Admin ----------

class DashboardStats(BaseModel):
    total_patients: int
    total_uploads: int
    total_predictions: int
    disease_categories: int
    drug_recommendations: int
