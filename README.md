# GenePredict AI — Backend (Phase 2: Database + REST APIs)

FastAPI + PostgreSQL backend for the GenePredict AI platform. This phase covers auth,
patient management, mutation records, prediction storage, reports, and admin/dashboard
endpoints — tested end-to-end and confirmed working.

## Important note

The `/api/predict` endpoint currently uses a **placeholder mock model** (`app/ml_service.py`),
not a trained deep learning model. It returns deterministic demo scores so the rest of the
app (frontend, DB writes, reports) can be built and tested against a real API contract.
Swap in a real trained model for Phase 3 before using this for anything beyond development.
Do not use this for real clinical decisions until it's backed by a validated model, and
be aware that real deployment on patient health data will need HIPAA-compliant hosting
and, if used to inform real treatment decisions, likely FDA review (Software as a Medical
Device).

## Quick start (Docker — recommended)

```bash
cp .env.example .env
docker compose up --build
```

API will be available at http://localhost:8000
Interactive docs (Swagger UI): http://localhost:8000/docs

## Quick start (local, without Docker)

Requires Python 3.11+ and a running PostgreSQL instance.

```bash
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# edit .env with your DATABASE_URL and a real SECRET_KEY

uvicorn app.main:app --reload
```

## Project structure

```
app/
  main.py            # FastAPI app, middleware, router registration
  config.py          # Settings loaded from .env
  database.py        # SQLAlchemy engine/session
  models.py          # ORM models: users, patients, mutations, predictions, etc.
  schemas.py         # Pydantic request/response schemas
  security.py        # Password hashing + JWT creation/verification
  dependencies.py    # get_current_user, role-based access control
  ml_service.py       # Placeholder prediction logic (replace in Phase 3)
  routers/
    auth.py          # signup, login, logout, forgot-password
    users.py         # profile get/update
    patients.py      # patient CRUD
    mutations.py     # mutation records per patient
    predictions.py   # run + fetch predictions
    reports.py       # report creation/listing
    admin.py         # dashboard stats, admin user list, system analytics
```

## API endpoints implemented

| Method | Path                              | Description                          |
|--------|-----------------------------------|---------------------------------------|
| POST   | /api/auth/signup                  | Register a new user                   |
| POST   | /api/auth/login                   | Get access + refresh tokens           |
| POST   | /api/auth/logout                  | Logout (stateless JWT)                |
| POST   | /api/auth/forgot-password          | Request password reset                |
| GET    | /api/auth/me                      | Current user info                     |
| GET/PUT| /api/users/me                     | View/update profile                   |
| GET/POST | /api/patients                   | List / create patients                |
| GET/PUT/DELETE | /api/patients/{id}          | View / update / delete a patient      |
| POST   | /api/mutations                    | Add a mutation record                 |
| GET    | /api/mutations/patient/{id}       | List mutations for a patient          |
| POST   | /api/predict                      | Run prediction on a mutation          |
| GET    | /api/predict/patient/{id}         | List predictions for a patient        |
| POST/GET | /api/reports                    | Create / list reports                 |
| GET    | /api/dashboard                    | Dashboard summary stats               |
| GET    | /api/admin/users                  | List all users (admin only)           |
| GET    | /api/admin/analytics               | System-wide analytics (admin only)    |

## Security features included

- Bcrypt password hashing
- JWT access + refresh tokens
- Role-based access control (researcher / doctor / student / administrator)
- Per-resource ownership checks (a user can only see their own patients)
- Rate limiting (slowapi) — wire up `@limiter.limit(...)` decorators on sensitive routes
- CORS configured via `.env`
- Generic responses on forgot-password to avoid leaking registered emails

## Not yet implemented (next phases)

- Real trained ML model (Phase 3)
- File upload endpoints for CSV/Excel/VCF/FASTA (Phase 3)
- PDF report generation with QR codes (Phase 4)
- Email verification + password reset emails
- Alembic migrations (currently uses `Base.metadata.create_all`)
- Audit log writes on each action (table exists, not yet populated)
- Notifications (table exists, not yet populated)
