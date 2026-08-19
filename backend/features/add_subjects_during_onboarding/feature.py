"""
Flask Blueprint module for adding subjects during student onboarding.

This module provides endpoints for students to create and list their subjects
during the initial setup process.
"""

from flask import Blueprint, request, jsonify, g
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import uuid

from backend.core.auth import require_auth
from backend.core.database import get_db_connection


def get_authenticated_user_id():
    """Return the subject established by the shared bearer-token decorator."""
    identity = getattr(g, "identity", None) or {}
    return identity.get("sub")

blueprint = Blueprint('capability_add_subjects_during_onboarding_c90dae67', __name__)


@blueprint.post('/api/capability_add_subjects_during_onboarding_c90dae67/subjects')
@require_auth
def create_subject():
    """
    Creates a new subject record for the authenticated student during onboarding.
    
    Stores the subject name so it can appear as an option when creating homework cards.
    """
    try:
        # Get authenticated student ID
        student_id = get_authenticated_user_id()
        if not student_id:
            return jsonify({
                'code': 'UNAUTHORIZED',
                'message': 'Authentication required'
            }), 401
        
        # Parse request body
        data = request.get_json()
        if not data:
            return jsonify({
                'code': 'INVALID_SUBJECT_NAME',
                'message': 'Subject name must be between 1 and 100 characters'
            }), 400
        
        subject_name = data.get('name', '').strip()
        
        # Validate subject name
        if not subject_name or len(subject_name) < 1 or len(subject_name) > 100:
            return jsonify({
                'code': 'INVALID_SUBJECT_NAME',
                'message': 'Subject name must be between 1 and 100 characters'
            }), 400
        
        # Generate UUID and timestamp
        subject_id = str(uuid.uuid4())
        created_at = datetime.utcnow()
        
        # Insert into database
        conn = get_db_connection()
        try:
            query = text("""
                INSERT INTO f_c90dae67__subjects (id, student_id, name, created_at)
                VALUES (:id, :student_id, :name, :created_at)
            """)
            conn.execute(query, {
                'id': subject_id,
                'student_id': student_id,
                'name': subject_name,
                'created_at': created_at
            })
            conn.commit()
        except SQLAlchemyError as e:
            conn.rollback()
            return jsonify({
                'code': 'INTERNAL_ERROR',
                'message': 'Failed to create subject'
            }), 500
        finally:
            conn.close()
        
        # Return success response
        return jsonify({
            'id': subject_id,
            'name': subject_name,
            'student_id': student_id,
            'created_at': created_at.isoformat() + 'Z'
        }), 201
        
    except Exception as e:
        return jsonify({
            'code': 'INTERNAL_ERROR',
            'message': 'Failed to create subject'
        }), 500


@blueprint.get('/api/capability_add_subjects_during_onboarding_c90dae67/subjects')
@require_auth
def list_subjects():
    """
    Retrieves all subjects for the authenticated student.
    
    Returns subjects so they can be displayed as options when creating homework cards.
    """
    try:
        # Get authenticated student ID
        student_id = get_authenticated_user_id()
        if not student_id:
            return jsonify({
                'code': 'UNAUTHORIZED',
                'message': 'Authentication required'
            }), 401
        
        # Query database for subjects
        conn = get_db_connection()
        try:
            query = text("""
                SELECT id, student_id, name, created_at
                FROM f_c90dae67__subjects
                WHERE student_id = :student_id
                ORDER BY created_at ASC
            """)
            result = conn.execute(query, {'student_id': student_id})
            rows = result.fetchall()
        except SQLAlchemyError as e:
            return jsonify({
                'code': 'INTERNAL_ERROR',
                'message': 'Failed to retrieve subjects'
            }), 500
        finally:
            conn.close()
        
        # Format response
        subjects = []
        for row in rows:
            subjects.append({
                'id': row[0],
                'student_id': row[1],
                'name': row[2],
                'created_at': row[3].isoformat() + 'Z' if isinstance(row[3], datetime) else row[3]
            })
        
        return jsonify({
            'subjects': subjects
        }), 200
        
    except Exception as e:
        return jsonify({
            'code': 'INTERNAL_ERROR',
            'message': 'Failed to retrieve subjects'
        }), 500
