# TankWatch

TankWatch is a Django application for account-specific LPG tank simulation and
usage tracking. Members and students can record consumption, review their
consumption history, and edit or delete their own records. Changes update their
remaining tank balance. Administrators can view member levels and adjust a
member's simulated tank percentage.

Consumption records belong to the user who created them. Members and students
can access their own tracker; administrators have separate controls for
managing member tank levels.

## Requirements

- Python 3.10 or later
- Dependencies listed in `requirements.txt`

## Local setup on Windows

Run these commands in PowerShell from the project folder:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

The default `.env.example` configuration uses SQLite. The local database file
is created as `db.sqlite3` and is ignored by Git. Keep `.env` private; it is
also ignored by Git.

Apply database migrations, optionally create an administrator, then start the
development server:

```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open <http://127.0.0.1:8000/> in a browser. Public registration is available
from the login page. Administrators can create and manage accounts in the
custom admin console.

## Database configuration

SQLite is the default for local development. To use PostgreSQL or Supabase,
set `USE_SQLITE=False` in `.env` and configure either `DATABASE_URL` or the
individual `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, and `DB_PORT`
variables. Set `DB_SSL_REQUIRE=True` when the database provider requires SSL.
Run `python manage.py migrate` after configuring the database.

Never commit `.env` or database credentials.

## Tests and checks

Run the test suite:

```powershell
python manage.py test
```

Run Django's configuration check:

```powershell
python manage.py check
```
