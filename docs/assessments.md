# Phase 6: Advanced Assessments, Auto-Grading & Certification Engine Documentation

## 1. Overview

Phase 6 implements a comprehensive enterprise evaluation, grading, and verifiable credentials engine within the Learning Management System (LMS). It enables instructors to publish practical assignments and timed randomized quizzes, empowers students with server-authoritative assessments, automatically calculates multi-criteria course completion, and issues cryptographically signed certificates with public verification portals.

---

## 2. Core Capabilities

### 2.1 Assignment Submissions & File Handling
* **Models**: `Assignment`, `AssignmentSubmission`, `SubmissionStatus` (`DRAFT`, `SUBMITTED`, `RESUBMITTED`, `GRADED`, `RETURNED`).
* **Storage Abstraction**: Dedicated `StorageService` saving student submissions securely under `storage/submissions` with MIME type and size enforcement.
* **Student Workflow**: Submit textual answers or upload files (PDF, ZIP, DOCX, TXT), receive status updates, and view instructor remarks and scores.
* **Instructor Workflow**: Instructors view and evaluate submissions for their own courses only.

### 2.2 Advanced & Timed Quizzes
* **Randomization**: Server-side shuffle of question sequences and answer choices on attempt creation when `randomize_questions=True`.
* **Zero-Trust Client Scoring**: Correct answers are stripped from question payloads delivered to the client during active quiz runs.
* **Server-Authoritative Timer**: `expires_at` is generated and enforced on the server. If an attempt is submitted after expiration (+ 15s network latency buffer), it is marked `EXPIRED` with strict scoring.
* **Attempt Limits**: `max_attempts` validation ensures student attempts cannot exceed policy limits.

### 2.3 Course Completion Engine
* **Evaluation Criteria**: Multi-dimensional verification ensuring:
  1. 100% of published lessons in all course modules are marked completed.
  2. 100% of required quizzes have at least one passing attempt (`score >= passing_score`).
  3. 100% of course assignments have been graded by an instructor.
* **Enrollment Progress**: Auto-syncs enrollment completion percentage and updates status to `COMPLETED`.

### 2.4 Cryptographic Certification Engine
* **Certificate Serial**: Generates human-readable, unique IDs formatted as `CERT-2026-XXXXXXXX`.
* **Cryptographic Hash**: Creates SHA-256 digital fingerprint based on student ID, course ID, certificate number, and system salt.
* **Public Verification**: Zero-auth public verification endpoint (`GET /api/v1/certificates/verify/{cert_number}`) and UI (`/verify/certificate/:cert_number`) allowing prospective employers or academic institutions to verify credential validity.

---

## 3. Database Schema

### `assignments`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | VARCHAR(36) | PRIMARY KEY | UUID primary key |
| `course_id` | VARCHAR(36) | FK -> courses.id | Owning course (indexed) |
| `module_id` | VARCHAR(36) | FK -> course_modules.id (Nullable) | Associated module |
| `lesson_id` | VARCHAR(36) | FK -> lessons.id (Nullable) | Associated lesson |
| `title` | VARCHAR(255) | NOT NULL | Assignment title |
| `description` | TEXT | NULLABLE | Brief description |
| `instructions` | TEXT | NULLABLE | Detailed rubric / instructions |
| `max_marks` | INTEGER | NOT NULL (Default: 100) | Maximum achievable points |
| `due_date` | TIMESTAMP | NULLABLE | Optional due date |
| `allowed_file_types` | VARCHAR(255) | NULLABLE | Comma-separated allowed extensions |
| `max_file_size_mb` | INTEGER | NOT NULL (Default: 10) | File size ceiling |
| `created_by` | INTEGER | FK -> users.id | Author instructor |
| `created_at` / `updated_at` | TIMESTAMP | NOT NULL | Timestamps |

### `assignment_submissions`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | VARCHAR(36) | PRIMARY KEY | UUID primary key |
| `assignment_id` | VARCHAR(36) | FK -> assignments.id | Target assignment (indexed) |
| `student_id` | INTEGER | FK -> users.id | Submitting student (indexed) |
| `file_url` | VARCHAR(500) | NULLABLE | Storage reference / URL |
| `file_name` | VARCHAR(255) | NULLABLE | Original uploaded file name |
| `file_size_bytes` | BIGINT | NULLABLE | File size in bytes |
| `submission_text`| TEXT | NULLABLE | Textual submission answer |
| `score` | FLOAT | NULLABLE | Awarded score |
| `feedback` | TEXT | NULLABLE | Instructor feedback remarks |
| `graded_by` | INTEGER | FK -> users.id (Nullable) | Grading instructor |
| `status` | ENUM | NOT NULL | DRAFT, SUBMITTED, RESUBMITTED, GRADED, RETURNED |
| `submitted_at` | TIMESTAMP | NULLABLE | Submission timestamp |
| `graded_at` | TIMESTAMP | NULLABLE | Grading timestamp |

### `certificates`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | VARCHAR(36) | PRIMARY KEY | UUID primary key |
| `certificate_number` | VARCHAR(64) | UNIQUE, NOT NULL | Unique public serial (CERT-2026-XXXX) |
| `enrollment_id` | VARCHAR(36) | FK -> enrollments.id, UNIQUE | Associated enrollment record |
| `student_id` | INTEGER | FK -> users.id | Student recipient (indexed) |
| `course_id` | VARCHAR(36) | FK -> courses.id | Certified course (indexed) |
| `issued_at` | TIMESTAMP | NOT NULL | Issue timestamp |
| `completion_date` | TIMESTAMP | NOT NULL | Course completion date |
| `verification_hash` | VARCHAR(128) | NOT NULL | SHA-256 cryptographic verification token |
| `pdf_url` | VARCHAR(500) | NULLABLE | Downloadable PDF URL |

---

## 4. API Endpoints

### Student Assignment & Quiz Endpoints
* `GET /api/v1/courses/{course_id}/assignments` – List assignments for enrolled course.
* `GET /api/v1/assignments/{assignment_id}` – Get assignment details.
* `POST /api/v1/assignments/{assignment_id}/submissions` – Submit text / file payload.
* `GET /api/v1/assignments/{assignment_id}/my-submission` – View current submission & grade.
* `POST /api/v1/quizzes/{quiz_id}/attempts/start` – Start timed, randomized quiz attempt.
* `GET /api/v1/quizzes/{quiz_id}/attempts/{attempt_id}` – View active attempt and sanitized question order.
* `POST /api/v1/quizzes/{quiz_id}/attempts/{attempt_id}/submit` – Submit answers for server-side evaluation.

### Instructor Grading & Assessment Endpoints
* `POST /api/v1/instructor/courses/{course_id}/assignments` – Create new assignment.
* `GET /api/v1/instructor/courses/{course_id}/assignments` – List course assignments.
* `GET /api/v1/instructor/assignments/{assignment_id}/submissions` – List all student submissions.
* `GET /api/v1/instructor/submissions/{submission_id}` – Inspect single student submission.
* `POST /api/v1/instructor/submissions/{submission_id}/grade` – Record score and feedback.

### Course Completion & Certification Endpoints
* `GET /api/v1/courses/{course_id}/completion` – Authoritative multi-criteria completion report.
* `GET /api/v1/courses/{course_id}/certificate` – Get or issue verified certificate upon 100% completion.
* `GET /api/v1/certificates/{certificate_id}` – Get certificate details by ID.
* `GET /api/v1/certificates/verify/{certificate_number}` – Public zero-auth certificate verification.

---

## 5. Security & Multi-Tenant Isolation
1. **Course Ownership Enforcement**: Instructors can only view submissions, grade assignments, or modify assessment criteria for courses they own (`instructor_id == current_user.id`). Platform Admins retain global supervisory access.
2. **Student Enrollment Guard**: Students can only access assignments, submit attempts, or view grades for courses in which they hold active enrollments.
3. **Immutability of Finalized Attempts**: Submitted quiz attempts cannot be overwritten or re-submitted.
