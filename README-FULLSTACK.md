# Homework Kanban full-stack application

The runnable app uses one account, subject, and task API across all public
screens. Browser authentication is stored locally as a short-lived JWT and is
sent on every protected API request.

## Run locally

1. Create and activate a Python virtual environment.
2. Install dependencies: `python -m pip install -r requirements.txt`.
3. Copy `.env.example` to `.env` and replace every example value.
4. For a new MySQL database, apply `database/schema.sql`.
5. Run `.venv/bin/pytest -q`.
6. Start the complete app with
   `flask --app 'fullstack:create_app()' run --debug`.
7. Open `http://127.0.0.1:5000/`; the root redirects to `/login`.

The canonical screens are `/signup`, `/login`, `/onboarding/subjects`,
`/board`, `/board/create-task`, and `/logout`. Older generated screen routes
redirect to their canonical equivalent.

## Update an existing database

Before deploying this version over an existing database, back up MySQL and run
`database/migrations/001_unique_account_email.sql`. Its duplicate-email query
must return zero rows before the unique index can be created.

Never commit `.env`; production must provide `DATABASE_URL`, `JWT_SECRET`, and
`JWT_ISSUER` to the application service.
