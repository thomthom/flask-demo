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
    # User must have an id. Without committing it will be None.
    with app.app_context():
        db.session.add(user)
        db.session.commit()
    yield app.test_client(user=user)


def seed_user(app, user):
    with app.app_context():
        db.session.add(user)
        db.session.commit()
        stmt = select(User).filter_by(email=user.email)
        return db.session.execute(stmt).scalars().one()


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
        'TILES_EXTRACT': './graphs/nordics/custom_files/valhalla_tiles.tar',
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
    print('>>> Database Context Start')
    yield
    print('>>> Database Context End')


@pytest.fixture()
def app():
    test_app = create_test_app()
    app = test_app

    # with app.app_context():
    #     # Base.metadata.drop_all(db.engine)
    #     # Base.metadata.create_all(db.engine)
    #     engines = db.engines

    # cleanup = []

    # for key, engine in engines.items():
    #     connection = engine.connect()
    #     transaction = connection.begin()
    #     engines[key] = connection  # type: ignore
    #     cleanup.append((key, engine, connection, transaction))

    with app.app_context():
        connection = db.engine.connect()
        transaction = connection.begin()
        # t = db.session.begin_nested()

    yield app

    with app.app_context():
        # t.rollback()
        # db.session.rollback()
        # db.session.close()
        transaction.rollback()
        connection.close()
        # connection.rollback()

    # for key, engine, connection, transaction in cleanup:
    #     transaction.rollback()
    #     connection.close()
    #     engines[key] = engine


@pytest.fixture()
def client(app) -> FlaskLoginClient:
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


@pytest.fixture()
def test_user_raw_password():
    return 'password123'


@pytest.fixture()
def test_user(test_user_raw_password):
    return create_user('test@example.com', test_user_raw_password)


def create_user(email: str, password: str, name='Test User'):
    encrypted_password = bcrypt.generate_password_hash(password).decode('utf-8')
    return User(email=email, password=encrypted_password, name=name)
