"""Integration coverage for the browser-facing account and board journey."""

from sqlalchemy import select

from backend.features.data_persistence.feature import users
from fullstack import create_app


API = "/api/capability_data_persistence_8e00a8e9"
PASSWORD = "correct-horse-battery-staple"


def _register_and_login(client, email):
    created = client.post(f"{API}/users", json={"email": email, "password": PASSWORD})
    assert created.status_code == 201
    logged_in = client.post(
        f"{API}/auth/login",
        json={"email": email, "password": PASSWORD},
    )
    assert logged_in.status_code == 200
    return logged_in.get_json()["token"]


def _authorization(token):
    return {"Authorization": f"Bearer {token}"}


def test_root_and_canonical_screens_are_available():
    client = create_app(testing=True).test_client()

    root = client.get("/")
    assert root.status_code == 302
    assert root.headers["Location"].endswith("/login")

    for route in (
        "/signup",
        "/login",
        "/onboarding/subjects",
        "/board",
        "/board/create-task",
        "/board/create-card",
        "/logout",
    ):
        assert client.get(route).status_code == 200

    alias = client.get("/register")
    assert alias.status_code == 302
    assert alias.headers["Location"].endswith("/signup")
    assert client.get(
        "/__frontend_assets/frontend/features/data_persistence/api.js"
    ).status_code == 200


def test_canonical_pages_load_their_interactive_controllers():
    client = create_app(testing=True).test_client()
    page_contracts = {
        "/signup": ("id=\"signup-form\"", "sign_up.js"),
        "/login": ("id=\"login-form\"", "login.js"),
        "/onboarding/subjects": ("id=\"subject-form\"", "add_subjects_onboarding.js"),
        "/board/create-task": ("id=\"task-form\"", "create_task_modal.js"),
        "/board": ("href=\"/board/create-task\"", "kanban_board.js"),
    }
    for route, (control, controller) in page_contracts.items():
        html = client.get(route).get_data(as_text=True)
        assert control in html
        assert "data_persistence/api.js" in html
        assert controller in html
        assert html.index("data_persistence/api.js") < html.index(controller)

    task_page = client.get("/board/create-task").get_data(as_text=True)
    assert "a1b2c3d4-e5f6-7890-abcd-ef1234567890" not in task_page


def test_complete_signup_subject_task_and_move_flow():
    app = create_app(testing=True)
    client = app.test_client()
    token = _register_and_login(client, "student@example.com")
    headers = _authorization(token)

    duplicate = client.post(
        f"{API}/users",
        json={"email": "STUDENT@example.com", "password": PASSWORD},
    )
    assert duplicate.status_code == 409
    assert duplicate.get_json()["code"] == "EMAIL_EXISTS"

    created_subject = client.post(
        f"{API}/subjects", json={"name": "Mathematics"}, headers=headers
    )
    assert created_subject.status_code == 201
    subject_id = created_subject.get_json()["id"]
    assert client.get(f"{API}/subjects", headers=headers).get_json()["subjects"][0][
        "name"
    ] == "Mathematics"

    created_task = client.post(
        f"{API}/tasks",
        json={
            "title": "Finish algebra exercises",
            "subject_id": subject_id,
            "due_date": "2026-08-30",
            "priority": "high",
        },
        headers=headers,
    )
    assert created_task.status_code == 201
    task_id = created_task.get_json()["id"]
    assert created_task.get_json()["status"] == "to_do"

    moved = client.patch(
        f"{API}/tasks/{task_id}/status",
        json={"status": "in_progress"},
        headers=headers,
    )
    assert moved.status_code == 200
    assert moved.get_json()["status"] == "in_progress"
    tasks = client.get(f"{API}/tasks", headers=headers).get_json()["tasks"]
    assert [task["title"] for task in tasks] == ["Finish algebra exercises"]

    with app.config["DATABASE_ENGINE"].connect() as connection:
        stored_hash = connection.execute(
            select(users.c.password_hash).where(users.c.email == "student@example.com")
        ).scalar_one()
    assert stored_hash != PASSWORD
    assert stored_hash.startswith("$2")


def test_users_cannot_read_or_change_each_others_data():
    client = create_app(testing=True).test_client()
    first_token = _register_and_login(client, "first@example.com")
    second_token = _register_and_login(client, "second@example.com")
    first_headers = _authorization(first_token)
    second_headers = _authorization(second_token)

    subject = client.post(
        f"{API}/subjects", json={"name": "Physics"}, headers=first_headers
    ).get_json()
    task = client.post(
        f"{API}/tasks",
        json={
            "title": "Lab report",
            "subject_id": subject["id"],
            "due_date": "2026-09-01",
            "priority": "medium",
        },
        headers=first_headers,
    ).get_json()

    assert client.get(f"{API}/subjects", headers=second_headers).get_json() == {
        "subjects": []
    }
    assert client.get(f"{API}/tasks", headers=second_headers).get_json() == {
        "tasks": []
    }
    cross_user_create = client.post(
        f"{API}/tasks",
        json={
            "title": "Not mine",
            "subject_id": subject["id"],
            "due_date": "2026-09-02",
            "priority": "low",
        },
        headers=second_headers,
    )
    assert cross_user_create.status_code == 404
    cross_user_move = client.patch(
        f"{API}/tasks/{task['id']}/status",
        json={"status": "done"},
        headers=second_headers,
    )
    assert cross_user_move.status_code == 404


def test_invalid_requests_return_clear_client_errors():
    client = create_app(testing=True).test_client()
    assert client.post(f"{API}/users", data="not json").status_code == 400
    assert client.post(
        f"{API}/users", json={"email": "bad", "password": PASSWORD}
    ).status_code == 400
    assert client.post(
        f"{API}/auth/login",
        json={"email": "missing@example.com", "password": PASSWORD},
    ).status_code == 401
    assert client.get(f"{API}/tasks").status_code == 401
