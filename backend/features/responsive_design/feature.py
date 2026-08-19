"""
Responsive Design Feature Module

This module implements viewport preferences and touch target configurations
for responsive design across desktop, tablet, and mobile devices.
"""

from flask import Blueprint, request, jsonify, g
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from datetime import datetime
import uuid
from functools import wraps

blueprint = Blueprint('capability_responsive_design_8e006bb8', __name__)


def get_db():
    """Get database connection from Flask g object."""
    from flask import current_app
    if 'db' not in g:
        g.db = current_app.config['DATABASE_ENGINE']
    return g.db


def require_auth(f):
    """Decorator to require authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(g, 'user_id') or g.user_id is None:
            return jsonify({
                'code': 'UNAUTHORIZED',
                'message': 'Authentication required'
            }), 401
        return f(*args, **kwargs)
    return decorated_function


def optional_auth(f):
    """Decorator for optional authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Authentication is optional, proceed regardless
        return f(*args, **kwargs)
    return decorated_function


@blueprint.route('/api/capability_responsive_design_8e006bb8/viewport-preferences', methods=['GET'])
@require_auth
def get_user_viewport_preferences():
    """
    Retrieves the authenticated user's saved viewport preferences for all device categories.
    """
    try:
        db = get_db()
        user_id = g.user_id
        
        query = text("""
            SELECT id, user_id, device_category, layout_mode, created_at, updated_at
            FROM f_8e006bb8__user_viewport_preferences
            WHERE user_id = :user_id
            ORDER BY device_category
        """)
        
        with db.connect() as conn:
            result = conn.execute(query, {'user_id': user_id})
            rows = result.fetchall()
        
        preferences = []
        for row in rows:
            preferences.append({
                'id': row[0],
                'user_id': row[1],
                'device_category': row[2],
                'layout_mode': row[3],
                'created_at': row[4].isoformat() if row[4] else None,
                'updated_at': row[5].isoformat() if row[5] else None
            })
        
        return jsonify({'preferences': preferences}), 200
        
    except SQLAlchemyError as e:
        return jsonify({
            'code': 'INTERNAL_ERROR',
            'message': 'Failed to retrieve viewport preferences'
        }), 500


@blueprint.route('/api/capability_responsive_design_8e006bb8/viewport-preferences', methods=['POST'])
@require_auth
def create_viewport_preference():
    """
    Creates a new viewport preference record for a device category.
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'code': 'INVALID_REQUEST',
                'message': 'Invalid device_category or layout_mode value'
            }), 400
        
        device_category = data.get('device_category')
        layout_mode = data.get('layout_mode')
        
        # Validate required fields
        if not device_category or not layout_mode:
            return jsonify({
                'code': 'INVALID_REQUEST',
                'message': 'Invalid device_category or layout_mode value'
            }), 400
        
        # Validate enum values
        valid_device_categories = ['desktop', 'tablet', 'mobile']
        valid_layout_modes = ['side_by_side', 'horizontal_scroll', 'vertical_stack', 'tabs']
        
        if device_category not in valid_device_categories or layout_mode not in valid_layout_modes:
            return jsonify({
                'code': 'INVALID_REQUEST',
                'message': 'Invalid device_category or layout_mode value'
            }), 400
        
        db = get_db()
        user_id = g.user_id
        preference_id = str(uuid.uuid4())
        
        # Check if preference already exists for this device category
        check_query = text("""
            SELECT id FROM f_8e006bb8__user_viewport_preferences
            WHERE user_id = :user_id AND device_category = :device_category
        """)
        
        with db.connect() as conn:
            result = conn.execute(check_query, {
                'user_id': user_id,
                'device_category': device_category
            })
            existing = result.fetchone()
            
            if existing:
                return jsonify({
                    'code': 'PREFERENCE_EXISTS',
                    'message': 'Viewport preference already exists for this device category'
                }), 409
            
            # Insert new preference
            insert_query = text("""
                INSERT INTO f_8e006bb8__user_viewport_preferences
                (id, user_id, device_category, layout_mode, created_at, updated_at)
                VALUES (:id, :user_id, :device_category, :layout_mode, :created_at, :updated_at)
            """)
            
            now = datetime.utcnow()
            conn.execute(insert_query, {
                'id': preference_id,
                'user_id': user_id,
                'device_category': device_category,
                'layout_mode': layout_mode,
                'created_at': now,
                'updated_at': now
            })
            conn.commit()
            
            # Fetch the created preference
            select_query = text("""
                SELECT id, user_id, device_category, layout_mode, created_at, updated_at
                FROM f_8e006bb8__user_viewport_preferences
                WHERE id = :id
            """)
            
            result = conn.execute(select_query, {'id': preference_id})
            row = result.fetchone()
        
        preference = {
            'id': row[0],
            'user_id': row[1],
            'device_category': row[2],
            'layout_mode': row[3],
            'created_at': row[4].isoformat() if row[4] else None,
            'updated_at': row[5].isoformat() if row[5] else None
        }
        
        return jsonify({'preference': preference}), 201
        
    except IntegrityError:
        return jsonify({
            'code': 'PREFERENCE_EXISTS',
            'message': 'Viewport preference already exists for this device category'
        }), 409
    except SQLAlchemyError as e:
        return jsonify({
            'code': 'INTERNAL_ERROR',
            'message': 'Failed to create viewport preference'
        }), 500


@blueprint.route('/api/capability_responsive_design_8e006bb8/viewport-preferences/<preference_id>', methods=['PATCH'])
@require_auth
def update_viewport_preference(preference_id):
    """
    Updates an existing viewport preference when a user changes their preferred layout mode.
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'code': 'INVALID_REQUEST',
                'message': 'Invalid layout_mode value'
            }), 400
        
        layout_mode = data.get('layout_mode')
        
        # Validate required field
        if not layout_mode:
            return jsonify({
                'code': 'INVALID_REQUEST',
                'message': 'Invalid layout_mode value'
            }), 400
        
        # Validate enum value
        valid_layout_modes = ['side_by_side', 'horizontal_scroll', 'vertical_stack', 'tabs']
        
        if layout_mode not in valid_layout_modes:
            return jsonify({
                'code': 'INVALID_REQUEST',
                'message': 'Invalid layout_mode value'
            }), 400
        
        db = get_db()
        user_id = g.user_id
        
        # Check if preference exists and belongs to user
        check_query = text("""
            SELECT user_id FROM f_8e006bb8__user_viewport_preferences
            WHERE id = :id
        """)
        
        with db.connect() as conn:
            result = conn.execute(check_query, {'id': preference_id})
            row = result.fetchone()
            
            if not row:
                return jsonify({
                    'code': 'NOT_FOUND',
                    'message': 'Viewport preference not found'
                }), 404
            
            if row[0] != user_id:
                return jsonify({
                    'code': 'FORBIDDEN',
                    'message': 'Cannot update another user\'s viewport preference'
                }), 403
            
            # Update preference
            update_query = text("""
                UPDATE f_8e006bb8__user_viewport_preferences
                SET layout_mode = :layout_mode, updated_at = :updated_at
                WHERE id = :id
            """)
            
            now = datetime.utcnow()
            conn.execute(update_query, {
                'id': preference_id,
                'layout_mode': layout_mode,
                'updated_at': now
            })
            conn.commit()
            
            # Fetch the updated preference
            select_query = text("""
                SELECT id, user_id, device_category, layout_mode, created_at, updated_at
                FROM f_8e006bb8__user_viewport_preferences
                WHERE id = :id
            """)
            
            result = conn.execute(select_query, {'id': preference_id})
            row = result.fetchone()
        
        preference = {
            'id': row[0],
            'user_id': row[1],
            'device_category': row[2],
            'layout_mode': row[3],
            'created_at': row[4].isoformat() if row[4] else None,
            'updated_at': row[5].isoformat() if row[5] else None
        }
        
        return jsonify({'preference': preference}), 200
        
    except SQLAlchemyError as e:
        return jsonify({
            'code': 'INTERNAL_ERROR',
            'message': 'Failed to update viewport preference'
        }), 500


@blueprint.route('/api/capability_responsive_design_8e006bb8/touch-target-configurations', methods=['GET'])
@optional_auth
def get_touch_target_configurations():
    """
    Retrieves active touch target size and spacing configurations.
    """
    try:
        device_category = request.args.get('device_category')
        element_type = request.args.get('element_type')
        
        # Validate enum values if provided
        if device_category:
            valid_device_categories = ['desktop', 'tablet', 'mobile']
            if device_category not in valid_device_categories:
                return jsonify({
                    'code': 'INVALID_REQUEST',
                    'message': 'Invalid device_category or element_type value'
                }), 400
        
        if element_type:
            valid_element_types = ['button', 'drag_handle', 'form_field', 'card', 'column_header']
            if element_type not in valid_element_types:
                return jsonify({
                    'code': 'INVALID_REQUEST',
                    'message': 'Invalid device_category or element_type value'
                }), 400
        
        db = get_db()
        
        # Build query with optional filters
        query_str = """
            SELECT id, device_category, element_type, minimum_width_px, 
                   minimum_height_px, minimum_spacing_px, is_active, created_at
            FROM f_8e006bb8__touch_target_configurations
            WHERE is_active = TRUE
        """
        params = {}
        
        if device_category:
            query_str += " AND device_category = :device_category"
            params['device_category'] = device_category
        
        if element_type:
            query_str += " AND element_type = :element_type"
            params['element_type'] = element_type
        
        query_str += " ORDER BY device_category, element_type"
        query = text(query_str)
        
        with db.connect() as conn:
            result = conn.execute(query, params)
            rows = result.fetchall()
        
        configurations = []
        for row in rows:
            configurations.append({
                'id': row[0],
                'device_category': row[1],
                'element_type': row[2],
                'minimum_width_px': row[3],
                'minimum_height_px': row[4],
                'minimum_spacing_px': row[5],
                'is_active': bool(row[6]),
                'created_at': row[7].isoformat() if row[7] else None
            })
        
        return jsonify({'configurations': configurations}), 200
        
    except SQLAlchemyError as e:
        return jsonify({
            'code': 'INTERNAL_ERROR',
            'message': 'Failed to retrieve touch target configurations'
        }), 500
