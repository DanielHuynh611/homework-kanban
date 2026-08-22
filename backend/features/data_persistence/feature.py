"""Canonical account, subject, and homework-task API.

The generated project contained several disconnected persistence and
authentication implementations. The public full-stack screens use this
blueprint as the single source of truth.
"""

import re
import uuid
from datetime import date, datetime, timedelta, timezone
from functools import wraps

import bcrypt
import jwt
from flask import Blueprint, current_app, jsonify, request
from sqlalchemy import (
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    MetaData,
    String,
    Table,
    select,
)
from sqlalchemy.exc import IntegrityError

blueprint = Blueprint("capability_data_persistence_8e00a8e9", __name__)

metadata = MetaData()
users = Table(
    "f_8e00a8e9__users",
    metadata,
    Column("id", String(36), primary_key=True),
    Column("email", String(255), nullable=False, unique=True),
    Column("password_hash", String(255), nullable=False),
    Column("created_at", DateTime, nullable=False),
)
subjects = Table(
    "f_8e00a8e9__subjects",
    metadata,
    Column("id", String(36), primary_key=True),
    Column(
        "user_id",
        String(36),
        ForeignKey("f_8e00a8e9__users.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("name", String(100), nullable=False),
    Column("created_at", DateTime, nullable=False),
)
tasks = Table(
    "f_8e00a8e9__tasks",
    metadata,
    Column("id", String(36), primary_key=True),
    Column(
        "user_id",
        String(36),
        ForeignKey("f_8e00a8e9__users.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column(
        "subject_id",
        String(36),
        ForeignKey("f_8e00a8e9__subjects.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("title", String(255), nullable=False),
    Column("due_date", Date, nullable=False),
    Column("priority", String(10), nullable=False),
    Column("status", String(20), nullable=False),
    Column("created_at", DateTime, nullable=False),
    Column("updated_at", DateTime, nullable=False),
    CheckConstraint("priority IN ('low','medium','high')"),
    CheckConstraint("status IN ('to_do','in_progress','done')"),
)

EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
VALID_PRIORITIES = {"low", "medium", "high"}
VALID_STATUSES = {"to_do", "in_progress", "done"}


def _utcnow():
    """Return naive UTC for MySQL TIMESTAMP and SQLite DateTime columns."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def create_schema(engine) -> None:
    """Create the canonical tables for an isolated test database."""
    metadata.create_all(engine)


def _engine():
    return current_app.config["DATABASE_ENGINE"]


def _json_body():
    value = request.get_json(silent=True)
    return value if isinstance(value, dict) else None


def _iso(value):
    return value.isoformat() if value is not None else None


def _serialize_subject(row):
    return {
        "id": row["id"],
        "user_id": row["user_id"],
        "name": row["name"],
        "created_at": _iso(row["created_at"]),
    }


def _serialize_task(row):
    return {
        "id": row["id"],
        "user_id": row["user_id"],
        "subject_id": row["subject_id"],
        "title": row["title"],
        "due_date": _iso(row["due_date"]),
        "priority": row["priority"],
        "status": row["status"],
        "created_at": _iso(row["created_at"]),
        "updated_at": _iso(row["updated_at"]),
    }


def _issue_token(user_id, email):
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {
            "sub": str(user_id),
            "email": email,
            "iss": current_app.config["JWT_ISSUER"],
            "iat": now,
            "exp": now + timedelta(hours=24),
        },
        current_app.config["SECRET_KEY"],
        algorithm="HS256",
    )


def _decode_token(token):
    try:
        return jwt.decode(
            token,
            current_app.config["SECRET_KEY"],
            algorithms=["HS256"],
            issuer=current_app.config["JWT_ISSUER"],
        )
    except jwt.PyJWTError:
        return None


def require_auth(handler):
    @wraps(handler)
    def wrapped(*args, **kwargs):
        authorization = request.headers.get("Authorization", "")
        scheme, _, token = authorization.partition(" ")
        payload = (
            _decode_token(token.strip())
            if scheme.lower() == "bearer" and token.strip()
            else None
        )
        if not payload or not payload.get("sub"):
            return jsonify({
                "code": "UNAUTHORIZED",
                "message": "Authentication required",
            }), 401
        request.user_id = str(payload["sub"])
        request.user_email = payload.get("email")
        return handler(*args, **kwargs)

    return wrapped


@blueprint.post("/api/capability_data_persistence_8e00a8e9/users")
def create_user():
    data = _json_body()
    if data is None:
        return jsonify({"code": "INVALID_REQUEST", "message": "A JSON body is required"}), 400

    email_value = data.get("email")
    password = data.get("password")
    email = email_value.strip().lower() if isinstance(email_value, str) else ""
    if not 3 <= len(email) <= 255 or not EMAIL_PATTERN.fullmatch(email):
        return jsonify({"code": "INVALID_EMAIL", "message": "Email format is invalid"}), 400
    if not isinstance(password, str) or not 8 <= len(password) <= 255:
        return jsonify({
            "code": "INVALID_PASSWORD",
            "message": "Password must be between 8 and 255 characters",
        }), 400

    user_id = str(uuid.uuid4())
    created_at = _utcnow()
    password_hash = bcrypt.hashpw(
        password.encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")
    try:
        with _engine().begin() as connection:
            existing = connection.execute(
                select(users.c.id).where(users.c.email == email)
            ).first()
            if existing:
                return jsonify({
                    "code": "EMAIL_EXISTS",
                    "message": "An account with this email already exists",
                }), 409
            connection.execute(
                users.insert().values(
                    id=user_id,
                    email=email,
                    password_hash=password_hash,
                    created_at=created_at,
                )
            )
    except IntegrityError:
        return jsonify({
            "code": "EMAIL_EXISTS",
            "message": "An account with this email already exists",
        }), 409

    return jsonify({
        "id": user_id,
        "email": email,
        "created_at": _iso(created_at),
    }), 201


@blueprint.post("/api/capability_data_persistence_8e00a8e9/auth/login")
def authenticate_user():
    data = _json_body()
    if data is None:
        return jsonify({"code": "INVALID_REQUEST", "message": "A JSON body is required"}), 400
    email_value = data.get("email")
    password = data.get("password")
    email = email_value.strip().lower() if isinstance(email_value, str) else ""
    if not email or not isinstance(password, str):
        return jsonify({
            "code": "INVALID_CREDENTIALS",
            "message": "Email or password is incorrect",
        }), 401

    with _engine().connect() as connection:
        user = connection.execute(
            select(users).where(users.c.email == email)
        ).mappings().first()
    if not user or not bcrypt.checkpw(
        password.encode("utf-8"), user["password_hash"].encode("utf-8")
    ):
        return jsonify({
            "code": "INVALID_CREDENTIALS",
            "message": "Email or password is incorrect",
        }), 401

    return jsonify({
        "token": _issue_token(user["id"], user["email"]),
        "user": {"id": user["id"], "email": user["email"]},
    }), 200


@blueprint.post("/api/capability_data_persistence_8e00a8e9/subjects")
@require_auth
def create_subject():
    data = _json_body()
    name_value = data.get("name") if data else None
    name = name_value.strip() if isinstance(name_value, str) else ""
    if not 1 <= len(name) <= 100:
        return jsonify({
            "code": "INVALID_NAME",
            "message": "Subject name must be between 1 and 100 characters",
        }), 400

    subject_id = str(uuid.uuid4())
    created_at = _utcnow()
    with _engine().begin() as connection:
        connection.execute(
            subjects.insert().values(
                id=subject_id,
                user_id=request.user_id,
                name=name,
                created_at=created_at,
            )
        )
    return jsonify({
        "id": subject_id,
        "user_id": request.user_id,
        "name": name,
        "created_at": _iso(created_at),
    }), 201


@blueprint.get("/api/capability_data_persistence_8e00a8e9/subjects")
@require_auth
def list_subjects():
    with _engine().connect() as connection:
        rows = connection.execute(
            select(subjects)
            .where(subjects.c.user_id == request.user_id)
            .order_by(subjects.c.created_at, subjects.c.name)
        ).mappings().all()
    return jsonify({"subjects": [_serialize_subject(row) for row in rows]}), 200


@blueprint.post("/api/capability_data_persistence_8e00a8e9/tasks")
@require_auth
def create_task():
    data = _json_body()
    if data is None:
        return jsonify({"code": "INVALID_REQUEST", "message": "A JSON body is required"}), 400
    title_value = data.get("title")
    title = title_value.strip() if isinstance(title_value, str) else ""
    subject_id = data.get("subject_id")
    priority = data.get("priority")
    try:
        due_date = date.fromisoformat(str(data.get("due_date", "")))
    except ValueError:
        due_date = None
    if not 1 <= len(title) <= 255:
        return jsonify({"code": "INVALID_TITLE", "message": "Title must be between 1 and 255 characters"}), 400
    if priority not in VALID_PRIORITIES:
        return jsonify({"code": "INVALID_PRIORITY", "message": "Priority must be low, medium, or high"}), 400
    if due_date is None:
        return jsonify({"code": "INVALID_DATE", "message": "Due date must use YYYY-MM-DD"}), 400

    task_id = str(uuid.uuid4())
    now = _utcnow()
    with _engine().begin() as connection:
        owned_subject = connection.execute(
            select(subjects.c.id).where(
                subjects.c.id == subject_id,
                subjects.c.user_id == request.user_id,
            )
        ).first()
        if not owned_subject:
            return jsonify({
                "code": "SUBJECT_NOT_FOUND",
                "message": "Subject does not exist or does not belong to this user",
            }), 404
        connection.execute(
            tasks.insert().values(
                id=task_id,
                user_id=request.user_id,
                subject_id=subject_id,
                title=title,
                due_date=due_date,
                priority=priority,
                status="to_do",
                created_at=now,
                updated_at=now,
            )
        )
        row = connection.execute(
            select(tasks).where(tasks.c.id == task_id)
        ).mappings().one()
    return jsonify(_serialize_task(row)), 201


@blueprint.get("/api/capability_data_persistence_8e00a8e9/tasks")
@require_auth
def list_tasks():
    with _engine().connect() as connection:
        rows = connection.execute(
            select(tasks)
            .where(tasks.c.user_id == request.user_id)
            .order_by(tasks.c.due_date, tasks.c.created_at)
        ).mappings().all()
    return jsonify({"tasks": [_serialize_task(row) for row in rows]}), 200


@blueprint.patch("/api/capability_data_persistence_8e00a8e9/tasks/<task_id>/status")
@require_auth
def update_task_status(task_id):
    data = _json_body()
    status = data.get("status") if data else None
    if status not in VALID_STATUSES:
        return jsonify({
            "code": "INVALID_STATUS",
            "message": "Status must be to_do, in_progress, or done",
        }), 400

    with _engine().begin() as connection:
        existing = connection.execute(
            select(tasks.c.id).where(
                tasks.c.id == task_id,
                tasks.c.user_id == request.user_id,
            )
        ).first()
        if not existing:
            return jsonify({
                "code": "TASK_NOT_FOUND",
                "message": "Task does not exist or does not belong to this user",
            }), 404
        connection.execute(
            tasks.update()
            .where(tasks.c.id == task_id, tasks.c.user_id == request.user_id)
            .values(status=status, updated_at=_utcnow())
        )
        row = connection.execute(
            select(tasks).where(tasks.c.id == task_id)
        ).mappings().one()
    return jsonify(_serialize_task(row)), 200
