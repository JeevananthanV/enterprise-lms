# Flexible Content Management Architecture (Phase 7)

## Overview

The Enterprise LMS implements a **polyglot persistence architecture** separating high-integrity transactional relationships (PostgreSQL) from polymorphic, high-volume, and evolving learning content (MongoDB).

```
+------------------------------------+          +--------------------------------------+
|            PostgreSQL              |          |               MongoDB                |
|       (Transactional Core)         |          |       (Flexible Content Store)       |
+------------------------------------+          +--------------------------------------+
| - users & roles                    |          | Collection: lesson_contents          |
| - courses, modules, lessons        |          | - _id (Document ID)                  |
| - enrollments & progress tracking  | <------> | - lesson_id (PostgreSQL Lesson ID)   |
| - quizzes, attempts, assignments   |          | - course_id (PostgreSQL Course ID)   |
| - certificates & audit logs        |          | - content_type (TEXT/VIDEO/PDF/...)  |
| - lesson.content_ref ---------------+          | - body (Rich text / Markdown)        |
+------------------------------------+          | - video_metadata (Object storage ref)|
                                                | - pdf_metadata (Object storage ref)  |
                                                | - transcript (VTT/SRT text)          |
                                                | - external_resources (Array)         |
                                                | - version (Integer revision number)  |
                                                | - is_published (Boolean)             |
                                                +--------------------------------------+
```

---

## 1. Database Responsibilities & Segregation

### PostgreSQL (Source of Truth & Flexible Fallback Engine)
- **Entities**: Users, authentication credentials, course catalogs, syllabus structure (modules, lessons), enrollments, lesson progress, quiz attempts, assignments, and certificates.
- **Foreign Key Linkage**: The `lessons` table includes an indexed `content_ref VARCHAR(64)` column pointing to the corresponding content document/record ID.
- **PostgreSQL Fallback Table (`lesson_contents_pg`)**: When running in environments where MongoDB is disabled (`MONGODB_ENABLED=false`) or offline, PostgreSQL automatically stores rich lesson content using structured JSON columns (`video_metadata`, `pdf_metadata`, `transcript`, `external_resources`, `custom_properties`).
- **Guarantees**: ACID transactions, foreign key constraints, module/lesson ordering uniqueness, cascade deletion rules.

### MongoDB (Flexible Content Store - Optional for Local Dev)
- **Collection**: `lesson_contents`
- **Indexing**:
  - `{"lesson_id": 1}` (Unique index)
  - `{"course_id": 1}` (Compound lookups)
  - `{"is_published": 1}` (Publication queries)
  - `{"content_type": 1}` (Format filtering)
- **Polymorphism**: Can seamlessly store text articles, rich formatting, video player configurations, PDF attachments, synchronized transcripts, and external reading lists without altering relational schemas.
- **Automatic Degradation**: If MongoDB is unavailable or disabled, the application transparently delegates to PostgreSQL without breaking any REST API contracts or frontend Course Player experiences.

---

## 2. Media Strategy & Object Storage References

> **Zero Large Binary Blobs in Database**:
> Neither PostgreSQL nor MongoDB stores raw media binaries (MP4 files, large PDFs). Instead, MongoDB documents store validated object-storage URI references (`s3://`, `gcs://`, `https://cdn...`), playback metadata, duration, file sizes, and signed URL endpoints.

### Sub-Schema Definitions

#### Video Metadata
```json
{
  "video_url": "s3://enterprise-lms-media/courses/mod1/lesson1.mp4",
  "duration_seconds": 940,
  "resolution": "1080p",
  "provider": "s3",
  "captions_url": "s3://enterprise-lms-media/courses/mod1/lesson1.vtt",
  "thumbnail_url": "https://cdn.example.com/thumbnails/lesson1.jpg"
}
```

#### PDF Metadata
```json
{
  "file_url": "s3://enterprise-lms-media/docs/cheat-sheet.pdf",
  "file_name": "MongoDB-CheatSheet.pdf",
  "file_size_bytes": 1048576,
  "page_count": 4,
  "downloadable": true
}
```

#### Transcript Data
```json
{
  "language": "en",
  "content": "00:00:00 Welcome to the lesson on MongoDB content storage...",
  "format": "vtt"
}
```

#### External Resources
```json
[
  {
    "title": "MongoDB Schema Design Documentation",
    "url": "https://www.mongodb.com/docs/manual/data-modeling/",
    "resource_type": "documentation",
    "description": "Official design patterns and antipatterns"
  }
]
```

---

## 3. Versioning & Publication Lifecycle

1. **Creation**:
   - Newly created lesson content starts at `version: 1` and `is_published: false`.
2. **Draft Modifications**:
   - Calling `PUT /api/v1/lessons/{lesson_id}/content` applies partial updates, automatically increments `version` (`$inc: {version: 1}`), and updates `updated_at`.
3. **Publication Control**:
   - `POST /api/v1/lessons/{lesson_id}/content/publish` sets `is_published: true` and sets `published_at` to the current UTC timestamp.
   - `POST /api/v1/lessons/{lesson_id}/content/unpublish` sets `is_published: false` and clears `published_at`.

---

## 4. Security & RBAC Matrix

| Role / Context | Create (`POST`) | Read (`GET`) | Update (`PUT`) | Publish / Unpublish |
| :--- | :--- | :--- | :--- | :--- |
| **Platform Admin** | Allowed for any lesson | Allowed for any lesson | Allowed for any lesson | Allowed for any lesson |
| **Instructor (Course Owner)** | Allowed for own courses | Allowed for own courses (even unpublished) | Allowed for own courses | Allowed for own courses |
| **Instructor (Non-Owner)** | Forbidden (403) | Forbidden (403) | Forbidden (403) | Forbidden (403) |
| **Student (Enrolled)** | Forbidden (403) | Allowed if `is_published: true` | Forbidden (403) | Forbidden (403) |
| **Student (Unenrolled)** | Forbidden (403) | Allowed ONLY if `is_free_preview: true` and `is_published: true` | Forbidden (403) | Forbidden (403) |
| **Unauthenticated** | Rejected (401) | Rejected (401) | Rejected (401) | Rejected (401) |

---

## 5. REST API Reference

### Create Content
```http
POST /api/v1/lessons/{lesson_id}/content
Authorization: Bearer <INSTRUCTOR_OR_ADMIN_JWT>
Content-Type: application/json

{
  "content_type": "VIDEO",
  "body": "Markdown guide...",
  "video_metadata": {
    "video_url": "s3://media/lesson.mp4",
    "duration_seconds": 600,
    "resolution": "1080p",
    "provider": "s3"
  },
  "transcript": {
    "language": "en",
    "content": "Transcript text...",
    "format": "vtt"
  }
}
```

### Get Lesson Content
```http
GET /api/v1/lessons/{lesson_id}/content
Authorization: Bearer <JWT>
```

### Update Lesson Content
```http
PUT /api/v1/lessons/{lesson_id}/content
Authorization: Bearer <INSTRUCTOR_OR_ADMIN_JWT>
Content-Type: application/json

{
  "body": "Updated body text",
  "pdf_metadata": {
    "file_url": "s3://media/guide.pdf",
    "file_name": "guide.pdf",
    "downloadable": true
  }
}
```

### Publish Content
```http
POST /api/v1/lessons/{lesson_id}/content/publish
Authorization: Bearer <INSTRUCTOR_OR_ADMIN_JWT>
```

### Unpublish Content
```http
POST /api/v1/lessons/{lesson_id}/content/unpublish
Authorization: Bearer <INSTRUCTOR_OR_ADMIN_JWT>
```
