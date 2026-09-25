from app.db.course_data.helpers import make_lesson, make_question

# Course 2: Modern Full-Stack Engineering with FastAPI & React
# Slug: modern-full-stack-fastapi-react

MODULE_1_LESSONS = [
    make_lesson(
        title="Modern Python and FastAPI Introduction",
        slug="modern-python-and-fastapi-introduction",
        order_index=1,
        duration_minutes=45,
        description="Core modern Python features (type hints, asyncio) and the architecture of the FastAPI framework.",
        objectives=[
            "Leverage Python 3.10+ type annotations for static analysis and validation",
            "Understand ASGI (Asynchronous Server Gateway Interface) vs WSGI",
            "Initialize and run a production-ready FastAPI application with Uvicorn"
        ],
        content_body="""FastAPI is a modern, high-performance web framework for building APIs with Python 3.8+ based on standard Python type hints and ASGI.

### Key Advantages of FastAPI
- **High Performance**: On par with NodeJS and Go (powered by Starlette and Pydantic).
- **Fast to Code**: Increases feature development speed significantly.
- **Fewer Bugs**: Catches type errors and invalid input before execution.
- **Automatic Docs**: Interactive OpenAPI (Swagger UI) and ReDoc generation out of the box.

### Asynchronous Concurrency (async/await)
FastAPI utilizes Python's `asyncio` event loop. When I/O operations (database queries, HTTP calls) are awaited, the thread is released to process other concurrent requests.""",
        key_concepts=[
            "Python Type Hints and PEP 484/585",
            "ASGI architecture (Starlette) vs WSGI (Flask/Django)",
            "Asynchronous event loop and coroutines",
            "Automatic OpenAPI (Swagger) schema generation"
        ],
        practical_example="""```python
from fastapi import FastAPI

app = FastAPI(
    title="Enterprise LMS API",
    version="1.0.0",
    description="Scalable Learning Management System API"
)

@app.get("/health", tags=["System"])
async def health_check() -> dict[str, str]:
    return {"status": "healthy", "service": "lms-backend"}
```""",
        completion_req="Run a local FastAPI application and test the `/health` endpoint.",
        is_free_preview=True
    ),
    make_lesson(
        title="Path Parameters, Query Parameters, and Request Bodies",
        slug="path-parameters-query-parameters-request-bodies",
        order_index=2,
        duration_minutes=50,
        description="Handling HTTP request data: path parameters with typing, query parameters with defaults, and JSON request bodies.",
        objectives=[
            "Declare and validate path parameters with type constraints",
            "Implement pagination and filtering with query parameters",
            "Parse and validate complex JSON payload bodies"
        ],
        content_body="""FastAPI provides declarative parameter extraction and validation using Python type declarations and helper functions `Path`, `Query`, `Header`, and `Body`.

### Parameter Types
- **Path Parameters**: Extracted from URL segments (e.g., `/courses/{course_id}`). Used to identify specific resources.
- **Query Parameters**: Key-value pairs in the query string (e.g., `?page=1&limit=20&search=cloud`). Used for filtering, sorting, and pagination.
- **Request Body**: JSON payloads deserialized and validated automatically against Pydantic models.""",
        key_concepts=[
            "URL routing and path template matching",
            "Query parameter validation and default values",
            "Pydantic schema injection into route handlers",
            "HTTP 422 Unprocessable Entity automated responses"
        ],
        practical_example="""```python
from fastapi import FastAPI, Path, Query
from pydantic import BaseModel, Field

class CourseCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=100)
    price: float = Field(..., ge=0.0)

app = FastAPI()

@app.post("/courses/{category}")
async def create_course(
    category: str = Path(..., description="The course category code"),
    publish_now: bool = Query(default=False, description="Publish immediately"),
    course: CourseCreate = ...
):
    return {"category": category, "publish_now": publish_now, "course": course.dict()}
```""",
        completion_req="Implement a route handler accepting path, query, and body parameters."
    ),
    make_lesson(
        title="Pydantic Models, Validation, and Serialization",
        slug="pydantic-models-validation-and-serialization",
        order_index=3,
        duration_minutes=55,
        description="Data validation, schema parsing, custom validators, nested models, and response serialization with Pydantic V2.",
        objectives=[
            "Construct Pydantic V2 schemas with strict type annotations",
            "Implement `@field_validator` and `@model_validator` logic",
            "Manage response models and exclude sensitive attributes"
        ],
        content_body="""Pydantic is the data validation and serialization library that powers FastAPI. In Pydantic V2, validation is implemented in Rust (`pydantic-core`), providing a 5-20x performance improvement.

### Core Features
- **Type Coercion**: Converts incoming strings to integers, booleans, or datetimes when valid.
- **Custom Validators**: Apply complex business validation rules before object creation.
- **Serialization Control**: Use `response_model` and `response_model_exclude` to strip sensitive fields (e.g., `hashed_password`).""",
        key_concepts=[
            "BaseModel vs dataclass",
            "Field constraints and regex patterns",
            "field_validator and model_validator (mode='before' / mode='after')",
            "model_dump() and model_dump_json() serialization"
        ],
        practical_example="""```python
from pydantic import BaseModel, EmailStr, Field, field_validator

class UserRegister(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=30)
    password: str = Field(..., min_length=8)

    @field_validator("password")
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v
```""",
        completion_req="Create a validated Pydantic model with custom validation rules."
    ),
    make_lesson(
        title="Dependency Injection in FastAPI",
        slug="dependency-injection-in-fastapi",
        order_index=4,
        duration_minutes=60,
        description="FastAPI Dependency Injection system (`Depends`): reusable components, database sessions, authentication, and hierarchical dependencies.",
        objectives=[
            "Understand FastAPI's `Depends` mechanism and dependency graph",
            "Create database session dependencies with context management (`yield`)",
            "Build layered security dependencies for user authentication and RBAC"
        ],
        content_body="""FastAPI has a powerful **Dependency Injection** system that allows developers to declare reusable logic (database sessions, authentication, permissions, pagination) that is executed before the route handler.

### Key Benefits
- **Shared Logic**: Write authentication or database handling once and inject it into any route.
- **Context Management**: Dependencies using `yield` execute cleanup code after the request finishes (e.g., closing database connections).
- **Testability**: Dependencies can be easily overridden in tests using `app.dependency_overrides`.""",
        key_concepts=[
            "Dependency Injection graph and resolution",
            "Generator dependencies (`yield`) for resource management",
            "Hierarchical / Sub-dependencies",
            "app.dependency_overrides for unit and integration testing"
        ],
        practical_example="""```python
from typing import AsyncGenerator
from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/db")
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

app = FastAPI()

@app.get("/items")
async def read_items(db: AsyncSession = Depends(get_db)):
    # db session is active and automatically closed after response
    return {"message": "session injected"}
```""",
        completion_req="Implement a reusable database session dependency using `Depends`."
    ),
    make_lesson(
        title="Relational Database Integration with SQLAlchemy and Alembic",
        slug="relational-database-integration-sqlalchemy-alembic",
        order_index=5,
        duration_minutes=65,
        description="Database persistence with SQLAlchemy 2.0 ORM, async engines, relationships, migrations with Alembic, and connection pooling.",
        objectives=[
            "Define declarative ORM models and relationships with SQLAlchemy 2.0",
            "Execute efficient async CRUD queries with `select`, `update`, `delete`",
            "Generate and apply schema database migrations with Alembic"
        ],
        content_body="""SQLAlchemy 2.0 provides a modern, type-annotated ORM and database abstraction layer with first-class `asyncio` support.

### SQLAlchemy 2.0 Declarative Models
- Models inherit from `DeclarativeBase`.
- Attributes use `Mapped[T]` and `mapped_column()` with typing for compile-time verification.
- Relationships (`relationship()`) define foreign key associations (1-to-many, many-to-many).

### Alembic Migrations
Alembic tracks database schema evolution over time:
- `alembic revision --autogenerate -m "create users table"`
- `alembic upgrade head`
- `alembic downgrade -1`""",
        key_concepts=[
            "SQLAlchemy 2.0 DeclarativeBase and Mapped types",
            "AsyncEngine and connection pooling (QueuePool, NullPool)",
            "Eager loading (selectinload, joinedload) to prevent N+1 query problems",
            "Alembic migration lifecycle and revision history"
        ],
        practical_example="""```python
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    enrollments: Mapped[list["Enrollment"]] = relationship(back_populates="user")

class Enrollment(Base):
    __tablename__ = "enrollments"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped[User] = relationship(back_populates="enrollments")
```""",
        completion_req="Create SQLAlchemy 2.0 models and configure an Alembic migration."
    ),
    make_lesson(
        title="Authentication and Authorization with OAuth2 and JWT",
        slug="authentication-authorization-oauth2-jwt",
        order_index=6,
        duration_minutes=65,
        description="Implementing secure authentication: password hashing with bcrypt/Argon2, OAuth2 password bearer flow, JWT creation, and Role-Based Access Control (RBAC).",
        objectives=[
            "Hash and verify passwords securely with Passlib/bcrypt",
            "Issue, sign, and verify JSON Web Tokens (JWT) with HS256/RS256",
            "Enforce Role-Based Access Control (RBAC) across endpoints"
        ],
        content_body="""Modern web applications use stateless token-based authentication with JSON Web Tokens (JWT) and OAuth2 Password Bearer flow.

### Authentication Flow
1. Client POSTs credentials (`username`, `password`) to `/api/v1/auth/login`.
2. Backend verifies hashed password (`bcrypt.checkpw`).
3. Backend generates signed JWT containing user identity (`sub`), roles, tenant ID, and expiration (`exp`).
4. Client attaches token in `Authorization: Bearer <token>` header on subsequent requests.
5. Backend verifies signature, validates claims, and injects current user into endpoint.""",
        key_concepts=[
            "Bcrypt / Argon2 password hashing with salt",
            "JWT structure: Header, Payload (Claims), Signature",
            "Token expiration and refresh token strategies",
            "Role-Based Access Control (RBAC) and permission matrices"
        ],
        practical_example="""```python
import jwt
from datetime import datetime, timedelta

SECRET_KEY = "enterprise-secure-jwt-signing-key-32bytes-min"
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=1)) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
```""",
        completion_req="Build an authentication flow issuing and verifying JWT tokens."
    ),
    make_lesson(
        title="Middleware, CORS, and Exception Handling",
        slug="middleware-cors-exception-handling",
        order_index=7,
        duration_minutes=50,
        description="Custom ASGI middleware, Cross-Origin Resource Sharing (CORS), request timing, global exception handlers, and standardized error responses.",
        objectives=[
            "Configure `CORSMiddleware` for secure cross-origin frontend communication",
            "Implement custom ASGI middleware for request IDs and response timing",
            "Register global exception handlers returning RFC 7807 problem details"
        ],
        content_body="""Middleware wraps request processing to execute logic before the request reaches route handlers and after the response is generated.

### Essential Middleware Components
- **CORSMiddleware**: Manages `Access-Control-Allow-Origin`, HTTP methods, and allowed headers for single-page applications.
- **Logging & Tracing Middleware**: Attaches a unique `X-Request-ID` and logs response latency.
- **Global Exception Handlers**: Intercepts unhandled exceptions or custom business exceptions to format consistent JSON error responses.""",
        key_concepts=[
            "ASGI middleware lifecycle and next_call execution",
            "CORS preflight (OPTIONS) requests and credential headers",
            "Custom exception classes and `app.exception_handler`",
            "Standardized API error response envelopes"
        ],
        practical_example="""```python
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://lms.enterprise.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```""",
        completion_req="Configure CORS and add a custom request-timing middleware."
    ),
    make_lesson(
        title="Background Tasks and Asynchronous Operations",
        slug="background-tasks-and-asynchronous-operations",
        order_index=8,
        duration_minutes=55,
        description="Asynchronous processing: FastAPI `BackgroundTasks`, task queues with Celery / ARQ / Redis, and event notifications.",
        objectives=[
            "Use FastAPI `BackgroundTasks` for lightweight post-response tasks",
            "Understand distributed task queues (Celery/ARQ) for heavy computation",
            "Implement email delivery and certificate generation asynchronously"
        ],
        content_body="""Web requests should respond immediately (<200ms). Long-running tasks (generating PDF certificates, sending welcome emails, transcode media) must be processed asynchronously in the background.

### Background Execution Options
1. **FastAPI `BackgroundTasks`**: In-process background tasks executed after returning HTTP response. Suitable for lightweight tasks (sending a webhook, logging).
2. **Distributed Task Queue (Celery / ARQ with Redis)**: Dedicated worker processes consuming from a message broker. Essential for heavy compute, retries, and persistence.""",
        key_concepts=[
            "In-process background tasks vs external task queues",
            "Idempotent task execution and error retry policies",
            "Redis message brokers and worker pools",
            "Non-blocking HTTP responses"
        ],
        practical_example="""```python
from fastapi import BackgroundTasks, FastAPI

app = FastAPI()

def send_welcome_email(email: str, username: str):
    # Simulated email delivery
    print(f"Sending welcome email to {username} ({email})...")

@app.post("/register")
async def register_user(email: str, username: str, bg_tasks: BackgroundTasks):
    # Perform user registration in database
    bg_tasks.add_task(send_welcome_email, email, username)
    return {"message": "User registered successfully; welcome email queued"}
```""",
        completion_req="Implement a background task triggered by an API route."
    ),
    make_lesson(
        title="RESTful API Design and OpenAPI Documentation",
        slug="restful-api-design-and-openapi-documentation",
        order_index=9,
        duration_minutes=55,
        description="Enterprise RESTful design principles, URL naming conventions, HTTP status codes, versioning, and customized OpenAPI / Swagger documentation.",
        objectives=[
            "Apply RESTful conventions (resource nouns, HTTP verb semantics)",
            "Implement API versioning strategies (/api/v1)",
            "Customize Swagger UI documentation with tags, summaries, and examples"
        ],
        content_body="""A well-designed REST API is intuitive, consistent, predictable, and self-documenting.

### REST Architectural Constraints
- **Resource Identification**: Use nouns in plural (e.g., `/api/v1/courses`, `/api/v1/enrollments`).
- **HTTP Methods**: `GET` (safe/idempotent read), `POST` (create), `PUT` (full replace), `PATCH` (partial update), `DELETE` (remove).
- **HTTP Status Codes**:
  - `200 OK`: Success with payload.
  - `201 Created`: Resource created.
  - `204 No Content`: Successful action with empty body.
  - `400 Bad Request`: Client error / malformed request.
  - `401 Unauthorized`: Authentication missing or invalid.
  - `403 Forbidden`: Authenticated, but lacking permissions.
  - `404 Not Found`: Resource does not exist.
  - `409 Conflict`: Duplicate resource or constraint violation.
  - `422 Unprocessable Entity`: Validation failure.""",
        key_concepts=[
            "HTTP verb semantics and idempotency",
            "API URL versioning (/api/v1)",
            "Appropriate HTTP status code selection",
            "OpenAPI 3.1 metadata and response documentation"
        ],
        practical_example="""```python
from fastapi import FastAPI, status
from pydantic import BaseModel

class CourseResponse(BaseModel):
    id: int
    title: str

app = FastAPI()

@app.get(
    "/api/v1/courses/{course_id}",
    response_model=CourseResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Course Details",
    tags=["Courses"]
)
async def get_course(course_id: int):
    return {"id": course_id, "title": "Cloud Architecture"}
```""",
        completion_req="Design a complete RESTful endpoint specification with OpenAPI tags."
    ),
    make_lesson(
        title="Testing FastAPI Applications with Pytest",
        slug="testing-fastapi-applications-with-pytest",
        order_index=10,
        duration_minutes=60,
        description="Automated testing: Pytest fixtures, `httpx.AsyncClient`, database mocking, dependency overrides, and test coverage.",
        objectives=[
            "Configure Pytest fixtures for test databases and HTTP clients",
            "Write asynchronous integration tests with `httpx.AsyncClient`",
            "Override dependencies (authentication, external services) during testing"
        ],
        content_body="""Robust test suites ensure API reliability, prevent regressions, and validate security policies.

### Testing Stack
- **Pytest**: Industry standard Python test framework.
- **HTTPX (`AsyncClient`)**: Asynchronous HTTP test client for executing requests against ASGI apps without starting a network socket.
- **In-Memory SQLite / Test PostgreSQL**: Isolated test databases migrated and cleaned between test runs.""",
        key_concepts=[
            "Pytest fixtures and scope (function, module, session)",
            "Async testing with pytest-asyncio and httpx.AsyncClient",
            "app.dependency_overrides for mocking auth and database",
            "Test coverage analysis with pytest-cov"
        ],
        practical_example="""```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy", "service": "lms-backend"}
```""",
        completion_req="Write and pass Pytest tests for route handlers and authentication."
    )
]

MODULE_2_LESSONS = [
    make_lesson(
        title="Modern JavaScript (ES6+) and TypeScript for React",
        slug="modern-javascript-typescript-for-react",
        order_index=1,
        duration_minutes=50,
        description="JavaScript ES6+ essentials (destructuring, spread, async/await) and TypeScript fundamentals (interfaces, generics, union types) in React.",
        objectives=[
            "Master ES6+ syntax: destructuring, rest/spread, arrow functions, modules",
            "Define TypeScript interfaces, type aliases, and generic props for components",
            "Configure tsconfig.json for strict React 18+ development"
        ],
        content_body="""Modern React applications are built with TypeScript, combining the dynamic flexibility of JavaScript ES6+ with compile-time type safety.

### Modern JavaScript Features in React
- **Destructuring**: Unpacking objects and arrays directly in function parameters.
- **Spread Operator (`...`)**: Immutably copying and merging state objects or arrays.
- **Optional Chaining (`?.`) & Nullish Coalescing (`??`)**: Safe navigation through deeply nested API data.

### TypeScript in React
- **Interfaces vs Types**: Defining component props, API response schemas, and domain models.
- **Generics**: Creating reusable UI components (e.g., generic dropdowns, tables, API clients).""",
        key_concepts=[
            "Immutability patterns in JavaScript",
            "TypeScript interfaces and Type Unions",
            "Generics for reusable components",
            "Strict null checking and type narrowing"
        ],
        practical_example="""```typescript
// Component Props Interface with TypeScript Generics
interface TableProps<T> {
  data: T[];
  columns: { key: keyof T; header: string }[];
  onRowClick?: (item: T) => void;
}

export function DataTable<T extends { id: string | number }>({ data, columns, onRowClick }: TableProps<T>) {
  return (
    <table>
      <thead>
        <tr>{columns.map(c => <th key={String(c.key)}>{c.header}</th>)}</tr>
      </thead>
      <tbody>
        {data.map(row => (
          <tr key={row.id} onClick={() => onRowClick?.(row)}>
            {columns.map(c => <td key={String(c.key)}>{String(row[c.key])}</td>)}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
```""",
        completion_req="Build a typed React component utilizing TypeScript interfaces and generics.",
        is_free_preview=True
    ),
    make_lesson(
        title="React Fundamentals: Components, Props, and State",
        slug="react-fundamentals-components-props-state",
        order_index=2,
        duration_minutes=55,
        description="Core React paradigms: declarative UI, Virtual DOM, JSX syntax, functional components, props drilling, and unidirectional data flow.",
        objectives=[
            "Understand the declarative programming model and Virtual DOM reconciliation",
            "Build modular functional components with typed props",
            "Manage local component state with unidirectional data flow"
        ],
        content_body="""React is a declarative, component-based JavaScript library for building user interfaces.

### Core React Concepts
1. **Declarative UI**: You describe *what* the UI should look like for a given state, and React handles DOM updates.
2. **Virtual DOM**: React maintains an in-memory representation of the DOM and computes efficient diffs (reconciliation) before applying changes.
3. **Props**: Read-only inputs passed from parent to child components.
4. **State**: Mutable data maintained within a component that triggers re-renders when updated.""",
        key_concepts=[
            "Declarative UI vs Imperative DOM manipulation",
            "Virtual DOM reconciliation and React Fiber",
            "Unidirectional data flow (Parent -> Child)",
            "State updates are asynchronous and batched"
        ],
        practical_example="""```tsx
import React, { useState } from 'react';

interface CounterProps {
  initialCount?: number;
  label: string;
}

export const Counter: React.FC<CounterProps> = ({ initialCount = 0, label }) => {
  const [count, setCount] = useState<number>(initialCount);

  return (
    <div className="p-4 border rounded-lg shadow-sm">
      <h3 className="text-lg font-semibold">{label}: {count}</h3>
      <div className="mt-2 space-x-2">
        <button onClick={() => setCount(prev => prev + 1)} className="px-3 py-1 bg-blue-600 text-white rounded">
          Increment
        </button>
        <button onClick={() => setCount(0)} className="px-3 py-1 bg-gray-300 rounded">
          Reset
        </button>
      </div>
    </div>
  );
};
```""",
        completion_req="Create a functional component managing state with typed props."
    ),
    make_lesson(
        title="Hooks in Depth: useState, useEffect, useCallback, useMemo",
        slug="hooks-in-depth-usestate-useeffect-usecallback-usememo",
        order_index=3,
        duration_minutes=65,
        description="Mastering React Hooks: component lifecycle with useEffect, memoization optimization with useMemo and useCallback, and custom hooks.",
        objectives=[
            "Manage side effects and cleanup functions using `useEffect`",
            "Optimize rendering performance with `useMemo` and `useCallback`",
            "Encapsulate reusable stateful logic into custom React hooks"
        ],
        content_body="""React Hooks let you use state and other React features in functional components without writing class components.

### Essential Built-in Hooks
- **`useState`**: Declares a state variable and updater function.
- **`useEffect`**: Synchronizes component with external systems (API fetching, event listeners, subscriptions). Always specify dependency arrays correctly!
- **`useMemo`**: Caches the result of an expensive calculation between renders.
- **`useCallback`**: Caches a function definition between renders to prevent unnecessary child re-renders.
- **`useRef`**: Persists a mutable value across renders without triggering a re-render; also used for direct DOM references.""",
        key_concepts=[
            "Rules of Hooks (call only at top level, only in React functions)",
            "Dependency arrays and stale closures",
            "Memoization trade-offs and performance profiling",
            "Custom Hook composition"
        ],
        practical_example="""```typescript
import { useState, useEffect } from 'react';

// Custom Hook for Debounced Search Input
export function useDebounce<T>(value: T, delay: number = 300): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}
```""",
        completion_req="Write a custom React Hook and optimize a component with `useMemo`."
    ),
    make_lesson(
        title="State Management with Zustand and Context API",
        slug="state-management-with-zustand-context-api",
        order_index=4,
        duration_minutes=60,
        description="Global state architectures: React Context API, lightweight reactive stores with Zustand, persistence, and selector subscriptions.",
        objectives=[
            "Evaluate Context API vs dedicated state libraries (Zustand, Redux Toolkit)",
            "Build atomic, scalable global stores using Zustand",
            "Implement persistent state synchronization with localStorage"
        ],
        content_body="""When application state spans many unrelated component trees (e.g., authenticated user, shopping cart, theme, active enrollment), global state management is required.

### Context API vs Zustand
- **React Context**: Built into React. Great for low-frequency updates (e.g., Theme, Locale). Drawback: Any state change re-renders all consumers of the context.
- **Zustand**: Tiny (1KB), unopinionated, fast store based on the flux pattern. Uses selective subscriptions to ensure components re-render ONLY when their selected slice of state changes.""",
        key_concepts=[
            "Prop drilling anti-pattern and global state boundaries",
            "Zustand store creation and `set` / `get` actions",
            "Selective subscriptions (`useAuthStore(state => state.user)`)",
            "Middleware: `persist` and `devtools`"
        ],
        practical_example="""```typescript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: string;
  email: string;
  role: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  setAuth: (user: User, token: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      setAuth: (user, token) => set({ user, token }),
      logout: () => set({ user: null, token: null }),
    }),
    { name: 'auth-storage' }
  )
);
```""",
        completion_req="Create a Zustand store with actions and persistent storage."
    ),
    make_lesson(
        title="Client-Side Routing with React Router",
        slug="client-side-routing-react-router",
        order_index=5,
        duration_minutes=55,
        description="Single Page Application routing: React Router v6, nested routes, protected/authenticated routes, loaders, and navigation hooks.",
        objectives=[
            "Configure declarative routing using React Router v6 `createBrowserRouter`",
            "Implement layout routes with `<Outlet />` for consistent app shells",
            "Construct protected route guards redirecting unauthenticated users"
        ],
        content_body="""React Router enables client-side routing, allowing single-page applications to update the URL and render corresponding views without full page reloads.

### Key Router Concepts
- **`RouterProvider` & `createBrowserRouter`**: Modern data routing API in React Router 6.4+.
- **Nested Routes & `<Outlet />`**: Nest child routes within parent layouts (e.g., Sidebar + Content area).
- **Protected Routes**: Wrapper components that check authentication state before rendering protected child views.""",
        key_concepts=[
            "Browser history API and client-side route matching",
            "Layouts and the `<Outlet />` component",
            "Programmatic navigation with `useNavigate`",
            "URL parameters (`useParams`) and search parameters (`useSearchParams`)"
        ],
        practical_example="""```tsx
import { Navigate, Outlet } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';

export const ProtectedRoute: React.FC<{ allowedRoles?: string[] }> = ({ allowedRoles }) => {
  const { user, token } = useAuthStore();

  if (!token || !user) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to="/unauthorized" replace />;
  }

  return <Outlet />;
};
```""",
        completion_req="Configure client-side routing with nested layouts and protected route guards."
    ),
    make_lesson(
        title="API Integration with Axios and React Query",
        slug="api-integration-axios-react-query",
        order_index=6,
        duration_minutes=65,
        description="Data fetching architecture: Axios interceptors, TanStack Query (React Query) for server-state caching, optimistic updates, and invalidation.",
        objectives=[
            "Create configured Axios instances with request/response JWT interceptors",
            "Fetch server state with React Query (`useQuery`) with automated caching and refetching",
            "Execute server mutations (`useMutation`) with cache invalidation"
        ],
        content_body="""Handling server state (data that lives on the backend) is fundamentally different from client state. **TanStack Query (React Query)** eliminates boilerplate by managing loading, caching, background synchronization, and retries.

### Axios Interceptors
- **Request Interceptor**: Automatically injects `Authorization: Bearer <token>` into outgoing requests.
- **Response Interceptor**: Catches HTTP 401 Unauthorized responses to trigger token refresh or user logout.

### React Query Paradigms
- `useQuery`: For read operations with unique query keys (`['courses', courseId]`).
- `useMutation`: For create/update/delete operations with `queryClient.invalidateQueries()`.""",
        key_concepts=[
            "Server state vs client state",
            "Axios request and response interceptors",
            "Query keys and stale-while-revalidate caching",
            "Mutations, optimistic updates, and cache invalidation"
        ],
        practical_example="""```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';

const apiClient = axios.create({ baseURL: '/api/v1' });

export function useCourses() {
  return useQuery({
    queryKey: ['courses'],
    queryFn: async () => {
      const response = await apiClient.get('/courses');
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes cache
  });
}
```""",
        completion_req="Implement an API client with interceptors and integrate React Query caching."
    ),
    make_lesson(
        title="Modern Styling with Tailwind CSS",
        slug="modern-styling-with-tailwind-css",
        order_index=7,
        duration_minutes=50,
        description="Utility-first styling: Tailwind CSS configuration, responsive design, dark mode, design tokens, and building reusable UI component libraries.",
        objectives=[
            "Apply utility-first CSS classes for rapid, responsive UI development",
            "Implement responsive layouts with mobile-first breakpoints (sm, md, lg, xl)",
            "Build accessible, themeable UI components with `clsx` and `tailwind-merge`"
        ],
        content_body="""Tailwind CSS is a utility-first CSS framework packed with classes that can be composed directly in markup to build modern designs without writing custom CSS.

### Advantages of Tailwind CSS
- **No Switching Context**: Style elements directly inside your JSX templates.
- **Consistency**: Constrained design system (spacing scale, color palettes, typography).
- **Zero Runtime Overhead**: Purges unused CSS at build time for tiny stylesheet sizes (<10KB).
- **Responsive & Dark Mode**: Simple prefixes like `md:grid-cols-3` and `dark:bg-slate-900`.""",
        key_concepts=[
            "Utility-first methodology vs semantic CSS",
            "Mobile-first responsive design breakpoints",
            "Dark mode toggling with class strategies",
            "Component class merging with `cn()` (`clsx` + `twMerge`)"
        ],
        practical_example="""```tsx
import React from 'react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger';
}

export const Button: React.FC<ButtonProps> = ({ variant = 'primary', className, ...props }) => {
  const baseStyles = "px-4 py-2 rounded-md font-medium transition-colors focus:outline-none focus:ring-2";
  const variants = {
    primary: "bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500",
    secondary: "bg-gray-200 text-gray-800 hover:bg-gray-300 focus:ring-gray-400",
    danger: "bg-red-600 text-white hover:bg-red-700 focus:ring-red-500",
  };

  return <button className={cn(baseStyles, variants[variant], className)} {...props} />;
};
```""",
        completion_req="Build a responsive UI card component using Tailwind CSS utility classes."
    ),
    make_lesson(
        title="Forms and Validation with React Hook Form and Zod",
        slug="forms-and-validation-react-hook-form-zod",
        order_index=8,
        duration_minutes=55,
        description="Type-safe forms: React Hook Form for uncontrolled high-performance inputs, schema validation with Zod, and error handling.",
        objectives=[
            "Build performant forms using React Hook Form without unnecessary re-renders",
            "Define client-side validation schemas with Zod and TypeScript inference",
            "Display field-level validation errors and manage form submission state"
        ],
        content_body="""Managing form state manually in React with `useState` on every keystroke causes unnecessary re-renders. **React Hook Form** uses uncontrolled inputs with refs for high performance.

### Pairing with Zod
**Zod** is a TypeScript-first schema declaration and validation library. By pairing React Hook Form with `@hookform/resolvers/zod`, validation is unified and type-safe from client to server schemas.""",
        key_concepts=[
            "Uncontrolled inputs with `register` vs controlled inputs",
            "Zod schema definition and `z.infer<typeof schema>`",
            "Form state: `isSubmitting`, `errors`, `isValid`",
            "Accessible form error messages and ARIA attributes"
        ],
        practical_example="""```tsx
import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
});

type LoginFormData = z.infer<typeof loginSchema>;

export const LoginForm: React.FC = () => {
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormData) => {
    console.log('Login submitted:', data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 max-w-sm">
      <div>
        <label className="block text-sm font-medium">Email</label>
        <input {...register('email')} className="w-full border p-2 rounded" />
        {errors.email && <p className="text-red-500 text-xs">{errors.email.message}</p>}
      </div>
      <div>
        <label className="block text-sm font-medium">Password</label>
        <input type="password" {...register('password')} className="w-full border p-2 rounded" />
        {errors.password && <p className="text-red-500 text-xs">{errors.password.message}</p>}
      </div>
      <button type="submit" disabled={isSubmitting} className="w-full bg-blue-600 text-white py-2 rounded">
        {isSubmitting ? 'Logging in...' : 'Sign In'}
      </button>
    </form>
  );
};
```""",
        completion_req="Create a form validated with React Hook Form and Zod."
    ),
    make_lesson(
        title="Frontend Security: XSS Prevention and Token Handling",
        slug="frontend-security-xss-prevention-token-handling",
        order_index=9,
        duration_minutes=55,
        description="Security in single-page applications: Cross-Site Scripting (XSS) defense, Content Security Policy (CSP), safe token storage, and sanitization.",
        objectives=[
            "Prevent Cross-Site Scripting (XSS) when rendering user-submitted markdown/HTML",
            "Evaluate token storage strategies (localStorage vs HttpOnly cookies)",
            "Sanitize dynamic content using DOMPurify"
        ],
        content_body="""Single Page Applications (SPAs) are vulnerable to client-side attacks if security is not engineered into every layer.

### Primary Threat Vectors & Countermeasures
1. **Cross-Site Scripting (XSS)**:
   - *Threat*: Malicious scripts injected into the DOM execute in the victim's browser session.
   - *Defense*: React escapes strings automatically in JSX. When rendering HTML/Markdown (e.g., LMS lesson content), always sanitize using **DOMPurify**.
2. **Token Storage**:
   - *localStorage*: Vulnerable to XSS script exfiltration.
   - *HttpOnly, Secure, SameSite Cookies*: Inaccessible to JavaScript, mitigating XSS token theft (requires CSRF protection).
3. **Content Security Policy (CSP)**: HTTP header restricting script and resource load origins.""",
        key_concepts=[
            "XSS types: Stored, Reflected, DOM-based",
            "HTML Sanitization with DOMPurify",
            "localStorage vs HttpOnly Cookie security tradeoffs",
            "Content Security Policy (CSP) and subresource integrity"
        ],
        practical_example="""```tsx
import React from 'react';
import DOMPurify from 'dompurify';

interface SafeHTMLProps {
  rawHtml: string;
}

export const SafeHTML: React.FC<SafeHTMLProps> = ({ rawHtml }) => {
  const cleanHtml = DOMPurify.sanitize(rawHtml, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'h1', 'h2', 'h3', 'ul', 'li', 'code', 'pre'],
    ALLOWED_ATTR: ['href', 'target', 'class'],
  });

  return <div dangerouslySetInnerHTML={{ __html: cleanHtml }} />;
};
```""",
        completion_req="Implement HTML sanitization with DOMPurify on dynamic content."
    ),
    make_lesson(
        title="Testing React Components and Production Build Optimization",
        slug="testing-react-components-production-build-optimization",
        order_index=10,
        duration_minutes=60,
        description="Frontend quality and deployment: Vitest, React Testing Library, user-event interactions, code splitting with React.lazy, and Vite production builds.",
        objectives=[
            "Write component tests with Vitest and React Testing Library",
            "Simulate user interactions with `@testing-library/user-event`",
            "Implement code splitting and bundle optimization with Vite"
        ],
        content_body="""Ensuring frontend quality requires unit/component testing along with production asset optimization.

### Testing Philosophy: React Testing Library
Test components as real users interact with them (query by accessible role or text, rather than implementation details like CSS class names or state variables).

### Production Optimization with Vite
- **Code Splitting**: Use `React.lazy()` and `<Suspense>` to load route bundles on demand.
- **Tree Shaking**: Vite and Rollup automatically eliminate unused code.
- **Asset Hashing**: Cache busting through content-hashed filenames.""",
        key_concepts=[
            "React Testing Library `screen.getByRole` and `findByText`",
            "Mocking API calls with Mock Service Worker (MSW)",
            "Dynamic imports with React.lazy and Suspense boundaries",
            "Vite rollup bundle chunking and Brotli/Gzip compression"
        ],
        practical_example="""```tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect } from 'vitest';
import { Counter } from './Counter';

describe('Counter Component', () => {
  it('increments count on button click', async () => {
    const user = userEvent.setup();
    render(<Counter label="Test Counter" />);

    const incrementButton = screen.getByRole('button', { name: /increment/i });
    expect(screen.getByText(/Test Counter: 0/i)).toBeInTheDocument();

    await user.click(incrementButton);
    expect(screen.getByText(/Test Counter: 1/i)).toBeInTheDocument();
  });
});
```""",
        completion_req="Write a component test with React Testing Library and build the frontend bundle."
    )
]

# 10 Questions for Module 1 Quiz
MODULE_1_QUIZ_QUESTIONS = [
    make_question(1, "What ASGI server is standard for running FastAPI applications in development and production?", "Uvicorn", ["Gunicorn (without worker)", "Apache HTTPD", "Nginx directly"], "Uvicorn is the lightning-fast ASGI server implementation for Python based on uvloop and httptools."),
    make_question(2, "How does FastAPI automatically validate incoming request payloads?", "Through Pydantic schema model annotations", ["Using raw regex strings in every function", "By querying a remote validation server", "FastAPI does not validate input"], "FastAPI uses Pydantic models to inspect, coerce, and validate request bodies and parameters."),
    make_question(3, "What HTTP status code is automatically returned by FastAPI when request validation fails?", "422 Unprocessable Entity", ["400 Bad Request", "404 Not Found", "500 Internal Server Error"], "FastAPI returns 422 Unprocessable Entity with structured validation error details on malformed requests."),
    make_question(4, "How is Dependency Injection declared in FastAPI endpoint signatures?", "Using `Depends(dependency_function)` as a default parameter value", ["With `@inject` decorators above the function", "By editing the global sys.modules dictionary", "Through Python meta-classes"], "FastAPI uses the `Depends()` marker inside function arguments to declare dependencies."),
    make_question(5, "In SQLAlchemy 2.0, what is the modern method for declaring model column types with full static typing?", "`Mapped[T]` and `mapped_column()`", ["`Column(Integer)` only", "`django.models.Field`", "`pydantic.Field`"], "SQLAlchemy 2.0 uses `Mapped[T] = mapped_column(...)` for type-annotated declarative models."),
    make_question(6, "What is Alembic used for in Python database applications?", "Database schema migration management and version tracking", ["Generating frontend React components", "Encrypting JWT tokens", "Serving static image files"], "Alembic is the database migration tool built by the author of SQLAlchemy to version and apply schema updates."),
    make_question(7, "Which hashing algorithm is recommended for securely storing user passwords?", "Bcrypt or Argon2", ["MD5", "SHA-1", "Plain Base64"], "Bcrypt and Argon2 are slow, adaptive, salted hashing functions resistant to brute-force and rainbow table attacks."),
    make_question(8, "What are the three parts that constitute a JSON Web Token (JWT)?", "Header, Payload, and Signature", ["Username, Password, and Role", "Public Key, Private Key, and Salt", "Request, Response, and Cookie"], "A JWT consists of three Base64URL-encoded parts separated by dots: Header, Payload (claims), and Signature."),
    make_question(9, "What is the purpose of CORS (Cross-Origin Resource Sharing) middleware in FastAPI?", "To specify which frontend origins are permitted to access API resources across domains", ["To compress API response payloads", "To optimize database queries", "To route DNS queries"], "CORS headers instruct the browser whether to allow frontend scripts from one origin to read responses from another origin."),
    make_question(10, "What test client is used for asynchronous testing of FastAPI applications without running a live server?", "`httpx.AsyncClient`", ["`requests.Session`", "`urllib.request`", "`selenium.webdriver`"], "HTTPX provides an AsyncClient that interfaces directly with ASGI apps for fast, asynchronous test execution.")
]

# 10 Questions for Module 2 Quiz
MODULE_2_QUIZ_QUESTIONS = [
    make_question(1, "What is the primary benefit of the React Virtual DOM?", "Optimizes UI updates by computing minimal DOM diffs (reconciliation) before applying changes", ["Directly accelerates GPU rendering", "Stores sensitive passwords securely", "Replaces the JavaScript compiler"], "The Virtual DOM calculates minimal required changes to the real DOM, avoiding expensive layout reflows."),
    make_question(2, "Which React Hook is used to execute side effects like API requests and DOM subscriptions?", "`useEffect`", ["`useState`", "`useMemo`", "`useCallback`"], "`useEffect` runs side effects after component rendering and handles cleanup on unmount or dependency change."),
    make_question(3, "What is the difference between `useMemo` and `useCallback` in React?", "`useMemo` memoizes a calculated value; `useCallback` memoizes a function definition", ["`useMemo` is for class components only", "`useCallback` runs synchronously on every frame", "There is no difference"], "`useMemo` caches the return value of a calculation; `useCallback` caches the callback function itself."),
    make_question(4, "Why is Zustand often preferred over React Context for frequently updated global state?", "Zustand uses selective subscriptions so only components reading changed state slices re-render", ["Zustand requires no JavaScript", "Context API is deprecated in React 18", "Zustand can only store numbers"], "Zustand avoids blanket re-renders across the entire component tree through selector-based subscriptions."),
    make_question(5, "In React Router v6, which component is used inside a parent layout to render matching child routes?", "`<Outlet />`", ["`<ChildRoutes />`", "`<Slot />`", "`<Yield />`"], "The `<Outlet />` component renders the element matching the active child route within a parent layout."),
    make_question(6, "What is the primary role of TanStack Query (React Query) in a React application?", "Managing server-state caching, background synchronization, and query invalidation", ["Compiling TypeScript into JavaScript", "Routing URLs on the client", "Styling CSS buttons"], "React Query specializes in server-state management, handling caching, refetching, and mutations."),
    make_question(7, "What is the utility-first CSS philosophy used by Tailwind CSS?", "Applying small, single-purpose utility classes directly in markup to compose designs", ["Writing monolithic CSS style files with BEM naming", "Writing inline CSS strings in JavaScript variables", "Generating CSS from SQL queries"], "Utility-first frameworks like Tailwind provide low-level utility classes that compose directly in JSX."),
    make_question(8, "Why should you use DOMPurify when rendering dynamic HTML or Markdown in React?", "To sanitize and neutralize malicious scripts, preventing Cross-Site Scripting (XSS) attacks", ["To compress HTML strings for faster downloads", "To format markdown into JSON", "To translate text to different languages"], "DOMPurify strips dangerous JavaScript execution vectors from untrusted HTML/markdown before injection."),
    make_question(9, "What library is commonly combined with React Hook Form for type-safe schema validation?", "Zod", ["Moment.js", "Lodash", "JQuery"], "Zod provides schema validation and automatic TypeScript type inference that seamlessly integrates with React Hook Form."),
    make_question(10, "What React feature allows lazy loading of component bundles on demand with code splitting?", "`React.lazy()` and `<Suspense>`", ["`React.memo()`", "`React.Fragment`", "`React.StrictMode`"], "`React.lazy()` dynamically imports components, while `<Suspense>` displays fallback UI during bundle download.")
]

# 20 Questions for Final Assessment Quiz
FINAL_QUIZ_QUESTIONS = [
    make_question(1, "What makes ASGI frameworks like FastAPI capable of handling high concurrent connections?", "Non-blocking asynchronous I/O running on the Python asyncio event loop", ["Multi-threaded GIL removal", "Compiling Python directly to machine assembly", "Using synchronous thread pooling only"], "FastAPI uses ASGI and asyncio so worker threads do not block while awaiting external I/O."),
    make_question(2, "In FastAPI, how do you specify that a path parameter must be an integer greater than or equal to 1?", "`Path(..., ge=1)` with type `int`", ["`Query(default=1)`", "`Body(min=1)`", "`Header(ge=1)`"], "The `Path(..., ge=1)` construct sets metadata and validation constraints on path variables."),
    make_question(3, "What happens when you define `response_model=UserPublic` in a FastAPI route decorator?", "FastAPI serializes the response data to match `UserPublic`, stripping undeclared fields like passwords", ["FastAPI disables all caching", "FastAPI encrypts the JSON response", "FastAPI converts the response into XML"], "The `response_model` filters, validates, and serializes the outgoing response according to the defined schema."),
    make_question(4, "How can a FastAPI dependency perform cleanup operations after an HTTP response is delivered?", "By using the `yield` keyword within the dependency function", ["By calling `sys.exit()`", "By throwing an HTTP 500 exception", "FastAPI dependencies cannot perform cleanup"], "Dependencies with `yield` pause execution, allow the route to respond, and resume for cleanup in the `finally` block."),
    make_question(5, "What database query issue occurs when an ORM fetches child relationships in separate queries per row?", "N+1 query problem", ["Race condition", "Deadlock", "Table fragmentation"], "The N+1 problem occurs when 1 query fetches N parent rows and N subsequent queries fetch related child rows."),
    make_question(6, "In SQLAlchemy 2.0, which eager loading strategy uses a `SELECT ... WHERE id IN (...)` query for collections?", "`selectinload()`", ["`joinedload()`", "`lazyload()`", "`subqueryload()`"], "`selectinload` emits a single second query using the IN operator to load related collections efficiently."),
    make_question(7, "What is the purpose of the `sub` claim in a standard JWT payload?", "Subject: identifies the principal (usually user ID) that is the subject of the token", ["Subscription: describes the billing tier", "Subnet: the user's IP subnet", "Submission: form submission timestamp"], "The `sub` claim is defined in RFC 7519 as the Subject (unique identifier) of the JWT."),
    make_question(8, "Why should sensitive JWT access tokens NOT be stored in browser `localStorage` in high-security apps?", "Any malicious JavaScript running on the page (via XSS) can read and exfiltrate `localStorage` tokens", ["`localStorage` is cleared every 5 minutes", "`localStorage` cannot store strings", "`localStorage` is only available in Firefox"], "JavaScript can access `localStorage`, making tokens stored there vulnerable to XSS exfiltration."),
    make_question(9, "What HTTP method is idempotent and intended to completely replace an existing resource?", "PUT", ["POST", "PATCH", "CONNECT"], "PUT is idempotent and replaces the entire target resource with the supplied payload."),
    make_question(10, "What is the primary difference between `BackgroundTasks` in FastAPI and Celery workers?", "`BackgroundTasks` run in the same server process; Celery workers run as distributed external processes", ["`BackgroundTasks` can survive server crashes", "Celery cannot connect to Redis", "There is no difference"], "FastAPI BackgroundTasks run within the local process; Celery manages independent worker pools with persistent message brokers."),
    make_question(11, "In React, why must state never be mutated directly (e.g., `state.items.push(item)`)?", "React relies on shallow reference equality checks to detect state changes and trigger re-renders", ["JavaScript will throw a runtime syntax error", "Direct mutation deletes the browser cache", "State variables are permanently frozen"], "React checks if the state object reference changed (`Object.is`); direct mutation maintains the same reference, skipping re-renders."),
    make_question(12, "What problem occurs if you omit the dependency array in a `useEffect` hook (`useEffect(() => {})`)?", "The effect will run after EVERY render cycle, potentially causing infinite re-rendering loops", ["The effect will never execute", "The effect will run only once on mount", "React will crash at build time"], "An omitted dependency array causes `useEffect` to execute on every single render."),
    make_question(13, "What is the role of `useRef` when referencing a DOM element in React?", "It holds a direct reference to the rendered HTML DOM element without causing re-renders when updated", ["It triggers a full Virtual DOM rebuild", "It converts the element into a web component", "It automatically styles the element"], "`useRef` creates a mutable container object whose `.current` property references the underlying DOM node."),
    make_question(14, "What is optimistic updating in TanStack Query (React Query)?", "Updating local UI state immediately before the server responds, and rolling back if the request fails", ["Assuming all server requests will succeed without error checking", "Prefetching all API endpoints on page load", "Caching queries indefinitely"], "Optimistic updates provide instant UI feedback by applying anticipated changes before server confirmation."),
    make_question(15, "In React Router, how do you retrieve dynamic route parameters such as `:courseId` from the URL?", "`useParams()` hook", ["`useSearchParams()` hook", "`useLocation()` hook", "`useNavigate()` hook"], "The `useParams()` hook returns an object of key/value pairs of dynamic URL path parameters."),
    make_question(16, "What utility functions are commonly used together to safely merge conditional Tailwind CSS classes?", "`clsx` and `tailwind-merge` (`twMerge`)", ["`lodash` and `jquery`", "`axios` and `zod`", "`vite` and `rollup`"], "`clsx` evaluates conditional class logic, and `tailwind-merge` resolves conflicting Tailwind utility classes."),
    make_question(17, "Why is React Hook Form generally more performant than controlled components with `useState`?", "It uses uncontrolled inputs and DOM refs, eliminating re-renders on every keystroke", ["It runs inside a Web Worker", "It compiles JavaScript into WebAssembly", "It disables browser input validation"], "React Hook Form registers inputs using refs, capturing values only on submit or validation without re-rendering on every keypress."),
    make_question(18, "How does Zod infer TypeScript types from schemas automatically?", "Using `z.infer<typeof schema>`", ["Using `schema.toType()`", "Using `typeof Zod`", "Zod cannot infer types"], "`z.infer<typeof schema>` extracts the exact TypeScript type corresponding to the validated schema structure."),
    make_question(19, "What is the primary role of Axios response interceptors in an enterprise frontend application?", "To centrally intercept responses, handling automatic token refreshes or global 401/500 errors", ["To encrypt the response body on the client", "To convert CSS stylesheets to JavaScript", "To render HTML components into the DOM"], "Response interceptors allow centralized handling of HTTP errors, auth token renewals, and response transformation."),
    make_question(20, "What is the purpose of `<Suspense>` in React applications with code splitting?", "Displays a fallback loading UI while lazy-loaded component bundles are being fetched over the network", ["Pauses JavaScript execution indefinitely", "Catches unhandled runtime exceptions", "Caches database queries on the client"], "`<Suspense>` wraps lazy components and renders a fallback (spinner/skeleton) until the chunk is downloaded.")
]

COURSE_2_DATA = {
    "title": "Modern Full-Stack Engineering with FastAPI & React",
    "slug": "modern-full-stack-fastapi-react",
    "level": "INTERMEDIATE",
    "short_description": "Build production-grade full-stack web applications with Python FastAPI backends and React TypeScript frontends.",
    "description": "Comprehensive full-stack engineering masterclass covering asynchronous Python APIs, Pydantic V2 validation, SQLAlchemy 2.0 ORM, JWT/RBAC security, React 18, TypeScript, Zustand global state, TanStack Query data fetching, Tailwind CSS, and automated testing.",
    "modules": [
        {
            "title": "FastAPI Backend Engineering",
            "slug": "fastapi-backend-engineering",
            "order_index": 1,
            "description": "Master modern Python APIs, request routing, Pydantic validation, dependency injection, SQLAlchemy 2.0 ORM, JWT security, and Pytest.",
            "lessons": MODULE_1_LESSONS,
            "quiz": {
                "title": "Module 1 Quiz: FastAPI Backend Engineering",
                "description": "Test your mastery of FastAPI routing, Pydantic data validation, dependency injection, database ORM, and JWT authentication.",
                "passing_score": 70,
                "questions": MODULE_1_QUIZ_QUESTIONS
            }
        },
        {
            "title": "React Frontend Engineering",
            "slug": "react-frontend-engineering",
            "order_index": 2,
            "description": "Build high-performance client applications with React 18, TypeScript, Hooks, Zustand, React Router, React Query, and Tailwind CSS.",
            "lessons": MODULE_2_LESSONS,
            "quiz": {
                "title": "Module 2 Quiz: React Frontend Engineering",
                "description": "Assess your understanding of React component design, hooks lifecycle, global state management, routing, and form validation.",
                "passing_score": 70,
                "questions": MODULE_2_QUIZ_QUESTIONS
            }
        }
    ],
    "final_quiz": {
        "title": "Final Assessment: Modern Full-Stack Engineering with FastAPI & React",
        "description": "Comprehensive 20-question certification assessment covering the entire FastAPI backend and React TypeScript frontend curriculum.",
        "passing_score": 80,
        "questions": FINAL_QUIZ_QUESTIONS
    }
}
