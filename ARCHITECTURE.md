# Enterprise Learning Management System (LMS) - Architecture Specification

## 1. System Overview & Architectural Vision
The Enterprise LMS is a scalable, resilient, high-concurrency learning platform designed to serve three distinct personas:
- **Students (Learners)**: Immersive course consumption, progress tracking, interactive quizzes, resource library, and certification.
- **Instructors (Creators)**: Course builder/authoring suite, rich content & assessment creation, grading center, student performance analytics, and Q&A management.
- **Platform Administrators (Ops/Compliance)**: System health & metrics, tenant/user management, role-based access governance, content moderation, course publishing workflows, and tamper-evident audit trails.

The system is built on a **Decoupled 3-Tier Architecture** emphasizing separation of concerns, high throughput, zero-trust security ("deny by default"), and strict cognitive load minimization for users.

---

## 2. High-Level Architecture Diagram

```
+---------------------------------------------------------------------------------------+
|                                PRESENTATION TIER                                      |
|  React 18+ (Vite) + TypeScript + Tailwind CSS + TanStack Query + React Router v6      |
|                                                                                       |
|  [Student Portal]          [Instructor Studio]             [Admin Control Center]     |
|  - Course Discovery        - Course Curriculum Builder     - System Metrics & Health  |
|  - Immersive Player        - Assessment Designer           - User & Role Management   |
|  - Progress Tracking       - Analytics Dashboard           - Content Moderation       |
|  - Assessments & Quizzes   - Student Review & Grading      - Immutable Audit Log      |
+---------------------------------------------------------------------------------------+
                                           |
                                  HTTPS / REST / JSON
                                  (Reverse Proxy / Nginx)
                                           |
+---------------------------------------------------------------------------------------+
|                              APPLICATION / API TIER                                   |
|                  FastAPI (Python 3.11+) + Pydantic v2 + Uvicorn                       |
|                                                                                       |
|  [Core & Security]     [Curriculum & Learning]    [Assessment & Progress]  [Analytics]|
|  - auth (JWT/OAuth)    - courses                  - assessments (Quizzes)  - telemetry|
|  - users & RBAC        - modules                  - submissions & grading  - analytics|
|  - audit & logging     - lessons                  - progress engine        - reports  |
|  - notifications       - object_storage (S3/MinIO)- certificates           - health   |
+---------------------------------------------------------------------------------------+
            |                               |                              |
            v                               v                              v
+-----------------------+       +-----------------------+       +-----------------------+
|      PostgreSQL       |       |  MongoDB (Optional)   |       |    Redis (Optional)   |
| (Source of Truth)     |       | (Content Document)    |       | (Cache & Ephemeral)   |
|-----------------------|       |-----------------------|       |-----------------------|
| - Users & Credentials |       | - Rich Lesson Bodies  |       | - JWT Token Blacklist |
| - Roles & Permissions |       | - Video Metadata      |       | - Rate Limiting       |
| - Course Metadata     |       | - PDF Attachments     |       | - Catalog/Detail Cache|
| - Enrollments         |       | - Transcripts         |       | - Leaderboards/Stats  |
| - Progress Milestones |       | [Fallback: PostgreSQL |       | [Fallback: Direct DB] |
| - lesson_contents_pg  |       |  lesson_contents_pg]  |       |                       |
| - Audit Trail         |       |                       |       |                       |
+-----------------------+       +-----------------------+       +-----------------------+
                                            |
                                            v
                               +-------------------------+
                               | S3 / MinIO / GCS Bucket |
                               | (Object Storage Store)  |
                               | - Video Streams (HLS)   |
                               | - PDF & Document Attach |
                               | - User Uploads & Media  |
                               +-------------------------+
```

---

## 3. Data Tier Strategy & Multi-Database Segregation

| Database | Responsibility | Storage Strategy |
| :--- | :--- | :--- |
| **PostgreSQL 16+** | Relational source of truth, ACID transactions, relational integrity | User accounts, hashed credentials, roles, course headers, enrollment records, module hierarchy references, milestone completions, payment/cert records, relational audit trail. |
| **MongoDB 7+** | Semi-structured and rich content document store | Detailed lesson contents (Markdown, structured block trees, interactive widgets, code playground configs), quiz question banks, rubrics, granular telemetry payloads. |
| **Redis 7+** | Low-latency in-memory cache & ephemeral store | User sessions, token invalidation denylist, sliding-window rate limit counters, volatile caching for high-traffic course catalogs, real-time analytics aggregation. |
| **Object Storage** (S3/MinIO API) | High-volume binary assets | Video files, PDF notes, certificates, downloadable resources. The database stores strictly signed URLs or storage keys/URIs. |

---

## 4. Domain-Oriented Modular Backend Structure

```
backend/
├── app/
│   ├── core/
│   │   ├── config.py           # Pydantic Settings (.env handling)
│   │   ├── security.py         # Password hashing (Argon2id/Bcrypt), JWT generation/validation
│   │   ├── database.py         # PostgreSQL (SQLAlchemy async engine & sessionmaker)
│   │   ├── mongodb.py          # Motor/PyMongo async client connection manager
│   │   ├── redis.py            # Redis connection pool & helper methods
│   │   ├── logging.py          # Structured JSON logging & correlation IDs
│   │   ├── exceptions.py       # Standardized domain exceptions & error handlers
│   │   └── dependencies.py     # Fast-injected dependencies (get_db, get_current_user, require_role)
│   ├── models/                 # SQLAlchemy ORM relational models
│   │   ├── user.py
│   │   ├── course.py
│   │   ├── module.py
│   │   ├── lesson.py
│   │   ├── enrollment.py
│   │   ├── progress.py
│   │   ├── quiz.py
│   │   ├── assignment.py
│   │   ├── certificate.py
│   │   └── audit.py
│   ├── schemas/                # Pydantic request/response validation schemas
│   │   ├── user.py
│   │   ├── auth.py
│   │   ├── course.py
│   │   ├── lesson.py
│   │   ├── content.py              # MongoDB Lesson Content schemas
│   │   ├── assessment.py
│   │   └── analytics.py
│   ├── repositories/           # Data access layer
│   │   ├── user_repository.py
│   │   ├── course_repository.py
│   │   ├── lesson_repository.py
│   │   ├── content_repository.py   # MongoDB Collection access
│   │   ├── enrollment_repository.py
│   │   ├── progress_repository.py
│   │   ├── assessment_repository.py
│   │   └── certificate_repository.py
│   ├── api/
│   │   └── v1/
│   │       ├── router.py
│   │       ├── endpoints/
│   │       │   ├── auth.py
│   │       │   ├── users.py
│   │       │   ├── courses.py
│   │       │   ├── modules.py
│   │       │   ├── lessons.py
│   │       │   ├── content.py          # Flexible MongoDB content endpoints
│   │       │   ├── enrollments.py
│   │       │   ├── progress.py
│   │       │   ├── assessment.py
│   │       │   ├── assignments.py
│   │       │   ├── certificates.py
│   │       │   ├── instructor_assessment.py
│   │       │   ├── analytics.py
│   │       │   ├── notifications.py
│   │       │   └── audit.py
│   ├── services/               # Encapsulated Business Logic Layer
│   │   ├── auth_service.py
│   │   ├── course_service.py
│   │   ├── curriculum_service.py
│   │   ├── content_service.py      # Multi-DB Content Orchestration
│   │   ├── cache_service.py        # Redis Caching & Invalidation Engine
│   │   ├── enrollment_service.py
│   │   ├── progress_service.py
│   │   ├── quiz_service.py
│   │   ├── assignment_service.py
│   │   ├── course_completion_service.py
│   │   ├── certificate_service.py
│   │   ├── storage_service.py
│   │   └── audit_service.py
│   └── main.py                 # FastAPI application factory & middleware stack

├── tests/
│   ├── conftest.py
│   ├── unit/
│   └── integration/
├── alembic/                    # DB Migrations
├── requirements.txt
└── Dockerfile
```

---

## 5. Security & Governance Architecture

1. **Deny by Default Authorization**: Every protected route enforces explicit role and permission validation through FastAPI dependencies (`require_role(["admin", "instructor"])`).
2. **Resource Ownership Checks**: Instructors can only edit their owned courses and modules; students can only inspect and submit for courses they are enrolled in.
3. **JWT Authentication & Token Lifecycle**:
   - Short-lived Access Tokens (e.g. 15-30 mins).
   - Refresh tokens with revocation lists held in Redis.
4. **Input Sanitization & Output Encoding**: Strict Pydantic models validate all incoming payloads to eliminate injection vectors.
5. **Rate Limiting**: Redis token-bucket middleware defending against brute-force attacks on sensitive endpoints (`/auth/login`, `/auth/register`).
6. **Immutable Audit Logging**: Every administrative action, enrollment change, grade alteration, and permission elevation writes a structured event to the audit log.
7. **Zero-Secret Codebase**: Mandatory reliance on `.env` and environment variables with strict schema validation on application boot.

---

## 6. Frontend Presentation Architecture

```
frontend/
├── src/
│   ├── assets/                 # SVGs, icons, base styles
│   ├── components/
│   │   ├── common/             # Buttons, Inputs, Modals, Toasts, Badges, Loaders, EmptyStates
│   │   ├── layout/             # Sidebar, Header, Breadcrumbs, AppShell, RoleGuard
│   │   ├── course/             # CourseCard, CourseGrid, CoursePlayer, LessonView
│   │   ├── dashboard/          # StatCards, ProgressCharts, RecentActivity
│   │   └── assessment/         # QuizRunner, QuestionBlock, SubmissionResult
│   ├── context/ / hooks/       # AuthContext, ThemeContext, useAuth, useDebounce
│   ├── lib/                    # Axios instance with interceptors, QueryClient
│   ├── pages/
│   │   ├── auth/               # Login, Register, ForgotPassword
│   │   ├── student/            # StudentDashboard, MyCourses, CoursePlayer, Catalog
│   │   ├── instructor/         # InstructorDashboard, CourseBuilder, Gradebook, Analytics
│   │   └── admin/              # AdminDashboard, UserManagement, CourseModeration, AuditLogs
│   ├── routes/                 # AppRoutes with role-based Route Guards
│   ├── services/               # Typed API client services
│   ├── types/                  # TypeScript interfaces matching backend schemas
│   ├── App.tsx
│   └── main.tsx
├── tailwind.config.js
├── vite.config.ts
└── package.json
```

---

## 7. UX & Cognitive Load Minimization Strategy
- **Context Clarity**: Dedicated breadcrumb and sticky step indicators ensuring users always know **Where they are**.
- **Action Clarity**: Primary actions (e.g., "Resume Course", "Publish Module", "Submit Quiz") are highlighted with high visual hierarchy, ensuring users know **What they can do**.
- **Next Step Guidance**: Contextual hints, next-lesson auto-cueing, and workflow checklists show users **What they should do next**.
- **Resilient States**: Every dynamic view provides deterministic Loading Skeletons, Informative Empty States (with action triggers), and Clear Error Recovery prompts.
