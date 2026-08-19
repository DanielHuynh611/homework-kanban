"""Deterministic contract checks for Three-column Kanban board."""

from backend import create_app


def test_feature_routes_are_registered():
    app = create_app(testing=True)
    actual = {
        (rule.rule, method)
        for rule in app.url_map.iter_rules()
        for method in (rule.methods or set())
    }
    expected = (('/api/capability_three_column_kanban_board_7897884e/kanban/board', 'GET'), ('/api/capability_three_column_kanban_board_7897884e/kanban/card-status', 'POST'), ('/api/capability_three_column_kanban_board_7897884e/kanban/card-status/<status_id>/move', 'PATCH'))
    assert all(route in actual for route in expected)


def test_protected_routes_reject_missing_authentication():
    client = create_app(testing=True).test_client()
    response = client.get('/api/capability_three_column_kanban_board_7897884e/kanban/board')
    assert response.status_code == 401
    response = client.post('/api/capability_three_column_kanban_board_7897884e/kanban/card-status')
    assert response.status_code == 401
    response = client.patch('/api/capability_three_column_kanban_board_7897884e/kanban/card-status/test-id/move')
    assert response.status_code == 401
