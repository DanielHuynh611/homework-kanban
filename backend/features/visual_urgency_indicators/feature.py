"""
Visual urgency indicators feature module.

This module computes urgency classifications for homework cards based on their due dates.
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timezone, timedelta
from functools import wraps

blueprint = Blueprint('capability_visual_urgency_indicators_79524665', __name__)


def require_auth(f):
    """Decorator to require authentication for endpoints."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for authentication token in Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({
                'error': 'UNAUTHORIZED',
                'message': 'Authentication required to compute card urgency'
            }), 401
        return f(*args, **kwargs)
    return decorated_function


def parse_iso_datetime(date_string):
    """
    Parse an ISO 8601 date-time string.
    
    Args:
        date_string: ISO 8601 formatted date-time string
        
    Returns:
        datetime object with timezone info
        
    Raises:
        ValueError: If the date string is invalid
    """
    try:
        # Try parsing with timezone info
        if date_string.endswith('Z'):
            date_string = date_string[:-1] + '+00:00'
        dt = datetime.fromisoformat(date_string)
        # Ensure timezone aware
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, AttributeError):
        raise ValueError(f"Invalid ISO 8601 date-time string: {date_string}")


def compute_urgency_level(due_date, current_time):
    """
    Compute the urgency level for a card based on its due date.
    
    Args:
        due_date: datetime object representing the due date
        current_time: datetime object representing the current time
        
    Returns:
        str: One of 'overdue', 'due_today', 'due_soon', or 'normal'
    """
    # Ensure both datetimes are timezone-aware
    if due_date.tzinfo is None:
        due_date = due_date.replace(tzinfo=timezone.utc)
    if current_time.tzinfo is None:
        current_time = current_time.replace(tzinfo=timezone.utc)
    
    # Calculate the difference
    time_diff = due_date - current_time
    
    # Overdue: due date is in the past
    if time_diff.total_seconds() < 0:
        return 'overdue'
    
    # Get date components for "today" comparison
    current_date = current_time.date()
    due_date_only = due_date.date()
    
    # Due today: due date is today
    if due_date_only == current_date:
        return 'due_today'
    
    # Due soon: due date is within 2-3 days (more than today, up to 3 days)
    days_until_due = (due_date_only - current_date).days
    if 1 <= days_until_due <= 3:
        return 'due_soon'
    
    # Normal: due date is more than 3 days away
    return 'normal'


@blueprint.route(
    '/api/capability_visual_urgency_indicators_79524665/cards/:card_id/urgency',
    defaults={'card_id': ':card_id'},
    methods=['GET'],
)
@blueprint.route('/api/capability_visual_urgency_indicators_79524665/cards/<card_id>/urgency', methods=['GET'])
@require_auth
def compute_card_urgency(card_id):
    """
    Compute the urgency classification for a single homework card.
    
    Args:
        card_id: The homework card ID from the URL path
        
    Query Parameters:
        due_date: The due date of the homework card (ISO 8601 format)
        
    Returns:
        JSON response with urgency level and metadata
    """
    # Get due_date from query parameters
    due_date_str = request.args.get('due_date')
    
    if not due_date_str:
        return jsonify({
            'error': 'INVALID_DUE_DATE',
            'message': 'The provided due_date is not a valid ISO 8601 date-time string'
        }), 400
    
    # Parse the due date
    try:
        due_date = parse_iso_datetime(due_date_str)
    except ValueError:
        return jsonify({
            'error': 'INVALID_DUE_DATE',
            'message': 'The provided due_date is not a valid ISO 8601 date-time string'
        }), 400
    
    # Get current server time
    current_time = datetime.now(timezone.utc)
    
    # Compute urgency level
    urgency_level = compute_urgency_level(due_date, current_time)
    
    # Return response
    return jsonify({
        'card_id': card_id,
        'urgency_level': urgency_level,
        'computed_at': current_time.isoformat()
    }), 200


@blueprint.route('/api/capability_visual_urgency_indicators_79524665/cards/urgency/batch', methods=['POST'])
@require_auth
def compute_batch_urgency():
    """
    Compute urgency classifications for multiple homework cards in a single request.
    
    Request Body:
        {
            "cards": [
                {
                    "card_id": "string",
                    "due_date": "ISO 8601 date-time string"
                },
                ...
            ]
        }
        
    Returns:
        JSON response with urgency levels for all cards
    """
    # Get request data
    data = request.get_json()
    
    if not data:
        return jsonify({
            'error': 'INVALID_REQUEST',
            'message': 'Request must contain a cards array with at least one card'
        }), 400
    
    cards = data.get('cards')
    
    # Validate cards array
    if not cards or not isinstance(cards, list) or len(cards) == 0:
        return jsonify({
            'error': 'INVALID_REQUEST',
            'message': 'Request must contain a cards array with at least one card'
        }), 400
    
    # Check batch size limit
    if len(cards) > 100:
        return jsonify({
            'error': 'BATCH_SIZE_EXCEEDED',
            'message': 'Maximum 100 cards allowed per batch request'
        }), 400
    
    # Get current server time
    current_time = datetime.now(timezone.utc)
    
    # Process each card
    urgencies = []
    for card in cards:
        # Validate card structure
        if not isinstance(card, dict):
            return jsonify({
                'error': 'INVALID_REQUEST',
                'message': 'Request must contain a cards array with at least one card'
            }), 400
        
        card_id = card.get('card_id')
        due_date_str = card.get('due_date')
        
        if not card_id or not due_date_str:
            return jsonify({
                'error': 'INVALID_REQUEST',
                'message': 'Request must contain a cards array with at least one card'
            }), 400
        
        # Parse the due date
        try:
            due_date = parse_iso_datetime(due_date_str)
        except ValueError:
            return jsonify({
                'error': 'INVALID_DUE_DATE',
                'message': 'One or more cards contain invalid due_date format'
            }), 400
        
        # Compute urgency level
        urgency_level = compute_urgency_level(due_date, current_time)
        
        urgencies.append({
            'card_id': card_id,
            'urgency_level': urgency_level
        })
    
    # Return response
    return jsonify({
        'urgencies': urgencies,
        'computed_at': current_time.isoformat()
    }), 200
