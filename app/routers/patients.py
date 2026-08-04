from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/patients", tags=["Patients"])


@router.get("", response_model=List[schemas.PatientOut])
def list_patients(
    search: Optional[str] = Query(None, description="Search by patient name"),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    query = db.query(models.Patient).filter(models.Patient.user_id == current_user.id)
    if search:
        query = query.filter(models.Patient.patient_name.ilike(f"%{search}%"))
    return query.order_by(models.Patient.created_at.desc()).offset(skip).limit(limit).all()


@router.post("", response_model=schemas.PatientOut, status_code=201)
def create_patient(
    payload: schemas.PatientCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    patient = models.Patient(user_id=current_user.id, **payload.model_dump())
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


@router.get("/{patient_id}", response_model=schemas.PatientOut)
def get_patient(
    patient_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    patient = _get_owned_patient(db, patient_id, current_user)
    return patient


@router.put("/{patient_id}", response_model=schemas.PatientOut)
def update_patient(
    patient_id: str,
    payload: schemas.PatientUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    patient = _get_owned_patient(db, patient_id, current_user)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(patient, field, value)
    db.commit()
    db.refresh(patient)
    return patient


@router.delete("/{patient_id}", status_code=204)
def delete_patient(
    patient_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    patient = _get_owned_patient(db, patient_id, current_user)
    db.delete(patient)
    db.commit()
    return None


def _get_owned_patient(db: Session, patient_id: str, current_user: models.User) -> models.Patient:
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    if patient.user_id != current_user.id and current_user.role != models.UserRole.administrator:
        raise HTTPException(status_code=403, detail="Not authorized to access this patient")
    return patient
