from flask import Flask
from flask_alembic import Alembic
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy_lite import SQLAlchemy

from .models import Base

db = SQLAlchemy()
alembic = Alembic(metadatas=Base.metadata)
bcrypt = Bcrypt()
migrate = Migrate()


def create_app(test_config: dict | None = None):
    from .models import User

    app = Flask(__name__)

    if test_config is None:
        app.config.from_prefixed_env(prefix='DEMO')
    else:
        app.testing = True
        app.config |= test_config

    db_host = app.config['DATABASE_HOST']
    db_port = app.config['DATABASE_PORT']
    db_user = app.config['DATABASE_USER']
    db_password = app.config['DATABASE_PASSWORD']
    db_database = app.config['DATABASE_NAME']
    assert db_host is not None
    assert db_port is not None
    assert db_user is not None
    assert db_password is not None
    app.config |= {
        'SQLALCHEMY_ENGINES': {
            'default': f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_database}',
        },
    }

    assert app.config['SECRET_KEY'] is not None
    assert app.config['SECRET_KEY'] != 'TODO_GENERATE_KEY'

    db.init_app(app)
    alembic.init_app(app)
    bcrypt.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'web.login'  # type: ignore
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from .web import web as web_blueprint

    app.register_blueprint(web_blueprint)

    return app
