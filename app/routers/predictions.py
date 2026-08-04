from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.dependencies import get_current_user
from app.routers.patients import _get_owned_patient
from app.ml_service import run_inference

router = APIRouter(prefix="/api/predict", tags=["Predictions"])


@router.post("", response_model=schemas.PredictionOut, status_code=201)
def predict(
    payload: schemas.PredictionRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    _get_owned_patient(db, payload.patient_id, current_user)

    result = run_inference(
        gene_name=payload.gene_name,
        mutation_type=payload.mutation_type,
        chromosome=payload.chromosome,
    )

    prediction = models.Prediction(
        patient_id=payload.patient_id,
        mutation_id=payload.mutation_id,
        disease=result["disease"],
        risk_level=result["risk_level"],
        confidence=result["confidence"],
        probability=result["probability"],
        recommended_drug=result["recommended_drug"],
        model_version=result["model_version"],
        inference_time_ms=result["inference_time_ms"],
    )
    db.add(prediction)
    db.flush()  # get prediction.id before commit

    for drug in result["drug_recommendations"]:
        db.add(models.DrugRecommendation(
            prediction_id=prediction.id,
            drug_name=drug["drug_name"],
            effectiveness=drug.get("effectiveness"),
            risk_level=drug.get("risk_level"),
        ))

    db.commit()
    db.refresh(prediction)
    return prediction


@router.get("/patient/{patient_id}", response_model=List[schemas.PredictionOut])
def list_predictions_for_patient(
    patient_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    _get_owned_patient(db, patient_id, current_user)
    return (
        db.query(models.Prediction)
        .filter(models.Prediction.patient_id == patient_id)
        .order_by(models.Prediction.created_at.desc())
        .all()
    )


@router.get("/{prediction_id}", response_model=schemas.PredictionOut)
def get_prediction(
    prediction_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    prediction = db.query(models.Prediction).filter(models.Prediction.id == prediction_id).first()
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    _get_owned_patient(db, prediction.patient_id, current_user)
    return prediction
