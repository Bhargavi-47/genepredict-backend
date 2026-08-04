from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.dependencies import get_current_user
from app.routers.patients import _get_owned_patient

router = APIRouter(prefix="/api/reports", tags=["Reports"])


@router.post("", response_model=schemas.ReportOut, status_code=201)
def create_report(
    payload: schemas.ReportCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    prediction = db.query(models.Prediction).filter(models.Prediction.id == payload.prediction_id).first()
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    _get_owned_patient(db, prediction.patient_id, current_user)

    existing = db.query(models.Report).filter(models.Report.prediction_id == payload.prediction_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="A report already exists for this prediction")

    # PDF generation (with hospital logo, QR code, doctor notes) plugs in here in Phase 4.
    report = models.Report(
        prediction_id=payload.prediction_id,
        doctor_notes=payload.doctor_notes,
        pdf_path=None,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@router.get("", response_model=List[schemas.ReportOut])
def list_reports(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return (
        db.query(models.Report)
        .join(models.Prediction)
        .join(models.Patient)
        .filter(models.Patient.user_id == current_user.id)
        .order_by(models.Report.created_at.desc())
        .all()
    )


@router.get("/{report_id}", response_model=schemas.ReportOut)
def get_report(
    report_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    report = db.query(models.Report).filter(models.Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    _get_owned_patient(db, report.prediction.patient_id, current_user)
    return report
