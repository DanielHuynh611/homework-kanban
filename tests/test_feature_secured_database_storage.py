"""Deterministic contract checks for Secured database storage."""

from backend import create_app


def test_feature_routes_are_registered():
    app = create_app(testing=True)
    actual = {
        (rule.rule, method)
        for rule in app.url_map.iter_rules()
        for method in (rule.methods or set())
    }
    expected = (('/api/capability_secured_database_storage_8df07551/users', 'POST'), ('/api/capability_secured_database_storage_8df07551/auth/login', 'POST'), ('/api/capability_secured_database_storage_8df07551/subjects', 'POST'), ('/api/capability_secured_database_storage_8df07551/subjects', 'GET'), ('/api/capability_secured_database_storage_8df07551/tasks', 'POST'), ('/api/capability_secured_database_storage_8df07551/tasks', 'GET'), ('/api/capability_secured_database_storage_8df07551/tasks/<task_id>/status', 'PATCH'))
    assert all(route in actual for route in expected)


def test_protected_routes_reject_missing_authentication():
    client = create_app(testing=True).test_client()
    response = client.post('/api/capability_secured_database_storage_8df07551/subjects')
    assert response.status_code == 401
    response = client.get('/api/capability_secured_database_storage_8df07551/subjects')
    assert response.status_code == 401
    response = client.post('/api/capability_secured_database_storage_8df07551/tasks')
    assert response.status_code == 401
    response = client.get('/api/capability_secured_database_storage_8df07551/tasks')
    assert response.status_code == 401
    response = client.patch('/api/capability_secured_database_storage_8df07551/tasks/test-id/status')
    assert response.status_code == 401
