CREATE TABLE IF NOT EXISTS rooms (
  id           SERIAL PRIMARY KEY,
  name         TEXT NOT NULL,
  monthly_rent NUMERIC(12,2) NOT NULL DEFAULT 0,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS users (
  id            SERIAL PRIMARY KEY,
  room_id       INT NOT NULL REFERENCES rooms(id),
  name          TEXT NOT NULL,
  email         TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  role          TEXT NOT NULL DEFAULT 'user' CHECK (role IN ('admin','user')),
  is_active     BOOLEAN NOT NULL DEFAULT TRUE,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS expenses (
  id           SERIAL PRIMARY KEY,
  room_id      INT NOT NULL REFERENCES rooms(id),
  user_id      INT NOT NULL REFERENCES users(id),
  title        TEXT NOT NULL,
  category     TEXT NOT NULL DEFAULT 'Other',
  amount       NUMERIC(12,2) NOT NULL CHECK (amount > 0),
  expense_date DATE NOT NULL DEFAULT CURRENT_DATE,
  note         TEXT,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_expenses_user ON expenses(user_id);
CREATE INDEX IF NOT EXISTS idx_expenses_room_date ON expenses(room_id, expense_date);

-- One rent split per room per month; shares hold each person's portion.
CREATE TABLE IF NOT EXISTS rent_splits (
  id         SERIAL PRIMARY KEY,
  room_id    INT NOT NULL REFERENCES rooms(id),
  month      CHAR(7) NOT NULL,             -- 'YYYY-MM'
  total_rent NUMERIC(12,2) NOT NULL CHECK (total_rent >= 0),
  mode       TEXT NOT NULL CHECK (mode IN ('equal','custom')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (room_id, month)
);

CREATE TABLE IF NOT EXISTS rent_shares (
  id       SERIAL PRIMARY KEY,
  split_id INT NOT NULL REFERENCES rent_splits(id) ON DELETE CASCADE,
  user_id  INT NOT NULL REFERENCES users(id),
  amount   NUMERIC(12,2) NOT NULL CHECK (amount >= 0),
  UNIQUE (split_id, user_id)
);
