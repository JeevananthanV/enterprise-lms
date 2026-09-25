# Redis Caching & Performance Architecture (Phase 8)

## 1. Overview

The Enterprise LMS uses **Redis** as a distributed, in-memory caching and transient storage layer to dramatically increase read throughput, reduce database connection saturation, and deliver sub-millisecond response times for public course discovery, curriculum syllabi, and administrative analytics summaries.

### Architectural Invariants:
1. **PostgreSQL & MongoDB Remain Sources of Truth**: Redis is strictly a non-authoritative caching layer. All authoritative writes, transactions, and state changes persist directly to PostgreSQL and MongoDB.
2. **Non-Authoritative Graceful Fallback**: If Redis becomes offline, unreachable, or returns connection errors, the application logs a warning and falls back transparently to the relational/document databases without raising 500 errors to users.
3. **Strict Privacy & Isolation**: Shared cache keys cache ONLY public or aggregated data (such as published course details and platform summaries). Private student enrollments, quiz submissions, and instructor drafts are NEVER stored in shared keys.
4. **Automated Write-Through Invalidation**: Any mutation across courses, curriculum modules, lessons, or rich content documents immediately purges affected Redis cache keys.

---

## 2. Reusable Cache Service (`app.services.cache_service`)

The `CacheService` class provides a unified interface for caching operations:

- `get_cached(key: str) -> Optional[Any]`: Retrieves and deserializes cached payloads using `CustomJSONEncoder` compatible rules. Returns `None` on cache miss, when caching is disabled (`CACHE_ENABLED=False`), or when Redis is offline.
- `set_cached(key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool`: Serializes and stores data with an expiration TTL.
- `delete_cached(key: str) -> bool`: Purges an individual cache key.
- `delete_pattern(pattern: str) -> int`: Wildcard key matching and batch invalidation (e.g. `courses:catalog:*`).
- `invalidate_course_cache(course_id: str) -> None`: High-level invalidation orchestrator that purges course details, curriculum, catalog permutations, and platform analytics simultaneously.

---

## 3. Cache Key Strategy & Namespaces

| Cache Key Pattern | Scope | Target Data | Invalidation Event |
| :--- | :--- | :--- | :--- |
| `courses:catalog:s={search}&c={category}&l={level}&p={page}&ps={pageSize}` | Public | Filtered and paginated published course list | Course creation, update, publish/unpublish, deletion |
| `course:details:{course_id}` | Public | Public course metadata, instructor info, price | Course update, deletion, publish/unpublish |
| `course:curriculum:{course_id}` | Public/Student | Published modules, lessons hierarchy, free preview flags | Module create/update/reorder/delete, Lesson create/update/reorder/delete |
| `analytics:summary:{scope}` | Admin | High-level platform counts and completion rates | Course lifecycle changes, periodic TTL refresh |

---

## 4. TTL Strategy & Environment Configuration

Cache Time-To-Live (TTL) is fully configurable through environment variables:

| Environment Variable | Default (Seconds) | Rationale |
| :--- | :--- | :--- |
| `CACHE_ENABLED` | `true` | Master feature flag for toggling caching |
| `CACHE_DEFAULT_TTL_SECONDS` | `300` (5 mins) | Default TTL for generic cached items |
| `CACHE_COURSE_CATALOG_TTL_SECONDS` | `300` (5 mins) | Balances high discovery throughput with freshness |
| `CACHE_COURSE_DETAILS_TTL_SECONDS` | `600` (10 mins) | Course descriptions and syllabi change infrequently |
| `CACHE_ANALYTICS_TTL_SECONDS` | `120` (2 mins) | Analytics summaries computed frequently with short caching window |

---

## 5. Cache Invalidation Triggers

Invalidation hooks are integrated into the following core services:

1. **Course Service (`app.services.course_service`)**:
   - `update_course()` -> triggers `invalidate_course_cache(course_id)`
   - `delete_course()` -> triggers `invalidate_course_cache(course_id)`
   - `publish_course()` / `unpublish_course()` -> triggers `invalidate_course_cache(course_id)`
2. **Curriculum Service (`app.services.curriculum_service`)**:
   - `create_module()`, `update_module()`, `delete_module()`, `reorder_modules()` -> triggers `invalidate_course_cache(course_id)`
   - `create_lesson()`, `update_lesson()`, `delete_lesson()`, `reorder_lessons()` -> triggers `invalidate_course_cache(course_id)`
3. **Content Service (`app.services.content_service`)**:
   - `create_or_update_content()`, `publish_content()`, `unpublish_content()` -> triggers `invalidate_course_cache(course_id)`

---

## 6. Verification and Testing

The Redis caching layer is verified through `backend/tests/test_redis_caching.py` covering:
- Cache hit / miss lifecycle
- Pattern-based invalidation
- Serialization with UUIDs, Decimals, datetimes
- Graceful offline and error recovery
- Role-based authorization on cached analytics endpoints
- Full integration with catalog, details, and curriculum endpoints
