"""Server-owned entry point for the assembled Zorentia application."""

import re
from pathlib import Path

from flask import abort, redirect, send_file
from backend import create_app as create_backend_app

PROJECT_ROOT = Path(__file__).resolve().parent
SCREEN_ROUTES = {
    "/signup": "frontend/features/data_persistence/sign_up.html",
    "/login": "frontend/features/data_persistence/login.html",
    "/onboarding/subjects": "frontend/features/data_persistence/add_subjects_onboarding.html",
    "/board": "frontend/features/data_persistence/kanban_board.html",
    "/board/create-task": "frontend/features/data_persistence/create_task_modal.html",
    "/board/create-card": "frontend/features/data_persistence/create_task_modal.html",
    "/board/responsive": "frontend/features/data_persistence/kanban_board.html",
    "/board/responsive/preferences": "frontend/features/data_persistence/kanban_board.html",
    "/logout": "frontend/features/data_persistence/logout.html",
}

ROUTE_ALIASES = {
    "/register": "/signup",
    "/validate-session": "/board",
    "/board/cards": "/board",
}


def _flask_route(route):
    return re.sub(
        r"\{([A-Za-z_][A-Za-z0-9_]*)\}",
        lambda match: "<" + match.group(1) + ">",
        route,
    )


def _project_file(relative_path):
    target = (PROJECT_ROOT / relative_path).resolve()
    if target != PROJECT_ROOT and PROJECT_ROOT not in target.parents:
        raise RuntimeError("frontend_route_path_invalid")
    return target


def create_app(testing=False, config=None):
    app = create_backend_app(testing=testing, config=config)

    @app.get("/")
    def index():
        return redirect("/login")

    @app.get("/__frontend_assets/<path:relative_path>")
    def frontend_asset(relative_path):
        normalized = str(relative_path or "").replace("\\", "/")
        if not normalized.startswith("frontend/features/") or not normalized.endswith(".js"):
            abort(404)
        return send_file(
            _project_file(normalized),
            mimetype="text/javascript",
        )

    for index, (route, relative_path) in enumerate(SCREEN_ROUTES.items()):
        target = _project_file(relative_path)

        def serve_screen(_target=target, **_route_parameters):
            return send_file(_target, mimetype="text/html")

        app.add_url_rule(
            _flask_route(route),
            endpoint="frontend_screen_" + str(index),
            view_func=serve_screen,
            methods=["GET"],
        )

    for index, (route, target) in enumerate(ROUTE_ALIASES.items()):
        def redirect_alias(_target=target):
            return redirect(_target)

        app.add_url_rule(
            route,
            endpoint="frontend_alias_" + str(index),
            view_func=redirect_alias,
            methods=["GET"],
        )
    return app
