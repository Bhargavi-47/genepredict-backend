from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.dependencies import get_current_user
from app.routers.patients import _get_owned_patient

router = APIRouter(prefix="/api/mutations", tags=["Mutations"])


@router.post("", response_model=schemas.MutationOut, status_code=201)
def create_mutation(
    payload: schemas.MutationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    _get_owned_patient(db, payload.patient_id, current_user)  # authorization check
    mutation = models.Mutation(**payload.model_dump())
    db.add(mutation)
    db.commit()
    db.refresh(mutation)
    return mutation


@router.get("/patient/{patient_id}", response_model=List[schemas.MutationOut])
def list_mutations_for_patient(
    patient_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    _get_owned_patient(db, patient_id, current_user)
    return (
        db.query(models.Mutation)
        .filter(models.Mutation.patient_id == patient_id)
        .order_by(models.Mutation.created_at.desc())
        .all()
    )


@router.delete("/{mutation_id}", status_code=204)
def delete_mutation(
    mutation_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    mutation = db.query(models.Mutation).filter(models.Mutation.id == mutation_id).first()
    if not mutation:
        raise HTTPException(status_code=404, detail="Mutation not found")
    _get_owned_patient(db, mutation.patient_id, current_user)
    db.delete(mutation)
    db.commit()
    return None
