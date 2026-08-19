import re
import uuid
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import os

blueprint = Blueprint('capability_account_creation_40702744', __name__)

# Database connection
def get_db_connection():
    db_url = os.environ.get('DATABASE_URL', 'mysql+pymysql://user:password@localhost/db')
    engine = create_engine(db_url, pool_pre_ping=True)
    return engine

# Email validation helper
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# JWT secret key
JWT_SECRET = os.environ.get('JWT_SECRET', 'default-secret-key-change-in-production')

@blueprint.post('/api/capability_account_creation_40702744/accounts')
def create_account():
    """Creates a new student account by validating email format and password minimum length, 
    hashing the password, and storing the account credentials in the database. 
    Returns the created account ID on success."""
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'INVALID_EMAIL_FORMAT',
                'message': 'Email address format is invalid'
            }), 400
        
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        # Validate email format
        if not email or not is_valid_email(email):
            return jsonify({
                'error': 'INVALID_EMAIL_FORMAT',
                'message': 'Email address format is invalid'
            }), 400
        
        # Validate email length
        if len(email) < 3 or len(email) > 255:
            return jsonify({
                'error': 'INVALID_EMAIL_FORMAT',
                'message': 'Email address format is invalid'
            }), 400
        
        # Validate password length
        if not password or len(password) < 8:
            return jsonify({
                'error': 'PASSWORD_TOO_SHORT',
                'message': 'Password must be at least 8 characters long'
            }), 400
        
        if len(password) > 128:
            return jsonify({
                'error': 'PASSWORD_TOO_SHORT',
                'message': 'Password must be at least 8 characters long'
            }), 400
        
        # Generate account ID and hash password
        account_id = str(uuid.uuid4())
        password_hash = generate_password_hash(password)
        
        # Insert into database
        engine = get_db_connection()
        with engine.connect() as conn:
            # Check if email already exists
            check_query = text("""
                SELECT id FROM f_40702744__accounts WHERE email = :email
            """)
            result = conn.execute(check_query, {'email': email})
            if result.fetchone():
                return jsonify({
                    'error': 'EMAIL_ALREADY_EXISTS',
                    'message': 'An account with this email address already exists'
                }), 409
            
            # Insert new account
            insert_query = text("""
                INSERT INTO f_40702744__accounts (id, email, password_hash, created_at, updated_at)
                VALUES (:id, :email, :password_hash, :created_at, :updated_at)
            """)
            
            created_at = datetime.utcnow()
            conn.execute(insert_query, {
                'id': account_id,
                'email': email,
                'password_hash': password_hash,
                'created_at': created_at,
                'updated_at': created_at
            })
            conn.commit()
        
        return jsonify({
            'id': account_id,
            'email': email,
            'created_at': created_at.isoformat() + 'Z'
        }), 201
        
    except IntegrityError:
        return jsonify({
            'error': 'EMAIL_ALREADY_EXISTS',
            'message': 'An account with this email address already exists'
        }), 409
    except SQLAlchemyError:
        return jsonify({
            'error': 'ACCOUNT_CREATION_FAILED',
            'message': 'Failed to create account due to server error'
        }), 500
    except Exception:
        return jsonify({
            'error': 'ACCOUNT_CREATION_FAILED',
            'message': 'Failed to create account due to server error'
        }), 500


@blueprint.post('/api/capability_account_creation_40702744/auth/login')
def login():
    """Authenticates a student by verifying their email and password against stored credentials. 
    Returns an authentication token on success that grants access to their personal homework board."""
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'MISSING_CREDENTIALS',
                'message': 'Email and password are required'
            }), 400
        
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        # Validate credentials are provided
        if not email or not password:
            return jsonify({
                'error': 'MISSING_CREDENTIALS',
                'message': 'Email and password are required'
            }), 400
        
        # Query database for account
        engine = get_db_connection()
        with engine.connect() as conn:
            query = text("""
                SELECT id, email, password_hash 
                FROM f_40702744__accounts 
                WHERE email = :email
            """)
            result = conn.execute(query, {'email': email})
            account = result.fetchone()
        
        # Check if account exists and password matches
        if not account or not check_password_hash(account[2], password):
            return jsonify({
                'error': 'INVALID_CREDENTIALS',
                'message': 'Email or password is incorrect'
            }), 401
        
        # Generate JWT token
        token_payload = {
            'account_id': account[0],
            'email': account[1],
            'exp': datetime.utcnow() + timedelta(days=7)
        }
        token = jwt.encode(token_payload, JWT_SECRET, algorithm='HS256')
        
        return jsonify({
            'token': token,
            'account_id': account[0],
            'email': account[1]
        }), 200
        
    except SQLAlchemyError:
        return jsonify({
            'error': 'LOGIN_FAILED',
            'message': 'Failed to authenticate due to server error'
        }), 500
    except Exception:
        return jsonify({
            'error': 'LOGIN_FAILED',
            'message': 'Failed to authenticate due to server error'
        }), 500
