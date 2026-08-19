"""
Secured database storage feature module.
Handles user authentication, subjects, and homework tasks with MySQL storage.
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

# Blueprint definition
blueprint = Blueprint('capability_secured_database_storage_8df07551', __name__)

# Database connection helper
def get_db_connection():
    """Get database connection from Flask app config."""
    engine = create_engine(current_app.config['SQLALCHEMY_DATABASE_URI'])
    return engine.connect()

# Authentication decorator
def require_auth(f):
    """Decorator to require JWT authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'code': 'UNAUTHORIZED', 'message': 'Authentication required'}), 401
        
        try:
            # Extract token from "Bearer <token>"
            token = auth_header.split(' ')[1] if ' ' in auth_header else auth_header
            payload = jwt.decode(token, current_app.config.get('SECRET_KEY', 'default-secret-key'), algorithms=['HS256'])
            request.user_id = payload['user_id']
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, KeyError, IndexError):
            return jsonify({'code': 'UNAUTHORIZED', 'message': 'Authentication required'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

# Validation helpers
def is_valid_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_valid_uuid(value):
    """Validate UUID format."""
    try:
        uuid.UUID(value)
        return True
    except (ValueError, AttributeError):
        return False

# Route handlers
@blueprint.post('/api/capability_secured_database_storage_8df07551/users')
def create_user():
    """Creates a new user account with hashed password."""
    data = request.get_json()
    
    if not data:
        return jsonify({'code': 'INVALID_EMAIL', 'message': 'Email format is invalid'}), 400
    
    email = data.get('email', '')
    password = data.get('password', '')
    
    # Validate email
    if not email or len(email) < 3 or len(email) > 255 or not is_valid_email(email):
        return jsonify({'code': 'INVALID_EMAIL', 'message': 'Email format is invalid'}), 400
    
    # Validate password
    if not password or len(password) < 8 or len(password) > 255:
        return jsonify({'code': 'PASSWORD_TOO_SHORT', 'message': 'Password must be at least 8 characters'}), 400
    
    # Hash password
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Generate UUID and timestamp
    user_id = str(uuid.uuid4())
    created_at = datetime.utcnow()
    
    # Insert into database
    conn = get_db_connection()
    try:
        conn.execute(
            text("INSERT INTO f_8df07551__users (id, email, password_hash, created_at) VALUES (:id, :email, :password_hash, :created_at)"),
            {'id': user_id, 'email': email, 'password_hash': password_hash, 'created_at': created_at}
        )
        conn.commit()
    except IntegrityError:
        conn.close()
        return jsonify({'code': 'EMAIL_EXISTS', 'message': 'An account with this email already exists'}), 409
    except Exception as e:
        conn.close()
        return jsonify({'code': 'EMAIL_EXISTS', 'message': 'An account with this email already exists'}), 409
    finally:
        conn.close()
    
    return jsonify({
        'id': user_id,
        'email': email,
        'created_at': created_at.isoformat() + 'Z'
    }), 201

@blueprint.post('/api/capability_secured_database_storage_8df07551/auth/login')
def authenticate_user():
    """Authenticates user credentials and returns JWT token."""
    data = request.get_json()
    
    if not data:
        return jsonify({'code': 'MISSING_CREDENTIALS', 'message': 'Email and password are required'}), 400
    
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'code': 'MISSING_CREDENTIALS', 'message': 'Email and password are required'}), 400
    
    # Query user from database
    conn = get_db_connection()
    try:
        result = conn.execute(
            text("SELECT id, email, password_hash FROM f_8df07551__users WHERE email = :email"),
            {'email': email}
        )
        user = result.fetchone()
    finally:
        conn.close()
    
    if not user:
        return jsonify({'code': 'INVALID_CREDENTIALS', 'message': 'Email or password is incorrect'}), 401
    
    # Verify password
    if not bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
        return jsonify({'code': 'INVALID_CREDENTIALS', 'message': 'Email or password is incorrect'}), 401
    
    # Generate JWT token
    token = jwt.encode(
        {'user_id': user[0], 'email': user[1]},
        current_app.config.get('SECRET_KEY', 'default-secret-key'),
        algorithm='HS256'
    )
    
    return jsonify({
        'user_id': user[0],
        'email': user[1],
        'token': token
    }), 200

@blueprint.post('/api/capability_secured_database_storage_8df07551/subjects')
@require_auth
def create_subject():
    """Stores a new school subject for the authenticated user."""
    data = request.get_json()
    
    if not data:
        return jsonify({'code': 'INVALID_NAME', 'message': 'Subject name must be between 1 and 100 characters'}), 400
    
    name = data.get('name', '')
    
    # Validate name
    if not name or len(name) < 1 or len(name) > 100:
        return jsonify({'code': 'INVALID_NAME', 'message': 'Subject name must be between 1 and 100 characters'}), 400
    
    # Generate UUID and timestamp
    subject_id = str(uuid.uuid4())
    created_at = datetime.utcnow()
    user_id = request.user_id
    
    # Insert into database
    conn = get_db_connection()
    try:
        conn.execute(
            text("INSERT INTO f_8df07551__subjects (id, user_id, name, created_at) VALUES (:id, :user_id, :name, :created_at)"),
            {'id': subject_id, 'user_id': user_id, 'name': name, 'created_at': created_at}
        )
        conn.commit()
    finally:
        conn.close()
    
    return jsonify({
        'id': subject_id,
        'user_id': user_id,
        'name': name,
        'created_at': created_at.isoformat() + 'Z'
    }), 201

@blueprint.get('/api/capability_secured_database_storage_8df07551/subjects')
@require_auth
def get_subjects():
    """Retrieves all subjects for the authenticated user."""
    user_id = request.user_id
    
    # Query subjects from database
    conn = get_db_connection()
    try:
        result = conn.execute(
            text("SELECT id, user_id, name, created_at FROM f_8df07551__subjects WHERE user_id = :user_id ORDER BY created_at"),
            {'user_id': user_id}
        )
        subjects = result.fetchall()
    finally:
        conn.close()
    
    subjects_list = []
    for subject in subjects:
        subjects_list.append({
            'id': subject[0],
            'user_id': subject[1],
            'name': subject[2],
            'created_at': subject[3].isoformat() + 'Z' if subject[3] else None
        })
    
    return jsonify({'subjects': subjects_list}), 200

@blueprint.post('/api/capability_secured_database_storage_8df07551/tasks')
@require_auth
def create_task():
    """Stores a new homework task for the authenticated user."""
    data = request.get_json()
    
    if not data:
        return jsonify({'code': 'INVALID_TITLE', 'message': 'Title must be between 1 and 255 characters'}), 400
    
    title = data.get('title', '')
    subject_id = data.get('subject_id')
    due_date = data.get('due_date')
    priority = data.get('priority')
    user_id = request.user_id
    
    # Validate title
    if not title or len(title) < 1 or len(title) > 255:
        return jsonify({'code': 'INVALID_TITLE', 'message': 'Title must be between 1 and 255 characters'}), 400
    
    # Validate priority
    if priority not in ['low', 'medium', 'high']:
        return jsonify({'code': 'INVALID_PRIORITY', 'message': 'Priority must be low, medium, or high'}), 400
    
    # Validate due_date
    try:
        datetime.strptime(due_date, '%Y-%m-%d')
    except (ValueError, TypeError):
        return jsonify({'code': 'INVALID_DATE', 'message': 'Due date must be a valid date'}), 400
    
    # Validate subject_id exists and belongs to user
    conn = get_db_connection()
    try:
        result = conn.execute(
            text("SELECT id FROM f_8df07551__subjects WHERE id = :subject_id AND user_id = :user_id"),
            {'subject_id': subject_id, 'user_id': user_id}
        )
        subject = result.fetchone()
        
        if not subject:
            conn.close()
            return jsonify({'code': 'SUBJECT_NOT_FOUND', 'message': 'Subject does not exist or does not belong to user'}), 404
        
        # Generate UUID and timestamps
        task_id = str(uuid.uuid4())
        created_at = datetime.utcnow()
        updated_at = created_at
        status = 'todo'
        
        # Insert into database
        conn.execute(
            text("""INSERT INTO f_8df07551__tasks 
                    (id, user_id, subject_id, title, due_date, priority, status, created_at, updated_at) 
                    VALUES (:id, :user_id, :subject_id, :title, :due_date, :priority, :status, :created_at, :updated_at)"""),
            {
                'id': task_id,
                'user_id': user_id,
                'subject_id': subject_id,
                'title': title,
                'due_date': due_date,
                'priority': priority,
                'status': status,
                'created_at': created_at,
                'updated_at': updated_at
            }
        )
        conn.commit()
    finally:
        conn.close()
    
    return jsonify({
        'id': task_id,
        'user_id': user_id,
        'subject_id': subject_id,
        'title': title,
        'due_date': due_date,
        'priority': priority,
        'status': status,
        'created_at': created_at.isoformat() + 'Z',
        'updated_at': updated_at.isoformat() + 'Z'
    }), 201

@blueprint.get('/api/capability_secured_database_storage_8df07551/tasks')
@require_auth
def get_tasks():
    """Retrieves all homework tasks for the authenticated user."""
    user_id = request.user_id
    
    # Query tasks from database
    conn = get_db_connection()
    try:
        result = conn.execute(
            text("""SELECT id, user_id, subject_id, title, due_date, priority, status, created_at, updated_at 
                    FROM f_8df07551__tasks WHERE user_id = :user_id ORDER BY due_date, created_at"""),
            {'user_id': user_id}
        )
        tasks = result.fetchall()
    finally:
        conn.close()
    
    tasks_list = []
    for task in tasks:
        tasks_list.append({
            'id': task[0],
            'user_id': task[1],
            'subject_id': task[2],
            'title': task[3],
            'due_date': task[4].isoformat() if task[4] else None,
            'priority': task[5],
            'status': task[6],
            'created_at': task[7].isoformat() + 'Z' if task[7] else None,
            'updated_at': task[8].isoformat() + 'Z' if task[8] else None
        })
    
    return jsonify({'tasks': tasks_list}), 200

@blueprint.patch('/api/capability_secured_database_storage_8df07551/tasks/<task_id>/status')
@require_auth
def update_task_status(task_id):
    """Updates the status of a homework task."""
    data = request.get_json()
    
    if not data:
        return jsonify({'code': 'INVALID_STATUS', 'message': 'Status must be todo, in_progress, or done'}), 400
    
    status = data.get('status')
    user_id = request.user_id
    
    # Validate status
    if status not in ['todo', 'in_progress', 'done']:
        return jsonify({'code': 'INVALID_STATUS', 'message': 'Status must be todo, in_progress, or done'}), 400
    
    # Update task in database
    conn = get_db_connection()
    try:
        # Check if task exists and belongs to user
        result = conn.execute(
            text("SELECT id FROM f_8df07551__tasks WHERE id = :task_id AND user_id = :user_id"),
            {'task_id': task_id, 'user_id': user_id}
        )
        task = result.fetchone()
        
        if not task:
            conn.close()
            return jsonify({'code': 'TASK_NOT_FOUND', 'message': 'Task does not exist or does not belong to user'}), 404
        
        # Update status
        updated_at = datetime.utcnow()
        conn.execute(
            text("UPDATE f_8df07551__tasks SET status = :status, updated_at = :updated_at WHERE id = :task_id"),
            {'status': status, 'updated_at': updated_at, 'task_id': task_id}
        )
        conn.commit()
        
        # Fetch updated task
        result = conn.execute(
            text("""SELECT id, user_id, subject_id, title, due_date, priority, status, created_at, updated_at 
                    FROM f_8df07551__tasks WHERE id = :task_id"""),
            {'task_id': task_id}
        )
        updated_task = result.fetchone()
    finally:
        conn.close()
    
    return jsonify({
        'id': updated_task[0],
        'user_id': updated_task[1],
        'subject_id': updated_task[2],
        'title': updated_task[3],
        'due_date': updated_task[4].isoformat() if updated_task[4] else None,
        'priority': updated_task[5],
        'status': updated_task[6],
        'created_at': updated_task[7].isoformat() + 'Z' if updated_task[7] else None,
        'updated_at': updated_task[8].isoformat() + 'Z' if updated_task[8] else None
    }), 200
