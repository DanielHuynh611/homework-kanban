import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, g
from sqlalchemy import text, and_
from functools import wraps

blueprint = Blueprint('capability_three_column_kanban_board_7897884e', __name__)

def get_db():
    """Get database connection from Flask g object"""
    from flask import current_app
    if 'db' not in g:
        g.db = current_app.config['DATABASE_ENGINE']
    return g.db

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(g, 'user_id') or g.user_id is None:
            return jsonify({'code': 'UNAUTHORIZED', 'message': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

@blueprint.get('/api/capability_three_column_kanban_board_7897884e/kanban/board')
@require_auth
def get_kanban_board():
    """Retrieves all homework card statuses for the authenticated student, organized by column"""
    try:
        db = get_db()
        user_id = g.user_id
        
        query = text("""
            SELECT id, homework_card_id, column_name, position, updated_at
            FROM f_7897884e__homework_card_status
            WHERE user_id = :user_id
            ORDER BY column_name, position
        """)
        
        with db.connect() as conn:
            result = conn.execute(query, {'user_id': user_id})
            rows = result.fetchall()
        
        # Organize cards by column
        columns_data = {
            'to_do': {'name': 'to_do', 'label': 'To Do', 'cards': []},
            'in_progress': {'name': 'in_progress', 'label': 'In Progress', 'cards': []},
            'done': {'name': 'done', 'label': 'Done', 'cards': []}
        }
        
        for row in rows:
            card = {
                'status_id': row[0],
                'homework_card_id': row[1],
                'position': row[3],
                'updated_at': row[4].isoformat() if isinstance(row[4], datetime) else row[4]
            }
            columns_data[row[2]]['cards'].append(card)
        
        # Build response in order
        columns = [
            columns_data['to_do'],
            columns_data['in_progress'],
            columns_data['done']
        ]
        
        return jsonify({'columns': columns}), 200
        
    except Exception as e:
        return jsonify({'code': 'INTERNAL_ERROR', 'message': 'Failed to retrieve board data'}), 500

@blueprint.post('/api/capability_three_column_kanban_board_7897884e/kanban/card-status')
@require_auth
def create_card_status():
    """Creates a new status record for a homework card, defaulting to the To Do column"""
    try:
        data = request.get_json()
        
        if not data or 'homework_card_id' not in data:
            return jsonify({'code': 'INVALID_REQUEST', 'message': 'homework_card_id is required and must be a valid UUID'}), 400
        
        homework_card_id = data['homework_card_id']
        
        # Validate UUID format
        try:
            uuid.UUID(homework_card_id)
        except (ValueError, AttributeError):
            return jsonify({'code': 'INVALID_REQUEST', 'message': 'homework_card_id is required and must be a valid UUID'}), 400
        
        db = get_db()
        user_id = g.user_id
        
        # Check for duplicate
        check_query = text("""
            SELECT id FROM f_7897884e__homework_card_status
            WHERE homework_card_id = :homework_card_id AND user_id = :user_id
        """)
        
        with db.connect() as conn:
            result = conn.execute(check_query, {'homework_card_id': homework_card_id, 'user_id': user_id})
            if result.fetchone():
                return jsonify({'code': 'DUPLICATE_STATUS', 'message': 'Status record already exists for this homework card'}), 409
        
        # Get next position in to_do column
        position_query = text("""
            SELECT COALESCE(MAX(position), -1) + 1 as next_position
            FROM f_7897884e__homework_card_status
            WHERE user_id = :user_id AND column_name = 'to_do'
        """)
        
        with db.connect() as conn:
            result = conn.execute(position_query, {'user_id': user_id})
            next_position = result.fetchone()[0]
        
        # Create new status record
        status_id = str(uuid.uuid4())
        updated_at = datetime.utcnow()
        
        insert_query = text("""
            INSERT INTO f_7897884e__homework_card_status
            (id, homework_card_id, user_id, column_name, position, updated_at)
            VALUES (:id, :homework_card_id, :user_id, :column_name, :position, :updated_at)
        """)
        
        with db.connect() as conn:
            conn.execute(insert_query, {
                'id': status_id,
                'homework_card_id': homework_card_id,
                'user_id': user_id,
                'column_name': 'to_do',
                'position': next_position,
                'updated_at': updated_at
            })
            conn.commit()
        
        return jsonify({
            'id': status_id,
            'homework_card_id': homework_card_id,
            'user_id': user_id,
            'column_name': 'to_do',
            'position': next_position,
            'updated_at': updated_at.isoformat()
        }), 201
        
    except Exception as e:
        if 'DUPLICATE_STATUS' in str(e) or 'INVALID_REQUEST' in str(e):
            raise
        return jsonify({'code': 'INTERNAL_ERROR', 'message': 'Failed to create card status'}), 500

@blueprint.patch('/api/capability_three_column_kanban_board_7897884e/kanban/card-status/<status_id>/move')
@require_auth
def move_card(status_id):
    """Updates a homework card's column and position when the student drags it"""
    try:
        data = request.get_json()
        
        if not data or 'column_name' not in data or 'position' not in data:
            return jsonify({'code': 'INVALID_REQUEST', 'message': 'column_name must be one of: to_do, in_progress, done; position must be >= 0'}), 400
        
        column_name = data['column_name']
        position = data['position']
        
        # Validate column_name
        if column_name not in ['to_do', 'in_progress', 'done']:
            return jsonify({'code': 'INVALID_REQUEST', 'message': 'column_name must be one of: to_do, in_progress, done; position must be >= 0'}), 400
        
        # Validate position
        if not isinstance(position, int) or position < 0:
            return jsonify({'code': 'INVALID_REQUEST', 'message': 'column_name must be one of: to_do, in_progress, done; position must be >= 0'}), 400
        
        db = get_db()
        user_id = g.user_id
        
        # Check if status exists and belongs to user
        check_query = text("""
            SELECT homework_card_id, user_id
            FROM f_7897884e__homework_card_status
            WHERE id = :status_id
        """)
        
        with db.connect() as conn:
            result = conn.execute(check_query, {'status_id': status_id})
            row = result.fetchone()
            
            if not row:
                return jsonify({'code': 'NOT_FOUND', 'message': 'Card status not found'}), 404
            
            homework_card_id = row[0]
            card_user_id = row[1]
            
            if card_user_id != user_id:
                return jsonify({'code': 'FORBIDDEN', 'message': 'Cannot move another user\'s card'}), 403
        
        # Update the card
        updated_at = datetime.utcnow()
        
        update_query = text("""
            UPDATE f_7897884e__homework_card_status
            SET column_name = :column_name, position = :position, updated_at = :updated_at
            WHERE id = :status_id
        """)
        
        with db.connect() as conn:
            conn.execute(update_query, {
                'column_name': column_name,
                'position': position,
                'updated_at': updated_at,
                'status_id': status_id
            })
            conn.commit()
        
        return jsonify({
            'id': status_id,
            'homework_card_id': homework_card_id,
            'user_id': user_id,
            'column_name': column_name,
            'position': position,
            'updated_at': updated_at.isoformat()
        }), 200
        
    except Exception as e:
        if any(code in str(e) for code in ['INVALID_REQUEST', 'NOT_FOUND', 'FORBIDDEN']):
            raise
        return jsonify({'code': 'INTERNAL_ERROR', 'message': 'Failed to move card'}), 500
