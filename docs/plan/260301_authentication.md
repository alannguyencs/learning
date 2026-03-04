# Authentication

**Feature**: User authentication with JWT cookie-based sessions
**Project**: Learning App

---

## Problem Statement

1. The app tracks per-user quiz history, recall scores, and memory state. Without authentication, there is no way to associate this data with a specific user.
2. Protected pages (quiz, dashboard) must be restricted to authenticated users only.
3. No registration flow is needed — accounts are pre-created.

---

## Proposed Solution

Copy the proven authentication system from `coach_weight`. It provides:

- **Backend**: JWT token generation (HS256, 90-day expiry), bcrypt password hashing, HttpOnly cookie sessions, and a `/api/me` endpoint for session restore.
- **Frontend**: React AuthContext with login/logout/checkAuth, ProtectedRoute wrapper, and a Login page.
- Two auth mechanisms: OAuth2 Bearer (for tooling/API clients) and Session Cookie (for frontend).

---

## Current Implementation Analysis

### What Exists (keep as-is)

New project — no existing code.

### What Changes

| Component | Current (coach_weight) | Proposed (learning) |
|-----------|----------------------|---------------------|
| Post-login redirect | `/chat` | `/quiz` |
| Protected routes | `/chat`, `/dashboard`, `/settings/reminders` | `/quiz`, `/dashboard` |
| Database table name | `users` | `users` (same) |
| CRUD session handling | `SessionLocal()` direct | `db: Session` via FastAPI `Depends(get_db)` |

---

## Implementation Plan

### Key Workflow

**To Delete:** None
**To Update:** None
**To Add New:**

Login, session restore, and logout flows — same as `coach_weight`.

```
Login:
  POST /api/login {username, password}
    → bcrypt.verify → create_access_token(90d)
    → Set-Cookie (HttpOnly) → Navigate to /quiz

Session Restore:
  Page load → AuthContext calls GET /api/me
    → Read cookie → decode JWT → get_user(username)
    → Return {authenticated, user}

Logout:
  POST /api/login/logout → Delete cookie → Clear frontend state
```

### Database Schema

**To Delete:** None
**To Update:** None
**To Add New:**

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    role VARCHAR
);
```

File: `scripts/sql/create_all_tables.sql`

ORM model: `backend/src/models/user.py`

```python
class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=True)
```

**Copy from:** `coach_weight/backend/src/models/user.py` — use as-is (includes `to_dict()` method).

### CRUD

**To Delete:** None
**To Update:** None
**To Add New:**

File: `backend/src/crud/crud_user.py`

| Function | Signature | Description |
|----------|-----------|-------------|
| `get_user_by_username` | `(db: Session, username: str) -> Optional[Users]` | Query by username |
| `get_user_by_id` | `(db: Session, user_id: int) -> Optional[Users]` | Query by PK |
| `create_user` | `(db: Session, username: str, hashed_password: str, role: Optional[str]) -> Users` | Insert new user |
| `update_user_password` | `(db: Session, user_id: int, new_hashed_password: str) -> Optional[Users]` | Update password |
| `delete_user` | `(db: Session, user_id: int) -> bool` | Delete by PK |

**Copy from:** `coach_weight/backend/src/crud/crud_user.py`
**Modify:** Replace `SessionLocal()` direct calls with `db: Session` parameter (injected via FastAPI `Depends(get_db)`).

### Services

**To Delete:** None
**To Update:** None
**To Add New:**

File: `backend/src/auth.py`

| Function | Signature | Description |
|----------|-----------|-------------|
| `authenticate_user` | `(db: Session, username: str, password: str) -> Union[Users, bool]` | bcrypt verify |
| `create_access_token` | `(data: dict, expires_delta: Optional[timedelta]) -> str` | HS256 JWT, default 90d |
| `get_current_user_from_token` | `(db: Session, token: str) -> Optional[Users]` | Decode JWT, fetch user |
| `authenticate_user_from_request` | `(request: Request, db: Session) -> Union[Users, bool]` | Read cookie, delegate |

Config constants:
- `SECRET_KEY` from `JWT_SECRET_KEY` env var
- `ALGORITHM = "HS256"`
- `ACCESS_TOKEN_EXPIRE_SECONDS = 7_776_000` (90 days)

**Copy from:** `coach_weight/backend/src/auth.py`
**Modify:** Add `db: Session` parameter to functions that query the database (instead of creating sessions internally).

Pydantic schemas — file: `backend/src/schemas/auth.py`

```python
class Token(BaseModel):
    access_token: str
    token_type: str

class LoginRequest(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    role: Optional[str] = None
    class Config:
        from_attributes = True
```

**Copy from:** `coach_weight/backend/src/schemas/auth.py`

### API Endpoints

**To Delete:** None
**To Update:** None
**To Add New:**

File: `backend/src/api/auth.py`

| Method | Path | Request | Response |
|--------|------|---------|----------|
| POST | `/auth/token` | `OAuth2PasswordRequestForm` | `{"access_token": "...", "token_type": "bearer"}` |

**Copy from:** `coach_weight/backend/src/api/auth.py` — use as-is.

File: `backend/src/api/login.py`

| Method | Path | Request | Response |
|--------|------|---------|----------|
| POST | `/api/login/` | `{"username": "...", "password": "..."}` | `{"success": true, "message": "...", "user": {...}}` + Set-Cookie |
| POST | `/api/login/logout` | — | `{"success": true, "message": "Logout successful"}` + delete cookie |

Cookie config: `HttpOnly=True`, `SameSite=Lax`, `Secure=False` (localhost), `Max-Age=7776000`, `Path=/`.

**Copy from:** `coach_weight/backend/src/api/login.py` — use as-is.

File: `backend/src/api/root.py`

| Method | Path | Request | Response |
|--------|------|---------|----------|
| GET | `/api/me` | — | `{"authenticated": true/false, "user": {...}/null}` |

**Copy from:** `coach_weight/backend/src/api/root.py` — use as-is.

### Testing

**To Delete:** None
**To Update:** None
**To Add New:**

#### Backend Test Infrastructure

File: `backend/tests/conftest.py`

```python
import pytest
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from src.database import Base, get_db
from src.main import app

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
```

**Copy from:** `fullstack_main_website-main/backend/tests/conftest.py`

#### Backend Test Files

File: `backend/tests/test_auth.py`

- **Class: `TestAuthService`**
  - `test_create_access_token` — token contains username and expire claims
  - `test_authenticate_user_correct_password` — mocks bcrypt, returns Users object
  - `test_authenticate_user_wrong_password` — returns False
  - `test_authenticate_user_not_found` — returns False
  - `test_get_current_user_from_valid_token` — returns user
  - `test_get_current_user_from_expired_token` — returns None

File: `backend/tests/test_api_login.py`

- **Class: `TestLoginEndpoints`**
  - `test_login_success` — POST `/api/login/` returns 200, Set-Cookie header present
  - `test_login_wrong_credentials` — returns 401
  - `test_login_missing_fields` — returns 422

File: `backend/tests/test_api_auth.py`

- **Class: `TestAuthEndpoints`**
  - `test_me_authenticated` — GET `/api/me` with valid cookie returns `authenticated: true`
  - `test_me_unauthenticated` — GET `/api/me` without cookie returns `authenticated: false`
  - `test_logout` — POST `/api/login/logout` deletes cookie

File: `backend/tests/test_crud_user.py`

- **Class: `TestUserCRUD`**
  - `test_get_user_by_username` — returns user or None
  - `test_create_user` — inserts and returns user
  - `test_create_duplicate_username` — raises IntegrityError

File: `backend/tests/test_models.py`

- `test_users_table_name` — `__tablename__` is "users"
- `test_users_to_dict` — serialization includes id, username, role

File: `backend/tests/test_schemas.py`

- `test_login_request_valid` — accepts username + password
- `test_login_request_missing_field` — raises validation error
- `test_token_schema` — access_token + token_type
- `test_user_response_from_orm` — `from_attributes = True` works

#### Frontend Test Infrastructure

File: `frontend/src/setupTests.js`

```javascript
import '@testing-library/jest-dom';
```

#### Frontend Test Files

File: `frontend/src/__tests__/contexts/AuthContext.test.js`

- `describe("AuthProvider")`:
  - `it("defaults to unauthenticated")` — initial state check
  - `it("restores session from /api/me")` — mocks API, checks authenticated
  - `it("login sets user and authenticated")` — calls login, checks state
  - `it("logout clears state")` — calls logout, checks cleared
  - `it("useAuth throws outside provider")` — error without AuthProvider

**Copy from:** `fullstack_main_website-main/frontend/src/__tests__/contexts/AuthContext.test.js`
**Modify:** Remove Google auth references. Update API service mocks to match our api.js.

File: `frontend/src/__tests__/components/ProtectedRoute.test.js`

- `it("redirects to /login when not authenticated")`
- `it("renders children when authenticated")`
- `it("shows loading while checking auth")`

File: `frontend/src/__tests__/components/Login.test.js`

- `it("renders login form")` — username and password fields present
- `it("submits credentials")` — mocks login, verifies call
- `it("shows error on failed login")` — mocks error, checks display

### Frontend

**To Delete:** None
**To Update:** None
**To Add New:**

File: `frontend/src/contexts/AuthContext.js`

- React context providing `user`, `authenticated`, `loading`, `login()`, `logout()`, `checkAuth()`
- On mount: calls `GET /api/me` to restore session
- `useAuth()` hook

**Copy from:** `coach_weight/frontend/src/contexts/AuthContext.js` — use as-is.

File: `frontend/src/pages/Login.jsx`

- Login form with username/password fields, error display, loading state
- On success: navigates to `/quiz` (change from `/chat`)

**Copy from:** `coach_weight/frontend/src/pages/Login.jsx`
**Modify:** Change redirect from `/chat` to `/quiz`.

File: `frontend/src/components/ProtectedRoute.jsx`

- Shows loading while checking auth, redirects to `/login` if not authenticated

**Copy from:** `coach_weight/frontend/src/components/ProtectedRoute.jsx` — use as-is.

File: `frontend/src/services/api.js`

- Axios instance with `withCredentials: true`, `baseURL` from env var
- Auth methods: `login()`, `logout()`, `getCurrentUser()`

**Copy from:** `coach_weight/frontend/src/services/api.js`
**Modify:** Remove non-auth endpoints (chat, dashboard, etc.). Keep only auth-related methods. Quiz/dashboard endpoints will be added in later features.

File: `frontend/src/App.js`

- Router with AuthProvider wrapping all routes
- Routes: `/login` (public), `/quiz` and `/dashboard` (ProtectedRoute), `/` redirects to `/quiz`

**Copy from:** `coach_weight/frontend/src/App.js`
**Modify:** Replace routes (`/chat` → `/quiz`, remove `/settings/reminders`).

### Infrastructure (project setup)

**To Delete:** None
**To Update:** None
**To Add New:**

File: `backend/src/main.py`

- FastAPI app with SessionMiddleware (first) + CORSMiddleware (second, `allow_credentials=True`)
- Include `api_router`

**Copy from:** `coach_weight/backend/src/main.py`
**Modify:** Remove non-auth routers. Keep middleware setup.

File: `backend/src/database.py`

- SQLAlchemy engine, `SessionLocal`, `Base`, `get_db()` dependency

**Copy from:** `coach_weight/backend/src/database.py` — use as-is (update DB URL via env vars).

File: `backend/src/configs.py`

- Pydantic Settings loading from `.env`
- Fields: `jwt_secret_key`, `jwt_algorithm`, `middleware_secret_key`, `allowed_origins`, DB credentials

**Copy from:** `coach_weight/backend/src/configs.py`
**Modify:** Remove non-auth config fields (Gemini keys, proactive scheduler, etc.).

File: `backend/src/api/api_router.py`

- Central router registering all endpoint modules

**Copy from:** `coach_weight/backend/src/api/api_router.py`
**Modify:** Only include auth, login, and root routers initially.

Files: `backend/requirements.txt`, `frontend/package.json`, `frontend/tailwind.config.js`, `frontend/postcss.config.js`, `.pre-commit-config.yaml`

**Copy from:** corresponding coach_weight files.
**Modify:** Remove unused dependencies (Gemini, OpenAI, Pillow, etc. from requirements.txt). Keep core: FastAPI, SQLAlchemy, python-jose, passlib, bcrypt, psycopg2-binary, pydantic, pydantic-settings, python-dotenv, uvicorn. Frontend: keep React 18, react-router-dom 6, axios, tailwindcss.

File: `.env` (project root directory)

- Environment variables: `JWT_SECRET_KEY`, `MIDDLEWARE_SECRET_KEY`, `ALLOWED_ORIGINS`, `DB_USERNAME`, `DB_PASSWORD`, `DB_URL`, `DB_NAME`
- Located at **project root**, not inside `backend/`

**Note:** `.env` and `venv/` are located at the **project root directory** (not inside `backend/`). The backend activates the venv from the project root: `source venv/bin/activate`.

File: `.pre-commit-config.yaml`

Pre-commit hooks include test runners for both backend and frontend:

```yaml
# Backend tests
- id: test-backend
  name: test (backend)
  entry: bash -c 'cd backend && dotenv -f ../.env run python -m pytest tests/ -q'
  language: system
  files: ^backend/.*\.py$

# Frontend tests
- id: test-frontend
  name: test (frontend)
  entry: bash -c 'cd frontend && npx react-scripts test --watchAll=false'
  language: system
  files: ^frontend/src/.*\.(js|jsx)$
```

**Copy from:** `fullstack_main_website-main/.pre-commit-config.yaml`
**Modify:** Keep Black, Flake8, ESLint, Prettier hooks from coach_weight. Add test hooks from fullstack_main_website.

File: `scripts/sql/create_all_tables.sql`

- SQL files are located in `scripts/sql/`, not `backend/sql/`
- Initial schema with `users` table only. Other tables added by later features.

### Documentation (`docs/tech_documentation/`)

**To Delete:** None
**To Update:** None
**To Add New:**

- `docs/technical/authentication.md` — already written, no changes needed
- `docs/technical/system_pipelines.md` — Login and Session Restore pipelines already documented

---
