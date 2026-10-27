# rms-api

Backend for the Room Management System (RMS): FastAPI + SQLAlchemy + Alembic on Neon (Postgres).
Frontend repo: **rms-ui**. The app manages **one room**; there is no rooms table.

- **Users** add their own maintenance expenses and see their totals and rent share.
- **Admin** sees every member's details and spends, manages members, and decides who pays rent and how it is split (equal or custom amounts). The admin is a room member too.

## Architecture

A request travels down through five layers and the answer comes back up. Each layer has one job.

```
HTTP request
  -> router        declares the URL, method and who may call it          app/routers/
  -> controller    calls one service, wraps the result in ApiResponse      app/controllers/
  -> service       business rules, permissions, transactions (commit)      app/services/
  -> repository    the only code that queries the database                 app/repositories/
  -> model         table definitions (SQLAlchemy)                          app/models/
```
`app/schemas/` holds the Pydantic request/response shapes, `app/shared/` the reusable helpers, `app/core/` the infrastructure.

```
rms-api/
├── app/
│   ├── main.py                  create_app(): CORS, origin guard, error handlers, routers
│   ├── dependencies.py          who is calling (current_user / require_admin) + builds controllers
│   ├── core/
│   │   ├── config.py            Settings from .env
│   │   ├── database.py          engine, session, Base, get_db
│   │   ├── security.py          PasswordHasher, TokenService (JWT)
│   │   ├── exceptions.py        AppError -> NotFound / BadRequest / Conflict / Unauthorized / Forbidden
│   │   ├── error_handlers.py    every error -> the standard envelope
│   │   └── middleware.py        OriginGuardMiddleware
│   ├── shared/
│   │   ├── pagination.py        PageParams, Page, PageMeta, get_page_params
│   │   ├── response.py          ApiResponse  {status, message, data, pagination}
│   │   ├── dates.py             month helpers (YYYY-MM)
│   │   └── money.py             cents maths so rent shares add up exactly
│   ├── models/                  User, Expense, RentSplit, RentShare
│   ├── schemas/                 request/response shapes per feature
│   ├── repositories/            BaseRepository[T] + user / expense / rent / summary
│   ├── services/                BaseService + auth / user / expense / rent / summary
│   │   └── rent_split_strategies.py   EqualSplit, CustomSplit (strategy pattern)
│   ├── controllers/             auth / user / expense / rent / summary
│   └── routers/                 auth / users / expenses / rent / summary
├── migrations/                  Alembic: env.py + versions/0001, 0002, ...
├── scripts/seed_admin.py        create the first admin
├── alembic.ini, requirements.txt, .env.example
```

OOP used throughout: generic `BaseRepository[T]` and `BaseService` hold the shared behaviour, each feature subclasses them; rent splitting is a `SplitStrategy` interface with one class per mode (add a mode = add a class); `PasswordHasher` and `TokenService` are injectable classes.

## API response format
Every endpoint, success or error, returns the same envelope:

```json
{ "status": "success", "message": "Expenses fetched", "data": [ ... ],
  "pagination": { "page": 1, "page_size": 10, "total_items": 42, "total_pages": 5, "has_next": true, "has_prev": false } }
```
- `status` is `"success"` or `"error"`; `pagination` is `null` for anything that is not a list.
- **Listing APIs** (`GET /users`, `/expenses`, `/expenses/mine`) take `?page=1&page_size=10` (`page_size` max 100).
- Errors: `{ "status": "error", "message": "Invalid credentials", "data": null, "pagination": null }` with the matching HTTP code.

## Database migrations (Alembic)
Tables are created and changed only through migrations in `migrations/versions/` (one numbered file per change):

| Revision | What it does |
|---|---|
| `0001` | the original schema (rooms, users, expenses, rent_splits, rent_shares) |
| `0002` | drops `rooms` and every `room_id` (single-room app) |

```bash
alembic current                                  # which revision the database is at
alembic upgrade head                             # apply every new migration
alembic downgrade -1                             # undo the last one
alembic revision --autogenerate -m "add notes"   # after editing a model: draft the next migration, then review it
alembic upgrade head --sql                       # print the SQL instead of running it
```
Workflow for any schema change: edit the model in `app/models/` -> `alembic revision --autogenerate -m "..."` -> read the generated file -> `alembic upgrade head`.

## Run it (Git Bash)
```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env            # edit: DATABASE_URL, JWT_SECRET, ADMIN_*
```
**Brand-new database:**
```bash
alembic upgrade head
python -m scripts.seed_admin
```
**Database that already has the old tables** (created before Alembic was added) - tell Alembic it is at `0001`, then upgrade:
```bash
alembic stamp 0001
alembic upgrade head            # runs 0002: removes the rooms table
```
Start the server:
```bash
uvicorn app.main:app --reload --port 8000
```
Health check: http://localhost:8000/health - API docs: http://localhost:8000/docs

**Postman:** import `docs/postman/RMS-API.postman_collection.json`, set `adminEmail` / `adminPassword` in the collection variables, then run the folders in order. Tokens are saved to collection variables by the login requests (no copy-paste).

## Money
- **Fair share** = the month's total spend / active members
- **Balance** = what the person spent - fair share (positive: the others owe them)
- **Rent share** = set by the admin for the members who pay rent
- **Total due** = rent share - balance

## Security
- `.env` is git-ignored. `JWT_SECRET` signs login tokens: use 32+ random characters.
- The login token is checked against the database on every request, so deactivating or deleting a member cuts their access at once.
- Browser calls from origins other than `CLIENT_ORIGIN` get 403 (CORS + origin guard).
