# homework-kanban-board full-stack application

This package combines the verified Backend Generator package unchanged with the
current complete responsive Frontend Generator pages. Each compiled page carries
its visual system locally and does not require a frontend CDN at runtime.

## Run locally

1. Create and activate a Python virtual environment.
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and replace its example values.
4. Apply `database/schema.sql` to MySQL.
5. Run `pytest -q`.
6. Start the complete application:
   `flask --app 'fullstack:create_app()' run --debug`
7. Open a screen route listed in `frontend-package-manifest.json`.

## Route setup note

Every completed page is included in this package. More than one page requested
the same browser URL, so the runnable starter uses the first page at that URL:

- `/login` also has the page `frontend/features/browser_based_platform/login_screen.html`.
- `/signup` also has the page `frontend/features/account_creation/sign_up.html`.
- `/login` also has the page `frontend/features/account_creation/login.html`.
- `/signup` also has the page `frontend/features/secured_database_storage/sign_up.html`.
- `/login` also has the page `frontend/features/secured_database_storage/login.html`.
- `/board` also has the page `frontend/features/three_column_kanban_board/kanban_board.html`.
- `/onboarding/subjects` also has the page `frontend/features/add_subjects_during_onboarding/add_subjects_onboarding.html`.
- `/signup` also has the page `frontend/features/password_hashing/account_creation.html`.
- `/login` also has the page `frontend/features/password_hashing/login.html`.
- `/board` also has the page `frontend/features/visual_urgency_indicators/kanban_board_with_urgency_indicators.html`.
- `/board` also has the page `frontend/features/drag_and_drop_task_movement/kanban_board.html`.

Choose a unique URL for each additional page in `fullstack.py` when connecting
the application. If you encounter an error locally, paste it into Goat Helper
for guided debugging.


## Local setup note

The package was assembled successfully, but Zorentia's temporary runtime check
reported:

- `frontend_application_boot_failed`

Your completed files are included. Follow the setup steps above, then paste any
local error into Goat Helper for guided debugging.

