from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas, security
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/signup", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def signup(payload: schemas.SignupRequest, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email is already registered")

    user = models.User(
        full_name=payload.full_name,
        email=payload.email,
        password_hash=security.hash_password(payload.password),
        phone=payload.phone,
        institution=payload.institution,
        role=payload.role,
        is_verified=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # In production: send a verification email with a signed token here.
    return user


@router.post("/login", response_model=schemas.TokenResponse)
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user or not security.verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")

    access_token = security.create_access_token(subject=user.id, extra_claims={"role": user.role.value})
    refresh_token = security.create_refresh_token(subject=user.id)
    return schemas.TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/logout")
def logout(current_user: models.User = Depends(get_current_user)):
    # Stateless JWT: real invalidation requires a token blocklist (e.g. Redis) keyed by jti.
    return {"message": "Logged out successfully"}


@router.post("/forgot-password")
def forgot_password(payload: schemas.ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    # Always return a generic response so we don't leak which emails are registered.
    if user:
        pass  # In production: generate a reset token and email it to the user.
    return {"message": "If that email exists, a password reset link has been sent"}


@router.get("/me", response_model=schemas.UserOut)
def get_me(current_user: models.User = Depends(get_current_user)):
    return current_user
