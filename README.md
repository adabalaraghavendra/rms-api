# rms-api

Backend for the Room Management System (RMS): FastAPI + Neon (Postgres).
Frontend repo: **rms-ui**.

## What it does
- **Users** add their own maintenance expenses and see their totals and rent share.
- **Admin** sees every member's details and spends, manages members, and decides who pays rent and how it is split (equally or custom amounts).

## Structure
```
rms-api/
├── app/
│   ├── main.py              creates the app, CORS, error format, registers routers
│   ├── core/
│   │   ├── config.py        reads settings from .env
│   │   ├── database.py      Neon connection pool + query helpers
│   │   └── security.py      password hashing, JWT tokens, admin-only guard
│   └── routers/             one file per feature (the endpoints)
│       ├── auth.py          login, my profile, change password
│       ├── users.py         members (add / edit / delete), room settings   [admin]
│       ├── expenses.py      add / edit / delete expenses, list mine or all
│       ├── rent.py          monthly rent split (equal or custom)            [admin]
│       └── summary.py       totals: spent, fair share, balance, rent
├── scripts/init_db.py       one-time: create tables + first admin
├── sql/schema.sql           database tables
├── requirements.txt
└── .env.example             copy to .env and fill in
```

## Database tables
`rooms` · `users` (role = admin | user) · `expenses` · `rent_splits` (one per month) · `rent_shares` (each payer's part)

## How the money is calculated
- **Fair share** = room's total maintenance for the month ÷ active members
- **Balance** = what the person spent − fair share (positive: others owe them)
- **Rent share** = set by the admin for the members who pay rent
- **Total due** = rent share − balance

## Run it (Git Bash)
```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env          # edit: DATABASE_URL, JWT_SECRET, ADMIN_EMAIL, ADMIN_PASSWORD
python -m scripts.init_db     # once: creates tables and the admin
uvicorn app.main:app --reload --port 5000
```
Health check: http://localhost:5000/health · API docs: http://localhost:5000/docs

## Secrets
Real values live only in `.env` (git-ignored). `JWT_SECRET` signs login tokens; generate one with
`python -c "import secrets; print(secrets.token_urlsafe(48))"`.
