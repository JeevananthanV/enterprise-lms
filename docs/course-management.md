# Phase 4: Course Management, Modules & Curriculum Studio

## Overview
Phase 4 implements the core course-authoring, curriculum-structuring, and public course-discovery capabilities for the Enterprise LMS. It supports three primary user personas:
1. **Instructors**: Course creation, metadata editing, curriculum module/lesson authoring and sequential reordering, publishing prerequisite validation, and course preview mode.
2. **Students / Public Learners**: Course catalog browsing, full-text search, category/level filtering, pagination, and course details/syllabus inspection.
3. **Platform Administrators**: Complete moderation and oversight across all courses and curricula.

---

## 1. Architecture & Data Model

### Relational Entities (PostgreSQL via SQLAlchemy Async)
* **`courses`**:
  * `id`: UUID primary key
  * `instructor_id`: Foreign key referencing `users.id` (Indexed)
  * `title`, `slug` (Unique, Indexed), `short_description`, `description`, `category` (Indexed), `level`, `status`, `estimated_duration_minutes`, `is_free`, `price`, `thumbnail_url`
  * `created_at`, `updated_at`, `published_at`
* **`course_modules`**:
  * `id`: UUID primary key
  * `course_id`: Foreign key referencing `courses.id` (CASCADE delete)
  * `title`, `slug`, `description`, `order_index`, `is_published`
  * Composite Unique Constraint: `(course_id, order_index)`
* **`lessons`**:
  * `id`: UUID primary key
  * `module_id`: Foreign key referencing `course_modules.id` (CASCADE delete)
  * `title`, `slug`, `content_type` (`VIDEO`, `TEXT`, `DOCUMENT`, `QUIZ`, `IFRAME`), `order_index`, `duration_minutes`, `is_preview`, `is_published`
  * Composite Unique Constraint: `(module_id, order_index)`

---

## 2. Server-Side Ownership & Security Enforcement

All instructor course-authoring endpoints strictly enforce resource ownership on the backend:
* **`require_resource_owner_or_admin(resource_owner_id, current_user)`**: Ensures Instructor A cannot read, edit, delete, reorder, or publish courses or modules belonging to Instructor B.
* **Role Verification**: Students attempting to invoke `/api/v1/instructor/*` endpoints receive `403 Forbidden`.
* **Platform Admin Authority**: `PLATFORM_ADMIN` users can inspect and moderate courses across all instructors.
* **Public Visibility Isolation**: Unauthenticated and student catalog endpoints (`/api/v1/courses`) only return courses with `status = PUBLISHED`. Draft, unpublished, and archived courses are strictly hidden.

---

## 3. Publishing Checklist & Prerequisite Rules

Before a course can transition from `DRAFT` / `UNPUBLISHED` to `PUBLISHED`, the backend `CourseService.get_publish_checklist` evaluates the following prerequisites:
1. **Valid Title**: Must be at least 3 characters long.
2. **Valid Description**: Must be at least 10 characters long.
3. **Module Requirement**: Must contain at least 1 module.
4. **Lesson Requirement**: Must contain at least 1 lesson.

If any check fails, `POST /api/v1/instructor/courses/{id}/publish` rejects the transition with `400 Bad Request` listing all failing criteria.

---

## 4. API Endpoints

### Public & Student Catalog (`/api/v1/courses`)
* `GET /api/v1/courses`: Search, filter by category/level, paginated catalog of published courses.
* `GET /api/v1/courses/{id}`: Detailed course syllabus and instructor profile.
* `GET /api/v1/courses/{id}/curriculum`: Module and lesson breakdown of published content.
* `GET /api/v1/courses/status`: Domain health check.

### Instructor Course & Curriculum Studio (`/api/v1/instructor`)
* `GET /api/v1/instructor/courses`: List authored courses for current instructor (or all courses if admin).
* `POST /api/v1/instructor/courses`: Create new course draft.
* `GET /api/v1/instructor/courses/{id}`: Get authored course details.
* `PUT /api/v1/instructor/courses/{id}`: Update course metadata.
* `DELETE /api/v1/instructor/courses/{id}`: Delete course and cascade modules/lessons.
* `GET /api/v1/instructor/courses/{id}/checklist`: Get live publish readiness checklist.
* `POST /api/v1/instructor/courses/{id}/publish`: Publish course.
* `POST /api/v1/instructor/courses/{id}/unpublish`: Move course back to unpublished/draft.
* `GET /api/v1/instructor/courses/{id}/preview`: Student-perspective preview of draft course.
* `POST /api/v1/instructor/courses/{course_id}/modules`: Create module.
* `PUT /api/v1/instructor/modules/{module_id}`: Update module.
* `DELETE /api/v1/instructor/modules/{module_id}`: Delete module.
* `POST /api/v1/instructor/courses/{course_id}/modules/reorder`: Reorder modules.
* `POST /api/v1/instructor/modules/{module_id}/lessons`: Create lesson.
* `PUT /api/v1/instructor/lessons/{lesson_id}`: Update lesson.
* `DELETE /api/v1/instructor/lessons/{lesson_id}`: Delete lesson.
* `POST /api/v1/instructor/modules/{module_id}/lessons/reorder`: Reorder lessons.

---

## 5. Frontend User Interface

* **`CourseCatalogPage` (`/courses`)**: Search bar, category filter pills, difficulty filter, course cards with metrics, pagination.
* **`CourseDetailsPage` (`/courses/:id`)**: Hero header banner, instructor card, course description, collapsible module accordions with preview tags.
* **`InstructorCoursesPage` (`/instructor/courses`)**: Table with status badges, quick actions (Studio, Edit, Preview, Publish/Unpublish, Delete), and status filtering.
* **`CourseCreatePage` (`/instructor/courses/new`)**: Course drafting form with validation.
* **`CourseEditPage` (`/instructor/courses/:id/edit`)**: Course metadata and settings editor.
* **`CurriculumStudioPage` (`/instructor/courses/:id/curriculum`)**: Interactive studio workspace for adding modules/lessons, reordering with Move Up / Move Down buttons, and viewing the live Publishing Checklist.
* **`CoursePreviewPage` (`/instructor/courses/:id/preview`)**: Learner-view simulation for draft courses with simulated lesson content player.
