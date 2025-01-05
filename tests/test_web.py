import pytest
from sqlalchemy import select

from tests.conftest import authenticated_user


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

    def test_profile_authenticated(self, app, test_user):
        with authenticated_user(app, test_user) as client:
            response = client.get("/profile")
            assert response.status_code == 200
            assert f"User: {test_user.name}" in response.text
