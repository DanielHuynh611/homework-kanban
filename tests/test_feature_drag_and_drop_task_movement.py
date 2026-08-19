"""Deterministic contract checks for Drag-and-drop task movement."""

from backend import create_app


def test_feature_routes_are_registered():
    app = create_app(testing=True)
    actual = {
        (rule.rule, method)
        for rule in app.url_map.iter_rules()
        for method in (rule.methods or set())
    }
    expected = (('/api/capability_drag_and_drop_task_movement_a0308110/cards/<homework_card_id>/status', 'PATCH'), ('/api/capability_drag_and_drop_task_movement_a0308110/cards/<homework_card_id>/status', 'GET'), ('/api/capability_drag_and_drop_task_movement_a0308110/cards/<homework_card_id>/status', 'POST'), ('/api/capability_drag_and_drop_task_movement_a0308110/cards/statuses', 'GET'))
    assert all(route in actual for route in expected)


def test_protected_routes_reject_missing_authentication():
    client = create_app(testing=True).test_client()
    response = client.patch('/api/capability_drag_and_drop_task_movement_a0308110/cards/test-id/status')
    assert response.status_code == 401
    response = client.get('/api/capability_drag_and_drop_task_movement_a0308110/cards/test-id/status')
    assert response.status_code == 401
    response = client.post('/api/capability_drag_and_drop_task_movement_a0308110/cards/test-id/status')
    assert response.status_code == 401
    response = client.get('/api/capability_drag_and_drop_task_movement_a0308110/cards/statuses')
    assert response.status_code == 401
