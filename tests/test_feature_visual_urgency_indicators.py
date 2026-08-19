"""Deterministic contract checks for Visual urgency indicators."""

from backend import create_app


def test_feature_routes_are_registered():
    app = create_app(testing=True)
    actual = {
        (rule.rule, method)
        for rule in app.url_map.iter_rules()
        for method in (rule.methods or set())
    }
    expected = (('/api/capability_visual_urgency_indicators_79524665/cards/:card_id/urgency', 'GET'), ('/api/capability_visual_urgency_indicators_79524665/cards/urgency/batch', 'POST'))
    assert all(route in actual for route in expected)


def test_protected_routes_reject_missing_authentication():
    client = create_app(testing=True).test_client()
    response = client.get('/api/capability_visual_urgency_indicators_79524665/cards/:card_id/urgency')
    assert response.status_code == 401
    response = client.post('/api/capability_visual_urgency_indicators_79524665/cards/urgency/batch')
    assert response.status_code == 401
