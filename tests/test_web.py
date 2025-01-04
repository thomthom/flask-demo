import pytest

from app import db
from tests.conftest import authenticated_user, create_user


@pytest.mark.usefixtures("db_ctx")
class TestWebRoutes:

    def test_index(self, client):
        response = client.get("/")
        assert b"Hello Flask Demo" in response.data

    def test_login(self, client):
        response = client.get("/login")
        assert b"Hello Flask Demo" in response.data

    def test_profile_not_authenticated(self, client):
        response = client.get("/profile")
        assert response.status_code == 302
        assert response.location == "/login?next=%2Fprofile"

    def test_profile_authenticated(self, app):
        # https://flask-sqlalchemy-lite.readthedocs.io/en/latest/testing/#testing-data-around-requests
        # User must have an id. Without committing it will be None.
        with app.app_context():
            test_user = create_user('test@example.com', 'password123')
            db.session.add(test_user)
            db.session.commit()
        # https://flask-login.readthedocs.io/en/latest/#automated-testing
        with app.test_client(user=test_user) as client:
            response = client.get("/profile")
            assert response.status_code == 200
            assert f"User: {test_user.name}" in response.text
