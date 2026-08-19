"""Deterministic contract checks for Browser-based platform."""

from backend import create_app


def test_feature_routes_are_registered():
    app = create_app(testing=True)
    actual = {
        (rule.rule, method)
        for rule in app.url_map.iter_rules()
        for method in (rule.methods or set())
    }
    expected = (('/api/capability_browser_based_platform_b7688c8b/auth/register', 'POST'), ('/api/capability_browser_based_platform_b7688c8b/auth/login', 'POST'), ('/api/capability_browser_based_platform_b7688c8b/auth/validate', 'GET'), ('/api/capability_browser_based_platform_b7688c8b/auth/logout', 'POST'))
    assert all(route in actual for route in expected)


def test_protected_routes_reject_missing_authentication():
    client = create_app(testing=True).test_client()
    response = client.get('/api/capability_browser_based_platform_b7688c8b/auth/validate')
    assert response.status_code == 401
    response = client.post('/api/capability_browser_based_platform_b7688c8b/auth/logout')
    assert response.status_code == 401
