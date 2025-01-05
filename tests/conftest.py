import os
from contextlib import contextmanager
from typing import Iterator

import pytest
from dotenv import load_dotenv
from flask_login import FlaskLoginClient
from sqlalchemy import select

from app import bcrypt, create_app, db
from app.models import Base, User


@contextmanager
def authenticated_user(app, user) -> Iterator[FlaskLoginClient]:
    # Flask-Login require the user object to have and id.
    # When using SQLAlchemy the User objects will not have an id without
    # committing it.
    with app.app_context():
        db.session.add(user)
        db.session.commit()
        user_id = user.id
    # flask-login documentation describe that for tests one can use
    # `app.test_client(user=user)`. However, the internal logic of that is to
    # call `user.get_id()` will will try to refresh the id attribute.
    #
    # This will not work without an application context:
    #
    #   sqlalchemy.orm.exc.DetachedInstanceError: Instance <User at 0x20280845e90> is not bound
    #   to a Session; attribute refresh operation cannot proceed
    #
    # But pushing an application context is explicitly warned against in the
    # flask-sqlalchemy(-lite) documentation:
    #
    # https://flask-sqlalchemy-lite.readthedocs.io/en/latest/testing/#testing-data-around-requests
    # > Accessing db.session or db.engine requires an app context, so you can
    # > push one temporarily. _Do not make requests inside an active context_,
    # > they will behave unexpectedly.
    #
    # To work around these incompatible design requirements this helper instead
    # replicates what `FlaskLoginClient` does, in terms of setting the appropriate
    # session data, but doing so by using cached id for the user.
    #
    # This will not work:
    #   yield app.test_client(user=user)
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['_user_id'] = user_id
            session['_fresh'] = True
        yield client


def create_test_app():
    # https://flask.palletsprojects.com/en/2.0.x/config/
    # https://testdriven.io/blog/flask-pytest/
    # https://flask-sqlalchemy-lite.readthedocs.io/en/latest/testing/

    load_dotenv()
    db_host = os.getenv('DEMO_DATABASE_HOST')
    db_port = os.getenv('DEMO_DATABASE_PORT')
    db_user = os.getenv('DEMO_DATABASE_USER')
    db_password = os.getenv('DEMO_DATABASE_PASSWORD')

    config = {
        # Flask
        'FLASK_APP': 'app',
        # Flask-Login
        'SESSION_PROTECTION': None,
        # Flask-WTF
        'WTF_CSRF_ENABLED': False,
        # App
        'DATABASE_HOST': db_host,
        'DATABASE_PORT': db_port,
        'DATABASE_USER': db_user,
        'DATABASE_PASSWORD': db_password,
        'DATABASE_NAME': 'flaskdemo-test',
        'SECRET_KEY': 'flaskdemo_test_app_key',
    }

    app = create_app(config)

    # https://flask-login.readthedocs.io/en/latest/#automated-testing
    app.test_client_class = FlaskLoginClient

    return app


@pytest.fixture(scope='session')
def db_ctx():
    test_app = create_test_app()
    with test_app.app_context():
        Base.metadata.drop_all(db.engine)
        Base.metadata.create_all(db.engine)


@pytest.fixture()
def app():
    app = create_test_app()

    # Based on:
    # https://flask-sqlalchemy-lite.readthedocs.io/en/latest/testing/#avoid-writing-data

    with app.app_context():
        # TODO: Temporarily doing this until I can figure out why rollback isn't
        # working.
        Base.metadata.drop_all(db.engine)
        Base.metadata.create_all(db.engine)
        # END-TODO

        engines = db.engines

    cleanup = []

    for key, engine in engines.items():
        connection = engine.connect()
        transaction = connection.begin()
        engines[key] = connection  # type: ignore
        cleanup.append((key, engine, connection, transaction))

    yield app

    for key, engine, connection, transaction in cleanup:
        transaction.rollback()
        connection.close()
        engines[key] = engine


@pytest.fixture()
def client(app) -> FlaskLoginClient:
    return app.test_client()


@pytest.fixture()
def test_user_raw_password():
    return 'password123'


@pytest.fixture()
def test_user(test_user_raw_password):
    return create_user('test@example.com', test_user_raw_password)


def create_user(email: str, password: str, name='Test User'):
    encrypted_password = bcrypt.generate_password_hash(password).decode('utf-8')
    return User(email=email, password=encrypted_password, name=name)
