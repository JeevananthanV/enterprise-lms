# Enterprise LMS — UI/UX Design System & Frontend Architecture (Phase 9)

## 1. Overview & Design Principles

The Enterprise LMS user interface is engineered as a responsive, high-performance, and accessible Single Page Application (SPA) built with React 18, TypeScript, Tailwind CSS, TanStack Query, and React Router v6.

### Core Design Tenets
1. **Role-Driven Ergonomics**: Tailored interfaces for `STUDENT`, `INSTRUCTOR`, and `PLATFORM_ADMIN` workflows with dedicated dashboards and contextual navigation.
2. **Predictable UX States**: Instant feedback using optimistic updates, skeleton loaders, subtle empty states, clear error recovery boundaries, and a non-blocking toast notification system.
3. **Multi-Tier Transparency**: Header and administrative diagnostics expose live health telemetry across PostgreSQL, MongoDB, and Redis caching.
4. **WCAG 2.1 AA Accessibility**: Semantic HTML landmark regions (`<nav>`, `<header>`, `<main>`, `<aside>`), high-contrast slate-on-white text tokens, full keyboard navigation (including `Escape` dismiss on dialogs), and ARIA-compliant status announcements (`aria-live="polite"`).

---

## 2. Layout & Global Navigation Hierarchy

```
+-----------------------------------------------------------------------------------+
| Top Navigation Header (Brand, Multi-Tenant Status, Global Search, User Pill/Role) |
+-----------------------------------------------------------------------------------+
|  Sidebar Navigation (Desktop)  |  Main Content Workspace                          |
|  - Role-Scoped Sections        |  - Dynamic Route Breadcrumb Trail                |
|  - Active Route Highlighting   |  - Page Header & Action Controls                 |
|  - Collapse / Expand Drawer    |  - Primary Data Grids & Responsive Cards         |
|  - Mobile Overlay Drawer       |  - Modal Overlays & Global Toast Portal          |
+-----------------------------------------------------------------------------------+
```

### Key Layout Components
- **`AppShell.tsx`**: Root layout managing collapsible sidebar state, sticky header, responsive container boundaries, and breadcrumbs injection.
- **`Header.tsx`**: Sticky top bar with quick catalog search, multi-tier system status pill, notifications drawer popover, and authenticated user dropdown.
- **`Sidebar.tsx`**: Navigation with distinct sections for Student Learning, Instructor Authoring, and Platform Governance.
- **`Breadcrumbs.tsx`**: Automatic URL-path deduction with human-readable route token formatting and UUID truncation.

---

## 3. Reusable Component & UX Primitive Library

| Component | Location | Description |
| :--- | :--- | :--- |
| **`ToastProvider` / `useToast`** | `src/context/ToastContext.tsx` | Global toast notification queue supporting `showSuccess`, `showError`, `showWarning`, `showInfo` with auto-dismiss and portal rendering. |
| **`Modal`** | `src/components/common/Modal.tsx` | Accessible dialog with backdrop blur, scroll locking, ESC key dismissal, and custom max-width constraints. |
| **`ConfirmDialog`** | `src/components/common/ConfirmDialog.tsx` | Specialized modal for destructive confirmation (e.g. user deactivation, cache purge). |
| **`Tabs`** | `src/components/common/Tabs.tsx` | Segmented tab switcher with active indicators and optional numerical item counts. |
| **`Card`** | `src/components/common/Card.tsx` | Consistent container with standardized borders, subtle drop-shadows, and headers. |
| **`Badge`** | `src/components/common/Badge.tsx` | Status indicators for roles, publication states, submission scores, and cache hits. |
| **`Button`** | `src/components/common/Button.tsx` | Buttons with variants (`primary`, `secondary`, `outline`, `danger`), sizes, and loading spinners. |
| **`LoadingState` / `EmptyState` / `ErrorState`** | `src/components/common/*` | Standardized visual representations for asynchronous query states. |

---

## 4. Role-Specific User Journeys

### 1. Student Journey
- **Dashboard (`/student/dashboard`)**: Enrolled course progress metrics, continue learning shortcuts, recently completed milestones.
- **Course Catalog (`/courses`)**: Search by keyword, category filter, difficulty level filtering, and responsive course cards.
- **Course Details (`/courses/:id`)**: Instructor metadata, detailed module/lesson syllabus, free lesson previews, enrollment CTA.
- **Course Player (`/student/courses/:id/learn`)**: Multi-format content player (PostgreSQL metadata + MongoDB rich documents), sidebar curriculum checklist, lesson completion toggle.
- **Timed Quiz Runner (`/student/courses/:id/quizzes/:quizId`)**: Real-time countdown timer, question pagination, answer submission, instant score calculation.
- **Assignment Submissions (`/student/courses/:id/assignments/:id`)**: Solution submission with rich notes, file URL attachments, instructor grade feedback.
- **Certificates (`/student/certificates/:id`)**: Printable certificate card, unique verification badge, public verification route (`/verify/certificate/:number`).

### 2. Instructor Journey
- **Dashboard (`/instructor/dashboard`)**: Total student reach, course creation shortcuts, active authoring draft status.
- **Course Management (`/instructor/courses`)**: Tabbed views of draft, published, and archived courses, one-click curriculum editor launcher.
- **Course Studio & Editor (`/instructor/courses/:id/edit`)**: Course metadata configuration, publish readiness checklist validation.
- **Curriculum Studio (`/instructor/courses/:id/curriculum`)**: Drag/reorder modules & lessons, manage flexible lesson contents with MongoDB modal editor.
- **Grading Center (`/instructor/courses/:id/assignments`)**: Review student assignment submissions, assign scores (0-100), submit constructive feedback.

### 3. Platform Admin Journey
- **Governance Dashboard (`/admin/dashboard`)**: Platform-wide metrics (users, courses, enrollments, certificates), quick sub-module shortcuts.
- **User Governance (`/admin/users`)**: Searchable user directory with role filters, immediate RBAC role reassignment modal, status activation toggles.
- **Course Moderation (`/admin/courses`)**: Platform-wide catalog inspection and quality control.
- **Security Audit Logs (`/admin/audit`)**: Tamper-evident audit trail capturing logins, role elevations, course publications, and cache invalidations.
- **System Diagnostics (`/admin/diagnostics`)**: Real-time status cards for PostgreSQL, MongoDB, and Redis caching with manual cache purge trigger.

---

## 5. Responsive Design Breakpoints

- **Mobile (`< 768px`)**: Drawer overlay navigation, full-width cards, streamlined header with search drawer, sticky bottom actions in Course Player.
- **Tablet (`768px - 1024px`)**: Condensed sidebar, dual-column grid layouts, responsive table viewports with horizontal scroll.
- **Desktop (`>= 1024px`)**: Persistent multi-section sidebar, 4-column metric grid, split-screen Course Player (curriculum index + active lesson content viewer).
