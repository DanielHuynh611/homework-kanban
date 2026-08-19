"""Deterministic contract checks for Create homework cards."""

from backend import create_app


def test_feature_routes_are_registered():
    app = create_app(testing=True)
    actual = {
        (rule.rule, method)
        for rule in app.url_map.iter_rules()
        for method in (rule.methods or set())
    }
    expected = (('/api/capability_create_homework_cards_384935a0/homework-cards', 'POST'), ('/api/capability_create_homework_cards_384935a0/homework-cards', 'GET'))
    assert all(route in actual for route in expected)


def test_protected_routes_reject_missing_authentication():
    client = create_app(testing=True).test_client()
    response = client.post('/api/capability_create_homework_cards_384935a0/homework-cards')
    assert response.status_code == 401
    response = client.get('/api/capability_create_homework_cards_384935a0/homework-cards')
    assert response.status_code == 401
