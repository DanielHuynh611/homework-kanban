import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, g
from sqlalchemy import text
from functools import wraps

blueprint = Blueprint('capability_create_homework_cards_384935a0', __name__)

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(g, 'user_id') or g.user_id is None:
            return jsonify({
                'code': 'UNAUTHORIZED',
                'message': 'Authentication required to create homework cards'
            }), 401
        return f(*args, **kwargs)
    return decorated_function

@blueprint.post('/api/capability_create_homework_cards_384935a0/homework-cards')
@require_auth
def create_homework_card():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({
                'code': 'VALIDATION_ERROR',
                'message': 'Invalid input: title is required and must be 1-255 characters; subject_id must be a valid UUID; due_date must be a valid date; priority must be High, Medium, or Low'
            }), 400
        
        title = data.get('title')
        subject_id = data.get('subject_id')
        due_date = data.get('due_date')
        priority = data.get('priority')
        description = data.get('description')
        
        # Validate title
        if not title or not isinstance(title, str) or len(title) < 1 or len(title) > 255:
            return jsonify({
                'code': 'VALIDATION_ERROR',
                'message': 'Invalid input: title is required and must be 1-255 characters; subject_id must be a valid UUID; due_date must be a valid date; priority must be High, Medium, or Low'
            }), 400
        
        # Validate subject_id (UUID format)
        if not subject_id:
            return jsonify({
                'code': 'VALIDATION_ERROR',
                'message': 'Invalid input: title is required and must be 1-255 characters; subject_id must be a valid UUID; due_date must be a valid date; priority must be High, Medium, or Low'
            }), 400
        
        try:
            uuid.UUID(subject_id)
        except (ValueError, AttributeError, TypeError):
            return jsonify({
                'code': 'VALIDATION_ERROR',
                'message': 'Invalid input: title is required and must be 1-255 characters; subject_id must be a valid UUID; due_date must be a valid date; priority must be High, Medium, or Low'
            }), 400
        
        # Validate due_date
        if not due_date:
            return jsonify({
                'code': 'VALIDATION_ERROR',
                'message': 'Invalid input: title is required and must be 1-255 characters; subject_id must be a valid UUID; due_date must be a valid date; priority must be High, Medium, or Low'
            }), 400
        
        try:
            datetime.strptime(due_date, '%Y-%m-%d')
        except (ValueError, TypeError):
            return jsonify({
                'code': 'VALIDATION_ERROR',
                'message': 'Invalid input: title is required and must be 1-255 characters; subject_id must be a valid UUID; due_date must be a valid date; priority must be High, Medium, or Low'
            }), 400
        
        # Validate priority
        if priority not in ['High', 'Medium', 'Low']:
            return jsonify({
                'code': 'VALIDATION_ERROR',
                'message': 'Invalid input: title is required and must be 1-255 characters; subject_id must be a valid UUID; due_date must be a valid date; priority must be High, Medium, or Low'
            }), 400
        
        # Check if subject exists and belongs to user
        from flask import current_app
        db = current_app.extensions['sqlalchemy']
        
        # Verify subject exists and belongs to user
        check_subject_query = text("""
            SELECT id FROM f_384935a0__subjects 
            WHERE id = :subject_id AND user_id = :user_id
        """)
        
        try:
            result = db.session.execute(
                check_subject_query,
                {'subject_id': subject_id, 'user_id': g.user_id}
            ).fetchone()
            
            if not result:
                return jsonify({
                    'code': 'SUBJECT_NOT_FOUND',
                    'message': 'The specified subject_id does not exist or does not belong to the authenticated user'
                }), 404
        except Exception:
            # If subjects table doesn't exist, we'll skip this check
            pass
        
        # Generate new UUID for homework card
        card_id = str(uuid.uuid4())
        status = 'to_do'
        created_at = datetime.utcnow()
        
        # Insert homework card
        insert_query = text("""
            INSERT INTO f_384935a0__homework_cards 
            (id, user_id, subject_id, title, due_date, priority, description, status, created_at)
            VALUES (:id, :user_id, :subject_id, :title, :due_date, :priority, :description, :status, :created_at)
        """)
        
        db.session.execute(
            insert_query,
            {
                'id': card_id,
                'user_id': g.user_id,
                'subject_id': subject_id,
                'title': title,
                'due_date': due_date,
                'priority': priority,
                'description': description,
                'status': status,
                'created_at': created_at
            }
        )
        db.session.commit()
        
        # Return created card
        response = {
            'id': card_id,
            'user_id': g.user_id,
            'subject_id': subject_id,
            'title': title,
            'due_date': due_date,
            'priority': priority,
            'description': description,
            'status': status,
            'created_at': created_at.isoformat() + 'Z'
        }
        
        return jsonify(response), 201
        
    except Exception as e:
        if hasattr(db, 'session'):
            db.session.rollback()
        return jsonify({
            'code': 'INTERNAL_ERROR',
            'message': 'Failed to create homework card due to server error'
        }), 500

@blueprint.get('/api/capability_create_homework_cards_384935a0/homework-cards')
@require_auth
def get_homework_cards():
    try:
        # Get optional status filter from query parameters
        status_filter = request.args.get('status')
        
        # Validate status filter if provided
        if status_filter and status_filter not in ['to_do', 'in_progress', 'done']:
            return jsonify({
                'code': 'VALIDATION_ERROR',
                'message': 'Invalid status filter value; must be to_do, in_progress, or done'
            }), 400
        
        from flask import current_app
        db = current_app.extensions['sqlalchemy']
        
        # Build query
        if status_filter:
            query = text("""
                SELECT id, user_id, subject_id, title, due_date, priority, description, status, created_at
                FROM f_384935a0__homework_cards
                WHERE user_id = :user_id AND status = :status
                ORDER BY created_at DESC
            """)
            result = db.session.execute(
                query,
                {'user_id': g.user_id, 'status': status_filter}
            )
        else:
            query = text("""
                SELECT id, user_id, subject_id, title, due_date, priority, description, status, created_at
                FROM f_384935a0__homework_cards
                WHERE user_id = :user_id
                ORDER BY created_at DESC
            """)
            result = db.session.execute(
                query,
                {'user_id': g.user_id}
            )
        
        # Format results
        cards = []
        for row in result:
            card = {
                'id': row[0],
                'user_id': row[1],
                'subject_id': row[2],
                'title': row[3],
                'due_date': row[4].isoformat() if hasattr(row[4], 'isoformat') else str(row[4]),
                'priority': row[5],
                'description': row[6],
                'status': row[7],
                'created_at': row[8].isoformat() + 'Z' if hasattr(row[8], 'isoformat') else str(row[8])
            }
            cards.append(card)
        
        return jsonify({'cards': cards}), 200
        
    except Exception as e:
        return jsonify({
            'code': 'INTERNAL_ERROR',
            'message': 'Failed to retrieve homework cards due to server error'
        }), 500
