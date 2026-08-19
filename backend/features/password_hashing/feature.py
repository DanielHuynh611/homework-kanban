"""Password hashing feature module for secure credential storage and verification."""

import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import bcrypt

from backend.core.database import db

blueprint = Blueprint('capability_password_hashing_ea5acd92', __name__)


def _is_valid_uuid(value):
    """Validate UUID format."""
    try:
        uuid.UUID(str(value))
        return True
    except (ValueError, AttributeError):
        return False


def _hash_password_bcrypt(password):
    """Hash a password using bcrypt."""
    try:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    except Exception:
        return None


def _verify_password_bcrypt(password, password_hash):
    """Verify a password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except Exception:
        return False


@blueprint.post('/api/capability_password_hashing_ea5acd92/credentials')
def hash_password():
    """
    Hashes a plaintext password using bcrypt and stores it in the user_credentials table.
    
    This endpoint ensures plaintext passwords are never stored and that secure hashing
    is applied before persistence.
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'INVALID_REQUEST',
                'message': 'Invalid user_id format or password does not meet requirements'
            }), 400
        
        user_id = data.get('user_id')
        password = data.get('password')
        
        # Validate user_id format
        if not user_id or not _is_valid_uuid(user_id):
            return jsonify({
                'error': 'INVALID_REQUEST',
                'message': 'Invalid user_id format or password does not meet requirements'
            }), 400
        
        # Validate password requirements
        if not password or not isinstance(password, str):
            return jsonify({
                'error': 'INVALID_REQUEST',
                'message': 'Invalid user_id format or password does not meet requirements'
            }), 400
        
        if len(password) < 8 or len(password) > 128:
            return jsonify({
                'error': 'INVALID_REQUEST',
                'message': 'Invalid user_id format or password does not meet requirements'
            }), 400
        
        # Hash the password
        password_hash = _hash_password_bcrypt(password)
        if not password_hash:
            return jsonify({
                'error': 'HASHING_FAILED',
                'message': 'Failed to hash password'
            }), 500
        
        # Insert into database
        try:
            query = text("""
                INSERT INTO f_ea5acd92__user_credentials (user_id, password_hash)
                VALUES (:user_id, :password_hash)
            """)
            
            result = db.session.execute(
                query,
                {'user_id': user_id, 'password_hash': password_hash}
            )
            db.session.commit()
            
            # Retrieve the created_at timestamp
            select_query = text("""
                SELECT created_at FROM f_ea5acd92__user_credentials
                WHERE user_id = :user_id
            """)
            row = db.session.execute(select_query, {'user_id': user_id}).fetchone()
            
            created_at = row[0] if row else datetime.utcnow()
            
            return jsonify({
                'user_id': user_id,
                'created_at': created_at.isoformat() + 'Z' if isinstance(created_at, datetime) else created_at
            }), 201
            
        except IntegrityError:
            db.session.rollback()
            return jsonify({
                'error': 'CREDENTIAL_EXISTS',
                'message': 'Credentials already exist for this user_id'
            }), 409
        except SQLAlchemyError:
            db.session.rollback()
            return jsonify({
                'error': 'HASHING_FAILED',
                'message': 'Failed to hash password'
            }), 500
            
    except Exception:
        return jsonify({
            'error': 'HASHING_FAILED',
            'message': 'Failed to hash password'
        }), 500


@blueprint.post('/api/capability_password_hashing_ea5acd92/credentials/verify')
def verify_password():
    """
    Retrieves the stored password hash for a user and compares it against a submitted plaintext password.
    
    This endpoint enables secure login authentication by comparing hashed values rather than
    storing or comparing plaintext passwords.
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'INVALID_REQUEST',
                'message': 'Invalid user_id format or missing password'
            }), 400
        
        user_id = data.get('user_id')
        password = data.get('password')
        
        # Validate user_id format
        if not user_id or not _is_valid_uuid(user_id):
            return jsonify({
                'error': 'INVALID_REQUEST',
                'message': 'Invalid user_id format or missing password'
            }), 400
        
        # Validate password presence
        if not password or not isinstance(password, str):
            return jsonify({
                'error': 'INVALID_REQUEST',
                'message': 'Invalid user_id format or missing password'
            }), 400
        
        if len(password) < 1 or len(password) > 128:
            return jsonify({
                'error': 'INVALID_REQUEST',
                'message': 'Invalid user_id format or missing password'
            }), 400
        
        # Retrieve password hash from database
        try:
            query = text("""
                SELECT password_hash FROM f_ea5acd92__user_credentials
                WHERE user_id = :user_id
            """)
            
            row = db.session.execute(query, {'user_id': user_id}).fetchone()
            
            if not row:
                return jsonify({
                    'error': 'CREDENTIAL_NOT_FOUND',
                    'message': 'No credentials found for this user_id'
                }), 404
            
            password_hash = row[0]
            
            # Verify the password
            verified = _verify_password_bcrypt(password, password_hash)
            
            return jsonify({
                'user_id': user_id,
                'verified': verified
            }), 200
            
        except SQLAlchemyError:
            return jsonify({
                'error': 'VERIFICATION_FAILED',
                'message': 'Failed to verify password'
            }), 500
            
    except Exception:
        return jsonify({
            'error': 'VERIFICATION_FAILED',
            'message': 'Failed to verify password'
        }), 500
