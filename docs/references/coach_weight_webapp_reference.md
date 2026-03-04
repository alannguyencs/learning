# Coach Weight Web App - Architecture Reference

Reference for building a full-stack webapp based on `/Users/alan/Documents/projects/coach_weight`.

## Stack Overview

| Layer    | Technology                          | Port |
|----------|-------------------------------------|------|
| Frontend | React 18 + Tailwind CSS + Axios     | 2513 |
| Backend  | FastAPI (Python) + SQLAlchemy       | 2613 |
| Database | PostgreSQL                          | 5432 |
| LLM      | Google Gemini API (via google-genai) |      |

No Docker — runs natively with a single `start_app.sh` script.

## Project Structure

```
coach_weight/
├── frontend/
│   ├── src/
│   │   ├── pages/           # Route-level components (ChatPage, DashboardPage, Login)
│   │   ├── components/      # Reusable UI (ProtectedRoute, dashboard/, quiz/)
│   │   ├── services/api.js  # Axios client — all backend calls in one file
│   │   ├── hooks/           # Custom hooks (useMessageSender, useDashboardData)
│   │   ├── contexts/        # AuthContext for session state
│   │   ├── utils/           # Helpers (dateUtils, dashboardHelpers)
│   │   └── App.js           # React Router setup
│   └── package.json         # proxy: "http://localhost:2613"
│
├── backend/
│   ├── src/
│   │   ├── main.py          # FastAPI app, CORS, session middleware, routes
│   │   ├── configs.py       # Pydantic Settings loads .env
│   │   ├── database.py      # PostgreSQL connection & session factory
│   │   ├── api/             # Route handlers (chat, dashboard, auth, quiz, etc.)
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── schemas/         # Pydantic request/response DTOs
│   │   ├── crud/            # Data access layer (one file per entity)
│   │   ├── service/         # Business logic + LLM integration
│   │   └── utils/           # Shared utilities
│   ├── sql/                 # Database schema DDL
│   ├── .env                 # API keys, DB creds, secrets
│   └── requirements.txt
│
├── start_app.sh             # Launches backend + frontend together
└── .pre-commit-config.yaml  # Black, Flake8, Pylint, ESLint, Prettier
```

## Key Architecture Patterns

### Frontend-Backend Communication

- Frontend proxies `/api/*` to backend in dev via `package.json` proxy setting
- Axios client in `services/api.js` centralizes all API calls with `withCredentials: true`
- Session/cookie-based auth (backend uses Starlette SessionMiddleware)

### Backend Layering

```
api/ (routes) → service/ (business logic) → crud/ (data access) → models/ (ORM)
         ↕                    ↕
     schemas/            service/llm/
   (validation)        (LLM calls)
```

Each layer has a clear responsibility — routes handle HTTP, services contain logic, CRUD handles DB queries.

### Auth Flow

1. `POST /api/login/` — server creates session cookie
2. Frontend stores auth state in `AuthContext`
3. `ProtectedRoute` component gates authenticated pages
4. Axios sends cookies automatically via `withCredentials: true`

## Key API Endpoints

| Area       | Method | Endpoint                          |
|------------|--------|-----------------------------------|
| Auth       | POST   | `/api/login/`, `/api/login/logout` |
| Chat       | POST   | `/api/chat/message`               |
| Dashboard  | GET    | `/api/dashboard/weights`, `/foods`, `/exercises` |
| Dimensions | GET    | `/api/dimensions`, `/dimensions/trends` |
| Quiz       | POST   | `/api/quiz/generate`, `/api/quiz/{id}/answer` |
| Reminders  | GET/PUT| `/api/reminder-settings`          |

## Dev Setup

```bash
# Backend
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
source .env
uvicorn src.main:app --host 0.0.0.0 --port 2613 --reload

# Frontend
cd frontend
npm install
npm start  # port 2513, proxies API to 2613
```

Or just: `./start_app.sh`

## Code Quality

Enforced via `.pre-commit-config.yaml`:
- **Backend**: Black formatter, Flake8, Pylint, max 300 lines/file
- **Frontend**: ESLint, Prettier, max 300 lines/file

## Takeaways for New Projects

1. **Single `services/api.js`** keeps all HTTP calls in one place — easy to maintain
2. **Custom hooks** per feature (e.g. `useDashboardData`) keep components clean
3. **Backend layering** (api → service → crud → models) scales well
4. **Pydantic Settings** for typed config from `.env` avoids stringly-typed config
5. **Proxy in `package.json`** eliminates CORS headaches in dev
6. **`start_app.sh`** script to launch everything with one command
