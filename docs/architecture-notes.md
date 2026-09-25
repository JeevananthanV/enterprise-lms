# Architecture & Engineering Notes

## Modular Monolith Design Principles
The Enterprise LMS is structured as a **domain-oriented modular monolith**. All domains share a unified runtime and process boundary during early phases, but retain clean internal boundaries to permit frictionless extraction into dedicated microservices if scale or operational autonomy demands it in the future.

### Domain Boundaries
1. **auth**: Token lifecycle, identity verification, password hashing, and authentication mechanics.
2. **users**: User profile management, tenant associations, and role definitions.
3. **courses**: Course metadata, categories, publish lifecycle, syllabus structure.
4. **modules**: Sectional groupings within a course.
5. **lessons**: Rich learning content units (text, video, interactive elements).
6. **enrollment**: Student registration, seat tracking, and enrollment states.
7. **progress**: Milestone tracking, lesson completion markers, and progress percentages.
8. **assessment**: Quizzes, questions, assignment submissions, grading rubrics.
9. **analytics**: Telemetry aggregation, dropoff metrics, and engagement dashboards.
10. **notifications**: In-app and outbound communication alerts.
11. **audit**: Tamper-evident logging of administrative, enrollment, and grading actions.

### Data Segregation Strategy
- **PostgreSQL**: ACID relational source of truth (users, enrollments, courses, audit logs).
- **MongoDB**: Flexible document store for polymorphic lesson content and dynamic question banks.
- **Redis**: Low-latency caching, rate limiting, and ephemeral token revocation.
