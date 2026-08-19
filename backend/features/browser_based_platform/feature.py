"""
Browser-based platform authentication module.

This module provides user registration, login, session management, and logout
functionality for a browser-based platform using Flask and MySQL.
"""

import re
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Tuple

from flask import Blueprint, request, jsonify
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash

# Create Blueprint
blueprint = Blueprint('capability_browser_based_platform_b7688c8b', __name__)

# Database connection (should be configured via app config in production)
engine = None


def init_db(database_uri):
    """Initialize database engine."""
    global engine
    engine = create_engine(database_uri, pool_pre_ping=True)


def get_db_connection():
    """Get database connection."""
    if engine is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return engine.connect()


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password: str) -> bool:
    """Validate password strength."""
    return len(password) >= 8


@blueprint.post('/api/capability_browser_based_platform_b7688c8b/auth/register')
def register_user():
    """
    Creates a new student user account with hashed password to enable browser-based access.
    
    Returns:
        JSON response with user_id, email, and created_at on success
        Error response with appropriate status code on failure
    """
    try:
        data = request.get_json(silent=True)
        
        if not data:
            return jsonify({
                'error': 'MISSING_CREDENTIALS',
                'message': 'Request body is required'
            }), 400
        
        email = data.get('email')
        password = data.get('password')
        
        # Validate required fields
        if not email or not password:
            return jsonify({
                'error': 'MISSING_CREDENTIALS',
                'message': 'Email and password are required'
            }), 400
        
        # Validate email format
        if not validate_email(email):
            return jsonify({
                'error': 'INVALID_EMAIL',
                'message': 'Email format is invalid'
            }), 400
        
        # Validate password strength
        if not validate_password(password):
            return jsonify({
                'error': 'WEAK_PASSWORD',
                'message': 'Password must be at least 8 characters'
            }), 400
        
        # Generate user ID and hash password
        user_id = str(uuid.uuid4())
        password_hash = generate_password_hash(password)
        created_at = datetime.utcnow()
        
        # Insert user into database
        conn = get_db_connection()
        try:
            query = text("""
                INSERT INTO f_b7688c8b__users (id, email, password_hash, created_at, updated_at)
                VALUES (:id, :email, :password_hash, :created_at, :updated_at)
            """)
            conn.execute(query, {
                'id': user_id,
                'email': email,
                'password_hash': password_hash,
                'created_at': created_at,
                'updated_at': created_at
            })
            conn.commit()
            
            return jsonify({
                'user_id': user_id,
                'email': email,
                'created_at': created_at.isoformat() + 'Z'
            }), 201
            
        except IntegrityError:
            conn.rollback()
            return jsonify({
                'error': 'EMAIL_EXISTS',
                'message': 'An account with this email already exists'
            }), 409
        finally:
            conn.close()
            
    except Exception as e:
        return jsonify({
            'error': 'INTERNAL_ERROR',
            'message': 'An unexpected error occurred'
        }), 500


@blueprint.post('/api/capability_browser_based_platform_b7688c8b/auth/login')
def login_user():
    """
    Authenticates student credentials and creates a browser session token for stateless HTTP access.
    
    Returns:
        JSON response with session_token, user_id, and expires_at on success
        Error response with appropriate status code on failure
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'MISSING_CREDENTIALS',
                'message': 'Email and password are required'
            }), 400
        
        email = data.get('email')
        password = data.get('password')
        
        # Validate required fields
        if not email or not password:
            return jsonify({
                'error': 'MISSING_CREDENTIALS',
                'message': 'Email and password are required'
            }), 400
        
        # Retrieve user from database
        conn = get_db_connection()
        try:
            query = text("""
                SELECT id, email, password_hash
                FROM f_b7688c8b__users
                WHERE email = :email
            """)
            result = conn.execute(query, {'email': email})
            user = result.fetchone()
            
            if not user or not check_password_hash(user[2], password):
                return jsonify({
                    'error': 'INVALID_CREDENTIALS',
                    'message': 'Email or password is incorrect'
                }), 401
            
            # Create session
            session_id = str(uuid.uuid4())
            session_token = secrets.token_urlsafe(32)
            created_at = datetime.utcnow()
            expires_at = created_at + timedelta(days=7)
            
            insert_query = text("""
                INSERT INTO f_b7688c8b__sessions (id, user_id, token, expires_at, created_at)
                VALUES (:id, :user_id, :token, :expires_at, :created_at)
            """)
            conn.execute(insert_query, {
                'id': session_id,
                'user_id': user[0],
                'token': session_token,
                'expires_at': expires_at,
                'created_at': created_at
            })
            conn.commit()
            
            return jsonify({
                'session_token': session_token,
                'user_id': user[0],
                'expires_at': expires_at.isoformat() + 'Z'
            }), 200
            
        finally:
            conn.close()
            
    except Exception as e:
        return jsonify({
            'error': 'INTERNAL_ERROR',
            'message': 'An unexpected error occurred'
        }), 500


@blueprint.get('/api/capability_browser_based_platform_b7688c8b/auth/validate')
def validate_session():
    """
    Validates browser session token on each HTTP request to maintain authenticated state in stateless browser environment.
    
    Returns:
        JSON response with user_id, email, and session_expires_at on success
        Error response with appropriate status code on failure
    """
    try:
        # Get session token from query parameter or Authorization header
        session_token = request.args.get('session_token')
        
        if not session_token:
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                session_token = auth_header[7:]
        
        if not session_token:
            return jsonify({
                'error': 'MISSING_TOKEN',
                'message': 'Session token is required'
            }), 401
        
        # Validate session token
        conn = get_db_connection()
        try:
            query = text("""
                SELECT s.user_id, s.expires_at, u.email
                FROM f_b7688c8b__sessions s
                JOIN f_b7688c8b__users u ON s.user_id = u.id
                WHERE s.token = :token
            """)
            result = conn.execute(query, {'token': session_token})
            session = result.fetchone()
            
            if not session:
                return jsonify({
                    'error': 'INVALID_SESSION',
                    'message': 'Session token is invalid or expired'
                }), 401
            
            user_id, expires_at, email = session
            
            # Check if session is expired
            if expires_at < datetime.utcnow():
                return jsonify({
                    'error': 'INVALID_SESSION',
                    'message': 'Session token is invalid or expired'
                }), 401
            
            return jsonify({
                'user_id': user_id,
                'email': email,
                'session_expires_at': expires_at.isoformat() + 'Z'
            }), 200
            
        finally:
            conn.close()
            
    except Exception as e:
        return jsonify({
            'error': 'INTERNAL_ERROR',
            'message': 'An unexpected error occurred'
        }), 500


@blueprint.post('/api/capability_browser_based_platform_b7688c8b/auth/logout')
def logout_user():
    """
    Terminates browser session by deleting session token to end authenticated access.
    
    Returns:
        JSON response with success status
        Error response with appropriate status code on failure
    """
    try:
        data = request.get_json(silent=True)
        
        # Get session token from request body or Authorization header
        session_token = None
        if data:
            session_token = data.get('session_token')
        
        if not session_token:
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                session_token = auth_header[7:]
        
        if not session_token:
            return jsonify({
                'error': 'MISSING_TOKEN',
                'message': 'Session token is required'
            }), 401
        
        # Delete session from database
        conn = get_db_connection()
        try:
            query = text("""
                DELETE FROM f_b7688c8b__sessions
                WHERE token = :token
            """)
            result = conn.execute(query, {'token': session_token})
            conn.commit()
            
            if result.rowcount == 0:
                return jsonify({
                    'error': 'INVALID_SESSION',
                    'message': 'Session token is invalid'
                }), 401
            
            return jsonify({
                'success': True
            }), 200
            
        finally:
            conn.close()
            
    except Exception as e:
        return jsonify({
            'error': 'INTERNAL_ERROR',
            'message': 'An unexpected error occurred'
        }), 500


def cleanup_expired_sessions():
    """
    Removes expired session records from database to maintain security and prevent stale session accumulation.
    
    This is a background task that should be called periodically (e.g., via cron job or scheduler).
    
    Returns:
        Dictionary with deleted_count
    """
    try:
        conn = get_db_connection()
        try:
            query = text("""
                DELETE FROM f_b7688c8b__sessions
                WHERE expires_at < :current_time
            """)
            result = conn.execute(query, {'current_time': datetime.utcnow()})
            conn.commit()
            
            return {
                'deleted_count': result.rowcount
            }
            
        finally:
            conn.close()
            
    except Exception as e:
        return {
            'deleted_count': 0,
            'error': str(e)
        }


def register_background_components(registry):
    """Register this feature's maintenance job once per process."""
    function_id = (
        'capability_browser_based_platform_b7688c8b.'
        'function.cleanup_expired_sessions'
    )
    if function_id not in registry.inventory():
        registry.register(function_id, cleanup_expired_sessions)
