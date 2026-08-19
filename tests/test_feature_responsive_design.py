"""Deterministic contract checks for Responsive design."""

from backend import create_app


def test_feature_routes_are_registered():
    app = create_app(testing=True)
    actual = {
        (rule.rule, method)
        for rule in app.url_map.iter_rules()
        for method in (rule.methods or set())
    }
    expected = (('/api/capability_responsive_design_8e006bb8/viewport-preferences', 'GET'), ('/api/capability_responsive_design_8e006bb8/viewport-preferences', 'POST'), ('/api/capability_responsive_design_8e006bb8/viewport-preferences/<preference_id>', 'PATCH'), ('/api/capability_responsive_design_8e006bb8/touch-target-configurations', 'GET'))
    assert all(route in actual for route in expected)


def test_protected_routes_reject_missing_authentication():
    client = create_app(testing=True).test_client()
    response = client.get('/api/capability_responsive_design_8e006bb8/viewport-preferences')
    assert response.status_code == 401
    response = client.post('/api/capability_responsive_design_8e006bb8/viewport-preferences')
    assert response.status_code == 401
    response = client.patch('/api/capability_responsive_design_8e006bb8/viewport-preferences/test-id')
    assert response.status_code == 401
