import os
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.dependencies import get_current_user
from app.config import get_settings

router = APIRouter(prefix="/api/uploads", tags=["Dataset Upload"])

settings = get_settings()
ALLOWED_EXTENSIONS = {"csv", "xlsx", "xls", "vcf", "fasta", "fa", "txt"}


def _extension(filename: str) -> str:
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


@router.post("", status_code=201)
async def upload_dataset(
    file: UploadFile = File(...),
    patient_id: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    ext = _extension(file.filename)
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '.{ext}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    if patient_id:
        patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        if patient.user_id != current_user.id and current_user.role != models.UserRole.administrator:
            raise HTTPException(status_code=403, detail="Not authorized to upload for this patient")

    os.makedirs(settings.upload_dir, exist_ok=True)

    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > settings.max_upload_size_mb:
        raise HTTPException(
            status_code=400,
            detail=f"File too large ({size_mb:.1f} MB). Max is {settings.max_upload_size_mb} MB.",
        )

    record = models.UploadedFile(
        patient_id=patient_id,
        uploaded_by=current_user.id,
        original_filename=file.filename,
        stored_path="",  # set below once we know the id
        file_type=ext,
        size_bytes=len(contents),
        status="uploaded",
    )
    db.add(record)
    db.flush()

    stored_path = os.path.join(settings.upload_dir, f"{record.id}_{file.filename}")
    with open(stored_path, "wb") as f:
        f.write(contents)
    record.stored_path = stored_path

    db.commit()
    db.refresh(record)

    # Lightweight preview: first few lines of text-based formats.
    preview_lines: List[str] = []
    if ext in {"csv", "txt", "vcf", "fasta", "fa"}:
        try:
            preview_lines = contents.decode("utf-8", errors="ignore").splitlines()[:10]
        except Exception:
            preview_lines = []

    return {
        "id": record.id,
        "original_filename": record.original_filename,
        "file_type": record.file_type,
        "size_bytes": record.size_bytes,
        "status": record.status,
        "patient_id": record.patient_id,
        "created_at": record.created_at,
        "preview": preview_lines,
    }


@router.get("")
def list_uploads(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    uploads = (
        db.query(models.UploadedFile)
        .filter(models.UploadedFile.uploaded_by == current_user.id)
        .order_by(models.UploadedFile.created_at.desc())
        .all()
    )
    return [
        {
            "id": u.id,
            "original_filename": u.original_filename,
            "file_type": u.file_type,
            "size_bytes": u.size_bytes,
            "status": u.status,
            "patient_id": u.patient_id,
            "created_at": u.created_at,
        }
        for u in uploads
    ]
