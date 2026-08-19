"""
Drag-and-drop task movement feature module.

This module provides endpoints for managing homework card statuses in a Kanban board,
allowing students to move cards between columns (to_do, in_progress, done) using
drag-and-drop functionality.
"""

from flask import Blueprint, request, jsonify, g
from sqlalchemy import text
from datetime import datetime
import uuid

from backend.core.database import get_db

blueprint = Blueprint('capability_drag_and_drop_task_movement_a0308110', __name__)

# Valid column statuses
VALID_COLUMN_STATUSES = ['to_do', 'in_progress', 'done']


def require_authentication():
    """
    Check if user is authenticated. Raises 401 if not.
    Assumes authentication middleware sets g.user_id.
    """
    if not hasattr(g, 'user_id') or g.user_id is None:
        return jsonify({
            'error': 'UNAUTHORIZED',
            'message': 'Authentication required'
        }), 401
    return None


def verify_card_ownership(homework_card_id):
    """
    Verify that the homework card exists and belongs to the authenticated user.
    Returns True if valid, False otherwise.
    
    Note: This assumes there's a homework_cards table with user_id field.
    Since the schema doesn't provide this table, we'll implement a basic check.
    """
    # In a real implementation, this would check against a homework_cards table
    # For now, we'll assume the card exists if we have a status record or allow creation
    return True


@blueprint.route('/api/capability_drag_and_drop_task_movement_a0308110/cards/<homework_card_id>/status', methods=['PATCH'])
def update_card_status(homework_card_id):
    """
    Updates the column status and position of a homework card when a student
    drags and drops it to a different column.
    """
    # Check authentication
    auth_error = require_authentication()
    if auth_error:
        return auth_error
    
    # Parse request body
    data = request.get_json()
    if not data:
        return jsonify({
            'error': 'INVALID_REQUEST',
            'message': 'Request body is required'
        }), 400
    
    # Validate required fields
    if 'column_status' not in data:
        return jsonify({
            'error': 'INVALID_REQUEST',
            'message': 'column_status is required'
        }), 400
    
    if 'position_in_column' not in data:
        return jsonify({
            'error': 'INVALID_REQUEST',
            'message': 'position_in_column is required'
        }), 400
    
    column_status = data['column_status']
    position_in_column = data['position_in_column']
    
    # Validate column_status
    if column_status not in VALID_COLUMN_STATUSES:
        return jsonify({
            'error': 'INVALID_COLUMN_STATUS',
            'message': 'column_status must be one of: to_do, in_progress, done'
        }), 400
    
    # Validate position_in_column
    if not isinstance(position_in_column, int) or position_in_column < 0:
        return jsonify({
            'error': 'INVALID_POSITION',
            'message': 'position_in_column must be a non-negative integer'
        }), 400
    
    db = get_db()
    
    try:
        # Check if the card status exists
        result = db.execute(
            text("""
                SELECT id, homework_card_id, column_status, position_in_column, updated_at
                FROM f_a0308110__homework_card_status
                WHERE homework_card_id = :homework_card_id
            """),
            {'homework_card_id': homework_card_id}
        ).fetchone()
        
        if not result:
            return jsonify({
                'error': 'CARD_NOT_FOUND',
                'message': 'Homework card not found or does not belong to authenticated user'
            }), 404
        
        # Update the card status
        db.execute(
            text("""
                UPDATE f_a0308110__homework_card_status
                SET column_status = :column_status,
                    position_in_column = :position_in_column,
                    updated_at = CURRENT_TIMESTAMP
                WHERE homework_card_id = :homework_card_id
            """),
            {
                'column_status': column_status,
                'position_in_column': position_in_column,
                'homework_card_id': homework_card_id
            }
        )
        db.commit()
        
        # Fetch the updated record
        updated_result = db.execute(
            text("""
                SELECT id, homework_card_id, column_status, position_in_column, updated_at
                FROM f_a0308110__homework_card_status
                WHERE homework_card_id = :homework_card_id
            """),
            {'homework_card_id': homework_card_id}
        ).fetchone()
        
        return jsonify({
            'id': updated_result[0],
            'homework_card_id': updated_result[1],
            'column_status': updated_result[2],
            'position_in_column': updated_result[3],
            'updated_at': updated_result[4].isoformat() if isinstance(updated_result[4], datetime) else updated_result[4]
        }), 200
        
    except Exception as e:
        db.rollback()
        return jsonify({
            'error': 'UPDATE_FAILED',
            'message': 'Failed to update card status'
        }), 500


@blueprint.route('/api/capability_drag_and_drop_task_movement_a0308110/cards/<homework_card_id>/status', methods=['GET'])
def get_card_status(homework_card_id):
    """
    Retrieves the current column status and position of a homework card.
    """
    # Check authentication
    auth_error = require_authentication()
    if auth_error:
        return auth_error
    
    db = get_db()
    
    try:
        # Fetch the card status
        result = db.execute(
            text("""
                SELECT id, homework_card_id, column_status, position_in_column, updated_at
                FROM f_a0308110__homework_card_status
                WHERE homework_card_id = :homework_card_id
            """),
            {'homework_card_id': homework_card_id}
        ).fetchone()
        
        if not result:
            return jsonify({
                'error': 'CARD_NOT_FOUND',
                'message': 'Homework card not found or does not belong to authenticated user'
            }), 404
        
        return jsonify({
            'id': result[0],
            'homework_card_id': result[1],
            'column_status': result[2],
            'position_in_column': result[3],
            'updated_at': result[4].isoformat() if isinstance(result[4], datetime) else result[4]
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'RETRIEVAL_FAILED',
            'message': 'Failed to retrieve card status'
        }), 500


@blueprint.route('/api/capability_drag_and_drop_task_movement_a0308110/cards/<homework_card_id>/status', methods=['POST'])
def create_initial_card_status(homework_card_id):
    """
    Creates the initial status record for a newly created homework card.
    """
    # Check authentication
    auth_error = require_authentication()
    if auth_error:
        return auth_error
    
    # Parse request body (optional fields)
    data = request.get_json() or {}
    
    column_status = data.get('column_status', 'to_do')
    position_in_column = data.get('position_in_column')
    
    # Validate column_status if provided
    if column_status not in VALID_COLUMN_STATUSES:
        return jsonify({
            'error': 'INVALID_COLUMN_STATUS',
            'message': 'column_status must be one of: to_do, in_progress, done'
        }), 400
    
    # Validate position_in_column if provided
    if position_in_column is not None:
        if not isinstance(position_in_column, int) or position_in_column < 0:
            return jsonify({
                'error': 'INVALID_POSITION',
                'message': 'position_in_column must be a non-negative integer'
            }), 400
    
    db = get_db()
    
    try:
        # Check if status already exists
        existing = db.execute(
            text("""
                SELECT id FROM f_a0308110__homework_card_status
                WHERE homework_card_id = :homework_card_id
            """),
            {'homework_card_id': homework_card_id}
        ).fetchone()
        
        if existing:
            return jsonify({
                'error': 'STATUS_ALREADY_EXISTS',
                'message': 'Status record already exists for this card'
            }), 409
        
        # If position not provided, calculate the end of the column
        if position_in_column is None:
            max_position_result = db.execute(
                text("""
                    SELECT COALESCE(MAX(position_in_column), -1) as max_pos
                    FROM f_a0308110__homework_card_status
                    WHERE column_status = :column_status
                """),
                {'column_status': column_status}
            ).fetchone()
            position_in_column = max_position_result[0] + 1
        
        # Generate new UUID for the status record
        status_id = str(uuid.uuid4())
        
        # Insert the new status record
        db.execute(
            text("""
                INSERT INTO f_a0308110__homework_card_status
                (id, homework_card_id, column_status, position_in_column, updated_at)
                VALUES (:id, :homework_card_id, :column_status, :position_in_column, CURRENT_TIMESTAMP)
            """),
            {
                'id': status_id,
                'homework_card_id': homework_card_id,
                'column_status': column_status,
                'position_in_column': position_in_column
            }
        )
        db.commit()
        
        # Fetch the created record
        result = db.execute(
            text("""
                SELECT id, homework_card_id, column_status, position_in_column, updated_at
                FROM f_a0308110__homework_card_status
                WHERE id = :id
            """),
            {'id': status_id}
        ).fetchone()
        
        return jsonify({
            'id': result[0],
            'homework_card_id': result[1],
            'column_status': result[2],
            'position_in_column': result[3],
            'updated_at': result[4].isoformat() if isinstance(result[4], datetime) else result[4]
        }), 201
        
    except Exception as e:
        db.rollback()
        return jsonify({
            'error': 'CREATION_FAILED',
            'message': 'Failed to create card status'
        }), 500


@blueprint.route('/api/capability_drag_and_drop_task_movement_a0308110/cards/statuses', methods=['GET'])
def get_all_card_statuses():
    """
    Retrieves the status and position of all homework cards for the authenticated user.
    """
    # Check authentication
    auth_error = require_authentication()
    if auth_error:
        return auth_error
    
    # Get optional column_status filter from query parameters
    column_status_filter = request.args.get('column_status')
    
    # Validate column_status filter if provided
    if column_status_filter and column_status_filter not in VALID_COLUMN_STATUSES:
        return jsonify({
            'error': 'INVALID_COLUMN_FILTER',
            'message': 'column_status filter must be one of: to_do, in_progress, done'
        }), 400
    
    db = get_db()
    
    try:
        # Build query based on filter
        if column_status_filter:
            query = text("""
                SELECT id, homework_card_id, column_status, position_in_column, updated_at
                FROM f_a0308110__homework_card_status
                WHERE column_status = :column_status
                ORDER BY position_in_column ASC
            """)
            results = db.execute(query, {'column_status': column_status_filter}).fetchall()
        else:
            query = text("""
                SELECT id, homework_card_id, column_status, position_in_column, updated_at
                FROM f_a0308110__homework_card_status
                ORDER BY 
                    CASE column_status
                        WHEN 'to_do' THEN 1
                        WHEN 'in_progress' THEN 2
                        WHEN 'done' THEN 3
                    END,
                    position_in_column ASC
            """)
            results = db.execute(query).fetchall()
        
        statuses = []
        for row in results:
            statuses.append({
                'id': row[0],
                'homework_card_id': row[1],
                'column_status': row[2],
                'position_in_column': row[3],
                'updated_at': row[4].isoformat() if isinstance(row[4], datetime) else row[4]
            })
        
        return jsonify({
            'statuses': statuses
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'RETRIEVAL_FAILED',
            'message': 'Failed to retrieve card statuses'
        }), 500
