# Enterprise Learning Management System (LMS) — Setup Guide

Welcome to the **Enterprise LMS** full-stack setup guide. This system features a decoupled 3-tier architecture with FastAPI, PostgreSQL 16, MongoDB 7, Redis 7, and React 18 + TypeScript.

- **GitHub Repository**: [https://github.com/JeevananthanV/enterprise-lms](https://github.com/JeevananthanV/enterprise-lms)
- **Author**: Jeevananthan V

---

## 📋 System Prerequisites

- **Python**: 3.11+
- **Node.js**: v18.0.0 or higher (v20+ LTS recommended)
- **PostgreSQL**: 15+ (Relational source of truth)
- **MongoDB**: 6.0+ (Rich content & assessment banks)
- **Redis**: 6.0+ (Caching & rate limits)
- **Docker & Compose**: (Optional containerized setup)

---

## 📥 1. Clone the Repository

```bash
git clone https://github.com/JeevananthanV/enterprise-lms.git
cd enterprise-lms
```

---

## ⚙️ 2. Environment Variables Configuration

Copy `.env.example` to root and `backend/.env`:

```bash
cp .env.example .env
cp .env.example backend/.env
```

Key environment settings:
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/enterprise_lms
MONGODB_URL=mongodb://root:example@localhost:27017
REDIS_URL=redis://localhost:6379/0
JWT_SECRET=enterprise_lms_super_secret_jwt_32_characters_minimum
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
SEED_DEMO_USERS=true
SEED_ADMIN_PASSWORD=AdminPass123!
SEED_INSTRUCTOR_PASSWORD=InstructorPass123!
SEED_STUDENT_PASSWORD=StudentPass123!
```

---

## 📦 3. Backend Setup & Database Migrations

1. Create and activate Python virtual environment:
```bash
python -m venv venv
# Windows:
.\venv\Scripts\Activate.ps1
# Linux/macOS:
source venv/bin/activate
```

2. Install Python dependencies:
```bash
pip install -r backend/requirements.txt
```

3. Run database migrations:
```bash
cd backend
alembic upgrade head
cd ..
```

4. Launch FastAPI development server:
```bash
uvicorn backend.app.main:app --reload --port 8000
```
Interactive Swagger UI will be available at: `http://localhost:8000/docs`

---

## 💻 4. Frontend Setup (React + Vite)

1. Navigate to the frontend directory:
```bash
cd frontend
npm install
npm run dev
```

The frontend application will be live at: `http://localhost:5173`

---

## 🧪 5. Automated Verification Suite

```bash
# Run backend test suite (60 unit and integration tests)
pytest backend/tests -v

# Typecheck and build frontend
cd frontend
npm run build
```

---

## 🛠️ Troubleshooting

- **Redis Connection Error**: Ensure Redis daemon is running locally (`redis-server`) or via Docker (`docker run -p 6379:6379 redis:7`).
- **PostgreSQL Database does not exist**: Create the database using `psql -U postgres -c "CREATE DATABASE enterprise_lms;"`.

