# Enterprise Learning Management System (LMS)

[![Repository](https://img.shields.io/badge/GitHub-JeevananthanV%2Fenterprise--lms-blue?logo=github)](https://github.com/JeevananthanV/enterprise-lms)
[![React](https://img.shields.io/badge/Frontend-React%2018%20%2B%20TypeScript-61DAFB?logo=react&logoColor=white)](https://react.dev)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI%20(Python%203.11+)-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL%2016-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![MongoDB](https://img.shields.io/badge/Database-MongoDB%207-47A248?logo=mongodb&logoColor=white)](https://www.mongodb.com)
[![Redis](https://img.shields.io/badge/Cache-Redis%207-DC382D?logo=redis&logoColor=white)](https://redis.io)

A modern, scalable, multi-tenant capable Enterprise Learning Management System built for **Students**, **Instructors**, and **Platform Administrators**.

---

## 🔗 Repository Links

| Detail | Link |
|---|---|
| **GitHub Repository** | [https://github.com/JeevananthanV/enterprise-lms](https://github.com/JeevananthanV/enterprise-lms) |
| **Author** | [Jeevananthan V](https://github.com/JeevananthanV) |
| **Backend API Docs** | `http://localhost:8000/docs` |
| **Frontend Portal** | `http://localhost:5173` |

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

### Clone

```bash
git clone https://github.com/JeevananthanV/enterprise-lms.git
cd enterprise-lms
```

### Backend (FastAPI)

1. Create and activate a Python virtual environment:
```bash
python -m venv venv
# Linux/macOS
source venv/bin/activate
# Windows PowerShell
.\venv\Scripts\Activate.ps1
```

2. Install dependencies:
```bash
pip install -r backend/requirements.txt
```

3. Run the database migrations (Alembic):
```bash
cd backend
alembic upgrade head
cd ..
```

4. Start the backend development server:
```bash
uvicorn backend.app.main:app --reload --port 8000
```
API Documentation will be available at: `http://localhost:8000/docs`

### Frontend (React + Vite)

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start Vite development server:
```bash
npm run dev
```
Frontend will be accessible at: `http://localhost:5173`

---

## 5. Automated Testing & Verification

Run the full end-to-end test suite:

```bash
# Backend pytest suite (60 tests across 14 modules)
pytest backend/tests -v

# Frontend production typecheck & Vite build
cd frontend && npm run build
```

---

## 6. Comprehensive Documentation Suite

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

---

## 👨‍💻 Author

**Jeevananthan V** — [@JeevananthanV](https://github.com/JeevananthanV)

## License

MIT
