import pytest
from sqlalchemy import select

from app import db
from tests.conftest import create_user


@pytest.fixture
def app_ctx(app):
    with app.app_context() as ctx:
        yield ctx


@pytest.mark.usefixtures("db_ctx", "app_ctx")
class TestDatabase:

    def test_one(self, test_user_raw_password):
        user1 = create_user('test1@example.com', test_user_raw_password)
        db.session.add(user1)

        user2 = create_user('test2@example.com', test_user_raw_password)
        db.session.add(user2)

        db.session.commit()

        user3 = create_user('test3@example.com', test_user_raw_password)
        db.session.add(user3)
        db.session.commit()

        user4 = create_user('test4@example.com', test_user_raw_password)
        db.session.add(user4)
        db.session.commit()

    def test_two(self, test_user_raw_password):
        user1 = create_user('test1@example.com', test_user_raw_password)
        db.session.add(user1)
        db.session.commit()
