"""
Data persistence feature module for Flask application.
Provides user authentication and task management with MySQL persistence.
"""

import re
import uuid
from datetime import datetime
from functools import wraps

import bcrypt
import jwt
from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError

blueprint = Blueprint('capability_data_persistence_8e00a8e9', __name__)


def get_db_connection():
    """Get database connection from Flask app config."""
    engine = create_engine(current_app.config['SQLALCHEMY_DATABASE_URI'])
    return engine.connect()


def generate_token(user_id, email):
    """Generate JWT token for authenticated user."""
    secret_key = current_app.config.get('SECRET_KEY', 'default-secret-key')
    payload = {
        'user_id': user_id,
        'email': email,
        'exp': datetime.utcnow().timestamp() + 86400  # 24 hours
    }
    return jwt.encode(payload, secret_key, algorithm='HS256')


def decode_token(token):
    """Decode JWT token and return payload."""
    secret_key = current_app.config.get('SECRET_KEY', 'default-secret-key')
    try:
        return jwt.decode(token, secret_key, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def require_auth(f):
    """Decorator to require authentication for endpoints."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'code': 'UNAUTHORIZED', 'message': 'Authentication required'}), 401
        
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return jsonify({'code': 'UNAUTHORIZED', 'message': 'Authentication required'}), 401
        
        token = parts[1]
        payload = decode_token(token)
        if not payload:
            return jsonify({'code': 'UNAUTHORIZED', 'message': 'Authentication required'}), 401
        
        request.user_id = payload['user_id']
        request.user_email = payload['email']
        return f(*args, **kwargs)
    
    return decorated_function


def validate_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


@blueprint.post('/api/capability_data_persistence_8e00a8e9/users')
def create_user():
    """Create a new student account with hashed password."""
    data = request.get_json()
    
    email = data.get('email', '').strip()
    password = data.get('password', '')
    
    # Validate email format
    if not email or len(email) < 3 or len(email) > 255 or not validate_email(email):
        return jsonify({'code': 'INVALID_EMAIL', 'message': 'Email format is invalid'}), 400
    
    # Validate password length
    if not password or len(password) < 8 or len(password) > 255:
        return jsonify({'code': 'INVALID_PASSWORD', 'message': 'Password must be at least 8 characters'}), 400
    
    # Hash password
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Generate UUID
    user_id = str(uuid.uuid4())
    
    conn = get_db_connection()
    try:
        # Check if email already exists
        result = conn.execute(
            text("SELECT id FROM f_8e00a8e9__users WHERE email = :email"),
            {'email': email}
        )
        if result.fetchone():
            return jsonify({'code': 'EMAIL_EXISTS', 'message': 'An account with this email already exists'}), 409
        
        # Insert new user
        conn.execute(
            text("""
                INSERT INTO f_8e00a8e9__users (id, email, password_hash, created_at)
                VALUES (:id, :email, :password_hash, :created_at)
            """),
            {
                'id': user_id,
                'email': email,
                'password_hash': password_hash,
                'created_at': datetime.utcnow()
            }
        )
        conn.commit()
        
        # Fetch created user
        result = conn.execute(
            text("SELECT id, email, created_at FROM f_8e00a8e9__users WHERE id = :id"),
            {'id': user_id}
        )
        user = result.fetchone()
        
        return jsonify({
            'id': user[0],
            'email': user[1],
            'created_at': user[2].isoformat()
        }), 201
    
    except IntegrityError:
        conn.rollback()
        return jsonify({'code': 'EMAIL_EXISTS', 'message': 'An account with this email already exists'}), 409
    finally:
        conn.close()


@blueprint.post('/api/capability_data_persistence_8e00a8e9/auth/login')
def authenticate_user():
    """Authenticate student login credentials."""
    data = request.get_json()
    
    email = data.get('email', '').strip()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({'code': 'INVALID_CREDENTIALS', 'message': 'Email or password is incorrect'}), 401
    
    conn = get_db_connection()
    try:
        result = conn.execute(
            text("SELECT id, email, password_hash FROM f_8e00a8e9__users WHERE email = :email"),
            {'email': email}
        )
        user = result.fetchone()
        
        if not user:
            return jsonify({'code': 'INVALID_CREDENTIALS', 'message': 'Email or password is incorrect'}), 401
        
        user_id, user_email, password_hash = user[0], user[1], user[2]
        
        # Verify password
        if not bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
            return jsonify({'code': 'INVALID_CREDENTIALS', 'message': 'Email or password is incorrect'}), 401
        
        # Generate token
        token = generate_token(user_id, user_email)
        
        return jsonify({
            'token': token,
            'user': {
                'id': user_id,
                'email': user_email
            }
        }), 200
    
    finally:
        conn.close()


@blueprint.post('/api/capability_data_persistence_8e00a8e9/subjects')
@require_auth
def create_subject():
    """Create a school subject for the authenticated student."""
    data = request.get_json()
    
    name = data.get('name', '').strip()
    
    # Validate name
    if not name or len(name) < 1 or len(name) > 100:
        return jsonify({'code': 'INVALID_NAME', 'message': 'Subject name must be between 1 and 100 characters'}), 400
    
    subject_id = str(uuid.uuid4())
    user_id = request.user_id
    
    conn = get_db_connection()
    try:
        conn.execute(
            text("""
                INSERT INTO f_8e00a8e9__subjects (id, user_id, name, created_at)
                VALUES (:id, :user_id, :name, :created_at)
            """),
            {
                'id': subject_id,
                'user_id': user_id,
                'name': name,
                'created_at': datetime.utcnow()
            }
        )
        conn.commit()
        
        result = conn.execute(
            text("SELECT id, user_id, name, created_at FROM f_8e00a8e9__subjects WHERE id = :id"),
            {'id': subject_id}
        )
        subject = result.fetchone()
        
        return jsonify({
            'id': subject[0],
            'user_id': subject[1],
            'name': subject[2],
            'created_at': subject[3].isoformat()
        }), 201
    
    finally:
        conn.close()


@blueprint.get('/api/capability_data_persistence_8e00a8e9/subjects')
@require_auth
def list_subjects():
    """Retrieve all subjects for the authenticated student."""
    user_id = request.user_id
    
    conn = get_db_connection()
    try:
        result = conn.execute(
            text("""
                SELECT id, user_id, name, created_at
                FROM f_8e00a8e9__subjects
                WHERE user_id = :user_id
                ORDER BY created_at ASC
            """),
            {'user_id': user_id}
        )
        subjects = result.fetchall()
        
        return jsonify({
            'subjects': [
                {
                    'id': subject[0],
                    'user_id': subject[1],
                    'name': subject[2],
                    'created_at': subject[3].isoformat()
                }
                for subject in subjects
            ]
        }), 200
    
    finally:
        conn.close()


@blueprint.post('/api/capability_data_persistence_8e00a8e9/tasks')
@require_auth
def create_task():
    """Create a homework task with all required attributes."""
    data = request.get_json()
    
    title = data.get('title', '').strip()
    subject_id = data.get('subject_id', '').strip()
    due_date = data.get('due_date', '').strip()
    priority = data.get('priority', '').strip()
    
    # Validate title
    if not title or len(title) < 1 or len(title) > 255:
        return jsonify({'code': 'INVALID_TITLE', 'message': 'Title must be between 1 and 255 characters'}), 400
    
    # Validate priority
    if priority not in ['low', 'medium', 'high']:
        return jsonify({'code': 'INVALID_PRIORITY', 'message': 'Priority must be low, medium, or high'}), 400
    
    # Validate due_date format
    try:
        datetime.strptime(due_date, '%Y-%m-%d')
    except (ValueError, TypeError):
        return jsonify({'code': 'INVALID_DUE_DATE', 'message': 'Due date must be a valid date'}), 400
    
    user_id = request.user_id
    task_id = str(uuid.uuid4())
    
    conn = get_db_connection()
    try:
        # Check if subject exists and belongs to user
        result = conn.execute(
            text("SELECT id FROM f_8e00a8e9__subjects WHERE id = :subject_id AND user_id = :user_id"),
            {'subject_id': subject_id, 'user_id': user_id}
        )
        if not result.fetchone():
            return jsonify({'code': 'SUBJECT_NOT_FOUND', 'message': 'Subject does not exist or does not belong to this user'}), 404
        
        # Insert task
        now = datetime.utcnow()
        conn.execute(
            text("""
                INSERT INTO f_8e00a8e9__tasks 
                (id, user_id, subject_id, title, due_date, priority, status, created_at, updated_at)
                VALUES (:id, :user_id, :subject_id, :title, :due_date, :priority, :status, :created_at, :updated_at)
            """),
            {
                'id': task_id,
                'user_id': user_id,
                'subject_id': subject_id,
                'title': title,
                'due_date': due_date,
                'priority': priority,
                'status': 'to_do',
                'created_at': now,
                'updated_at': now
            }
        )
        conn.commit()
        
        result = conn.execute(
            text("""
                SELECT id, user_id, subject_id, title, due_date, priority, status, created_at, updated_at
                FROM f_8e00a8e9__tasks
                WHERE id = :id
            """),
            {'id': task_id}
        )
        task = result.fetchone()
        
        return jsonify({
            'id': task[0],
            'user_id': task[1],
            'subject_id': task[2],
            'title': task[3],
            'due_date': task[4].isoformat(),
            'priority': task[5],
            'status': task[6],
            'created_at': task[7].isoformat(),
            'updated_at': task[8].isoformat()
        }), 201
    
    finally:
        conn.close()


@blueprint.get('/api/capability_data_persistence_8e00a8e9/tasks')
@require_auth
def list_tasks():
    """Retrieve all tasks for the authenticated student."""
    user_id = request.user_id
    
    conn = get_db_connection()
    try:
        result = conn.execute(
            text("""
                SELECT id, user_id, subject_id, title, due_date, priority, status, created_at, updated_at
                FROM f_8e00a8e9__tasks
                WHERE user_id = :user_id
                ORDER BY created_at ASC
            """),
            {'user_id': user_id}
        )
        tasks = result.fetchall()
        
        return jsonify({
            'tasks': [
                {
                    'id': task[0],
                    'user_id': task[1],
                    'subject_id': task[2],
                    'title': task[3],
                    'due_date': task[4].isoformat(),
                    'priority': task[5],
                    'status': task[6],
                    'created_at': task[7].isoformat(),
                    'updated_at': task[8].isoformat()
                }
                for task in tasks
            ]
        }), 200
    
    finally:
        conn.close()


@blueprint.patch('/api/capability_data_persistence_8e00a8e9/tasks/<task_id>/status')
@require_auth
def update_task_status(task_id):
    """Update the Kanban status of a task."""
    data = request.get_json()
    
    status = data.get('status', '').strip()
    
    # Validate status
    if status not in ['to_do', 'in_progress', 'done']:
        return jsonify({'code': 'INVALID_STATUS', 'message': 'Status must be to_do, in_progress, or done'}), 400
    
    user_id = request.user_id
    
    conn = get_db_connection()
    try:
        # Check if task exists and belongs to user
        result = conn.execute(
            text("SELECT id FROM f_8e00a8e9__tasks WHERE id = :task_id AND user_id = :user_id"),
            {'task_id': task_id, 'user_id': user_id}
        )
        if not result.fetchone():
            return jsonify({'code': 'TASK_NOT_FOUND', 'message': 'Task does not exist or does not belong to this user'}), 404
        
        # Update task status
        conn.execute(
            text("""
                UPDATE f_8e00a8e9__tasks
                SET status = :status, updated_at = :updated_at
                WHERE id = :task_id
            """),
            {
                'status': status,
                'updated_at': datetime.utcnow(),
                'task_id': task_id
            }
        )
        conn.commit()
        
        result = conn.execute(
            text("""
                SELECT id, user_id, subject_id, title, due_date, priority, status, created_at, updated_at
                FROM f_8e00a8e9__tasks
                WHERE id = :id
            """),
            {'id': task_id}
        )
        task = result.fetchone()
        
        return jsonify({
            'id': task[0],
            'user_id': task[1],
            'subject_id': task[2],
            'title': task[3],
            'due_date': task[4].isoformat(),
            'priority': task[5],
            'status': task[6],
            'created_at': task[7].isoformat(),
            'updated_at': task[8].isoformat()
        }), 200
    
    finally:
        conn.close()
