# Enterprise Learning Management System (LMS)

A modern, scalable, multi-tenant capable Enterprise Learning Management System built for **Students**, **Instructors**, and **Platform Administrators**.

---

## 1. System Architecture

The project follows a **Decoupled 3-Tier Architecture** utilizing a **domain-oriented modular monolith** backend for high development velocity and clear future microservice boundaries:

```
[Presentation Tier] : React 18 + TypeScript + Vite + Tailwind CSS + TanStack Query + React Router
        │ (REST / JSON)
[Application Tier]  : FastAPI (Python 3.11+) + Pydantic v2 + Uvicorn
        ├── auth            ├── enrollment
        ├── users           ├── progress
        ├── courses         ├── assessment
        ├── modules         ├── analytics
        ├── lessons         ├── notifications & audit
        │
[Data Tier]         : PostgreSQL 16 (Relational Source of Truth)
                    : MongoDB 7.0 (Rich Content & Dynamic Question Banks)
                    : Redis 7.0 (Ephemeral State, Cache, Rate Limits)
```

---

## 2. Prerequisites

- **Node.js**: `v20+` (or `v18+`)
- **npm**: `v10+`
- **Python**: `3.11+`
- **Docker & Docker Compose**: (Optional for containerized run)

---

## 3. Environment Configuration

Copy `.env.example` to `.env` in the root and in the backend folder:

```bash
cp .env.example .env
cp .env.example backend/.env
```

Key environment variables:
- `DATABASE_URL`: PostgreSQL connection string (e.g. `postgresql+asyncpg://postgres:postgres@localhost:5432/enterprise_lms`)
- `MONGODB_URL`: MongoDB connection string (e.g. `mongodb://root:example@localhost:27017`)
- `REDIS_URL`: Redis connection URL (e.g. `redis://localhost:6379/0`)
- `JWT_SECRET`: Secret key for signing JWT tokens (min 32 chars)
- `CORS_ORIGINS`: Comma-separated allowlist of frontend URLs
- `SEED_DEMO_USERS`: Set `true` in local development to seed initial users with credentials provided via `SEED_ADMIN_PASSWORD`, `SEED_INSTRUCTOR_PASSWORD`, and `SEED_STUDENT_PASSWORD` (automatically disabled in production).

---

## 4. Local Development Quickstart

### Backend (FastAPI)

1. Create and activate a Python virtual environment:
   ```bash
   cd backend
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On Linux/macOS:
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   - Interactive API Docs (Swagger): `http://localhost:8000/docs`
   - Alternative API Docs (ReDoc): `http://localhost:8000/redoc`
   - Health Probe: `http://localhost:8000/health`

### Frontend (React + Vite)

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```
   - Application URL: `http://localhost:5173`

---

## 5. Automated Testing

Run the backend test suite:

```bash
# From the repository root (or backend folder):
pytest backend/tests -v
```

---

## 6. Dockerized & Production Deployment

### Quick Local Docker Compose:
```bash
docker compose up --build
```

### Production Deployment (Multi-Stage with Ingress Gateway & SSL):
```bash
# 1. Copy and customize production environment
cp .env.production .env

# 2. Launch production stack (Nginx Ingress, Backend, Frontend, Postgres, Mongo, Redis)
docker compose -f docker-compose.prod.yml up -d --build

# 3. Verify health probe
curl http://localhost/health
```

For complete production guidelines, SSL setup, and domain configuration, refer to [docs/deployment.md](docs/deployment.md).

---

## 7. Automated Backups & Disaster Recovery

Run automated multi-database backups (PostgreSQL, MongoDB, Redis):

**Linux / macOS:**
```bash
chmod +x infra/scripts/backup.sh
./infra/scripts/backup.sh
```

**Windows (PowerShell):**
```powershell
.\infra\scripts\backup.ps1
```

---

## 8. Automated Testing & Verification

Run the full end-to-end test suite:

```bash
# Backend pytest suite (60 tests across 14 modules)
pytest backend/tests -v

# Frontend production typecheck & Vite build
cd frontend && npm run build
```

---

## 9. Comprehensive Documentation Suite

- [ARCHITECTURE.md](ARCHITECTURE.md): Decoupled 3-tier architecture, data modeling strategies, and polyglot persistence.
- [PROJECT_PLAN.md](PROJECT_PLAN.md): Phase-by-phase delivery roadmap across all 11 phases.
- [docs/deployment.md](docs/deployment.md): Complete Production Deployment & Operations Runbook.
- [docs/testing.md](docs/testing.md): Full QA, Integration & Security Testing Report.
- [docs/ui-ux.md](docs/ui-ux.md): Design tokens, UI component specifications, and accessibility guide.
- [docs/caching.md](docs/caching.md): Redis caching architecture, TTL configs, and automated invalidation.
- [docs/content-management.md](docs/content-management.md): MongoDB flexible content modeling & storage patterns.
- [docs/assessments.md](docs/assessments.md): Auto-grading and certification engine mechanics.
- [docs/student-learning-flow.md](docs/student-learning-flow.md): Student learning journey & player architecture.
- [docs/curriculum-management.md](docs/curriculum-management.md): Course management & curriculum studio documentation.
