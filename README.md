# rms-api

Backend for the Room Management System (RMS): FastAPI + PyMongo on **MongoDB**.
Frontend repo: **rms-ui**. The app manages **one room**.

- **Users** add their own maintenance expenses and see their totals and rent share.
- **Admin** sees every member's details and spends, manages members, and decides who pays rent and how it is split (equal or custom amounts). The admin is a room member too.

## Architecture

A request travels down through five layers and the answer comes back up. Each layer has one job.

```
HTTP request
  -> router        declares the URL, method and who may call it          app/routers/
  -> controller    calls one service, wraps the result in ApiResponse      app/controllers/
  -> service       business rules, permissions                             app/services/
  -> repository    the only code that queries MongoDB                      app/repositories/
  -> model         the shape of a stored document                          app/models/
```
`app/schemas/` holds the Pydantic request/response shapes, `app/shared/` the reusable helpers, `app/core/` the infrastructure.

```
rms-api/
├── app/
│   ├── main.py                  create_app(): CORS, origin guard, error handlers, routers
│   ├── dependencies.py          who is calling (current_user / require_admin) + builds controllers
│   ├── core/
│   │   ├── config.py            Settings from .env
│   │   ├── database.py          MongoDB client + get_db
│   │   ├── security.py          PasswordHasher, TokenService (JWT)
│   │   ├── exceptions.py        AppError -> NotFound / BadRequest / Conflict / Unauthorized / Forbidden
│   │   ├── error_handlers.py    every error -> the standard envelope
│   │   └── middleware.py        OriginGuardMiddleware
│   ├── shared/
│   │   ├── pagination.py        PageParams, Page, PageMeta, get_page_params
│   │   ├── response.py          ApiResponse  {status, message, data, pagination}
│   │   ├── object_id.py         MongoDB ObjectId <-> string
│   │   ├── dates.py             month helpers (YYYY-MM)
│   │   └── money.py             cents maths so rent shares add up exactly
│   ├── models/                  User, Expense, RentSplit (+ embedded RentShare)
│   ├── schemas/                 request/response shapes per feature
│   ├── repositories/            BaseRepository[T] + user / expense / rent / summary
│   ├── services/                BaseService + auth / user / expense / rent / summary
│   │   └── rent_split_strategies.py   EqualSplit, CustomSplit (strategy pattern)
│   ├── controllers/             auth / user / expense / rent / summary
│   └── routers/                 auth / users / expenses / rent / summary
├── migrations/                  versioned MongoDB migrations (runner + versions/v0001_...)
├── scripts/seed_admin.py        create the first admin
├── docs/postman/                Postman collection
├── requirements.txt, requirements-dev.txt, .env.example
```

OOP used throughout: generic `BaseRepository[T]` and `BaseService` hold shared behaviour and each feature subclasses them; models are classes that know how to convert to/from a MongoDB document; rent splitting is a `SplitStrategy` interface with one class per mode (add a mode = add a class); `PasswordHasher` and `TokenService` are injectable classes.

## MongoDB collections
| Collection | Document |
|---|---|
| `users` | `name, email (unique), password_hash, role, is_active, created_at` |
| `expenses` | `user_id, title, category, amount, expense_date ("YYYY-MM-DD"), note, created_at` |
| `rent_splits` | one per month (`month` unique): `total_rent, mode, shares: [{user_id, amount}]` - the shares are **embedded**, so a split is always saved or replaced as one atomic document |
| `schema_migrations` | which migrations have been applied |

Ids are MongoDB `ObjectId`s, sent to the frontend as 24-character strings.

## API response format
Every endpoint, success or error, returns the same envelope:

```json
{ "status": "success", "message": "Expenses fetched", "data": [ ... ],
  "pagination": { "page": 1, "page_size": 10, "total_items": 42, "total_pages": 5, "has_next": true, "has_prev": false } }
```
- `status` is `"success"` or `"error"`; `pagination` is `null` for anything that is not a list.
- **Listing APIs** (`GET /users`, `/expenses`, `/expenses/mine`) take `?page=1&page_size=10` (`page_size` max 100).
- Errors: `{ "status": "error", "message": "Invalid credentials", "data": null, "pagination": null }` with the matching HTTP code. A database outage returns `503`.

## Migrations
MongoDB has no fixed schema, so migrations here handle **indexes** (including the unique rules) and any future data fixes. Each migration is a file in `migrations/versions/` and runs once; applied versions are recorded in `schema_migrations`.

```bash
python -m migrations status        # applied and pending versions
python -m migrations upgrade       # apply everything pending
python -m migrations downgrade     # undo the last one (-n 2 undoes two)
```
| Version | What it does |
|---|---|
| `0001` | indexes: `users.email` unique, `rent_splits.month` unique, expense lookups by user/date |

To add one: create `migrations/versions/v0002_<what>.py` with a `class Migration(BaseMigration)` that sets `version = "0002"`, `description`, and implements `up()` (and `down()`), then run `upgrade`.

## Run it (Git Bash)
```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env            # edit: MONGODB_URI, JWT_SECRET, ADMIN_*
python -m migrations upgrade    # once, and after pulling new migrations
python -m scripts.seed_admin    # once: creates the admin
uvicorn app.main:app --reload --port 8000
```
Health check: http://localhost:8000/health - API docs: http://localhost:8000/docs

**Getting a MongoDB:**
- *Atlas (hosted, free tier):* create a cluster, add a database user, allow your IP under Network Access, then copy the connection string into `MONGODB_URI`.
- *Local:* install MongoDB Community, or run `docker run -d -p 27017:27017 --name rms-mongo mongo`, and use `mongodb://localhost:27017`.

**Postman:** import `docs/postman/RMS-API.postman_collection.json`, set `adminEmail` / `adminPassword` in the collection variables, then run the folders in order. Tokens are saved to collection variables by the login requests (no copy-paste).

**Tests:** `pip install -r requirements-dev.txt` adds `mongomock`, an in-memory MongoDB for tests.

## Money
- **Fair share** = the month's total spend / active members
- **Balance** = what the person spent - fair share (positive: the others owe them)
- **Rent share** = set by the admin for the members who pay rent
- **Total due** = rent share - balance

## Security
- `.env` is git-ignored. `JWT_SECRET` signs login tokens: use 32+ random characters.
- The login token is checked against the database on every request, so deactivating or deleting a member cuts their access at once.
- Browser calls from origins other than `CLIENT_ORIGIN` get 403 (CORS + origin guard).
- Deleting a member also removes their expenses and rent shares. MongoDB multi-document transactions need a replica set (Atlas has one), so this is done as three ordered steps rather than one transaction.
