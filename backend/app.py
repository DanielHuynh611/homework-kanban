"""Application factory for the homework Kanban backend."""

from flask import Flask, jsonify
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from backend.core.config import get_settings
from backend.core.database import close_request_database, db
from backend.core.errors import register_error_handlers
from backend.core.jobs import job_registry
from backend.features.data_persistence.feature import (
    blueprint as data_persistence_blueprint,
    create_schema as create_data_persistence_schema,
)
from backend.features.responsive_design.feature import blueprint as responsive_design_blueprint
from backend.features.browser_based_platform.feature import blueprint as browser_based_platform_blueprint
from backend.features.create_homework_cards.feature import blueprint as create_homework_cards_blueprint
from backend.features.account_creation.feature import blueprint as account_creation_blueprint
from backend.features.secured_database_storage.feature import blueprint as secured_database_storage_blueprint
from backend.features.three_column_kanban_board.feature import blueprint as three_column_kanban_board_blueprint
from backend.features.add_subjects_during_onboarding.feature import blueprint as add_subjects_during_onboarding_blueprint
from backend.features.password_hashing.feature import blueprint as password_hashing_blueprint
from backend.features.visual_urgency_indicators.feature import blueprint as visual_urgency_indicators_blueprint
from backend.features.drag_and_drop_task_movement.feature import blueprint as drag_and_drop_task_movement_blueprint
from backend.features.browser_based_platform.feature import register_background_components as register_browser_based_platform_background


def create_app(testing: bool = False, config: dict | None = None) -> Flask:
    overrides = dict(config or {})
    if testing:
        database_url = overrides.pop("DATABASE_URL", "sqlite+pysqlite:///:memory:")
        jwt_secret = overrides.pop(
            "JWT_SECRET", "test-only-secret-change-before-deployment"
        )
        jwt_issuer = overrides.pop("JWT_ISSUER", "homework-kanban-test")
    else:
        settings = get_settings()
        database_url = overrides.pop("DATABASE_URL", settings.database_url)
        jwt_secret = overrides.pop("JWT_SECRET", settings.jwt_secret)
        jwt_issuer = overrides.pop("JWT_ISSUER", settings.jwt_issuer)

    app = Flask(__name__)
    app.config.update(
        TESTING=bool(testing),
        DATABASE_URL=database_url,
        SQLALCHEMY_DATABASE_URI=database_url,
        SECRET_KEY=jwt_secret,
        JWT_ISSUER=jwt_issuer,
    )
    app.config.update(overrides)

    engine_options = {"future": True}
    if database_url.startswith("sqlite"):
        engine_options.update(
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    else:
        engine_options["pool_pre_ping"] = True
    app.config["DATABASE_ENGINE"] = create_engine(database_url, **engine_options)

    app.extensions["sqlalchemy"] = db
    app.teardown_appcontext(close_request_database)
    register_error_handlers(app)
    app.register_blueprint(data_persistence_blueprint)
    app.register_blueprint(responsive_design_blueprint)
    app.register_blueprint(browser_based_platform_blueprint)
    app.register_blueprint(create_homework_cards_blueprint)
    app.register_blueprint(account_creation_blueprint)
    app.register_blueprint(secured_database_storage_blueprint)
    app.register_blueprint(three_column_kanban_board_blueprint)
    app.register_blueprint(add_subjects_during_onboarding_blueprint)
    app.register_blueprint(password_hashing_blueprint)
    app.register_blueprint(visual_urgency_indicators_blueprint)
    app.register_blueprint(drag_and_drop_task_movement_blueprint)
    register_browser_based_platform_background(job_registry)

    if testing:
        create_data_persistence_schema(app.config["DATABASE_ENGINE"])

    @app.get("/health")
    def health():
        return jsonify({"ok": True, "service": "homework-kanban-board-backend"}), 200

    return app
