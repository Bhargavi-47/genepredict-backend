from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.dependencies import get_current_user, require_admin

router = APIRouter(prefix="/api", tags=["Admin & Dashboard"])


@router.get("/dashboard", response_model=schemas.DashboardStats)
def dashboard_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    patient_ids = [p.id for p in db.query(models.Patient.id).filter(models.Patient.user_id == current_user.id)]

    total_patients = len(patient_ids)
    total_uploads = db.query(models.UploadedFile).filter(models.UploadedFile.uploaded_by == current_user.id).count()
    total_predictions = (
        db.query(models.Prediction).filter(models.Prediction.patient_id.in_(patient_ids)).count()
        if patient_ids else 0
    )
    disease_categories = (
        db.query(models.Prediction.disease)
        .filter(models.Prediction.patient_id.in_(patient_ids))
        .distinct()
        .count()
        if patient_ids else 0
    )
    drug_recommendations = (
        db.query(models.DrugRecommendation)
        .join(models.Prediction)
        .filter(models.Prediction.patient_id.in_(patient_ids))
        .count()
        if patient_ids else 0
    )

    return schemas.DashboardStats(
        total_patients=total_patients,
        total_uploads=total_uploads,
        total_predictions=total_predictions,
        disease_categories=disease_categories,
        drug_recommendations=drug_recommendations,
    )


@router.get("/admin/users", response_model=List[schemas.UserOut])
def list_all_users(
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin),
):
    return db.query(models.User).order_by(models.User.created_at.desc()).all()


@router.get("/admin/analytics")
def system_analytics(
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin),
):
    return {
        "total_users": db.query(models.User).count(),
        "total_patients": db.query(models.Patient).count(),
        "total_predictions": db.query(models.Prediction).count(),
        "total_reports": db.query(models.Report).count(),
    }
