import pytest
from sqlalchemy import select

from app import db
from app.models import User
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

    def test_session(self, client):
        with client.session_transaction() as session:
            session['value'] = 42
        with client.session_transaction() as session:
            assert session['value'] == 42

    def test_session_user(self, app, client):
        with app.app_context():
            test_user = create_user('test@example.com', 'password123')
            db.session.add(test_user)
            db.session.commit()
            user_id = test_user.id
        with client.session_transaction() as session:
            session['user_id2'] = test_user.id
            session['user_id'] = test_user.get_id()
        with client.session_transaction() as session:
            assert session['user_id2'] == test_user.id
            assert session['user_id'] == test_user.get_id()

    def test_session_user2(self, app, client):
        with app.app_context():
            test_user = create_user('test@example.com', 'password123')
            db.session.add(test_user)
            db.session.commit()
            user_id = test_user.id
        with client.session_transaction() as session:
            session['user_id'] = user_id
        with client.session_transaction() as session:
            assert session['user_id'] == user_id

    def test_profile_auth(self, app, client):
        with app.app_context():
            test_user = create_user('test@example.com', 'password123')
            db.session.add(test_user)
            db.session.commit()
            user_id = test_user.id
        with client.session_transaction() as session:
            session['_user_id'] = user_id
            session['_fresh'] = True
        with app.test_client() as client:
            with client.session_transaction() as session:
                assert session['_user_id'] == user_id
                assert session['_fresh'] == True
            response = client.get("/profile")
            assert response.status_code == 200
            assert f"User: {test_user.name}" in response.text

    def test_profile_auth2(self, app):
        with app.app_context():
            test_user = create_user('test@example.com', 'password123')
            db.session.add(test_user)
            db.session.commit()
            user_id = test_user.id
        with app.test_client() as client:
            with client.session_transaction() as session:
                session['_user_id'] = user_id
                session['_fresh'] = True
            response = client.get("/profile")
            assert response.status_code == 200
            assert f"User: {test_user.name}" in response.text

    def test_profile_authenticated(self, app):
        # https://flask-sqlalchemy-lite.readthedocs.io/en/latest/testing/#testing-data-around-requests
        # User must have an id. Without committing it will be None.
        with app.app_context():
            test_user = create_user('test@example.com', 'password123')
            db.session.add(test_user)
            db.session.commit()
        # The flask-login documentation describe this pattern to authenticate
        # a user in tests.
        # https://flask-login.readthedocs.io/en/latest/#automated-testing
        #
        # However, calling `app.test_client(user=user)` outside of an app context
        # will lead to an error:
        #
        #   sqlalchemy.orm.exc.DetachedInstanceError: Instance <User at 0x20280845e90> is not bound
        #   to a Session; attribute refresh operation cannot proceed
        #
        # And wrapping it in a `with app.app_context():` of its own will not work
        # either. It only works if the user is creates/or fetched from within the
        # same app context.
        #
        # This is problematic as it directly contradict what flask-sqlalchemy-lite suggests:
        # https://flask-sqlalchemy-lite.readthedocs.io/en/latest/testing/#testing-data-around-requests
        # > Accessing db.session or db.engine requires an app context, so you can
        # > push one temporarily. _Do not make requests inside an active context_,
        # > they will behave unexpectedly.
        #
        # Possible related:
        # * https://github.com/pallets/flask/issues/4053
        with app.test_client(user=test_user) as client:
            response = client.get("/profile")
            assert response.status_code == 200
            assert f"User: {test_user.name}" in response.text

    def test_profile_authenticated2(self, app, test_user):
        with authenticated_user(app, test_user) as client:
            response = client.get("/profile")
            assert response.status_code == 200
            assert f"User: {test_user.name}" in response.text
