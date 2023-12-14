from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
# from flask_mobility import Mobility
from oauthlib.oauth2 import WebApplicationClient

from app import config


db = SQLAlchemy()
GoogleClient = WebApplicationClient(config.GOOGLE_CLIENT_ID)


def setup_db(app: Flask, db: SQLAlchemy = db):
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql+psycopg2://{config.DB_USER}:{config.DB_PASS}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}' # noqa
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return db


def create_app():
    app = Flask(__name__)
    app.config.from_envvar('FLASK_SECRETS')
    setup_db(app)
    # Mobility(app)
    login_manager = LoginManager(app)
    login_manager.login_view = 'auth.login'
    login_manager.logout_view = 'auth.logout'

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        user = User.query.get(user_id)
        return user

    with app.app_context():
        from app.routes import auth, main, raffle
        app.register_blueprint(main.bp)
        app.register_blueprint(auth.bp)
        app.register_blueprint(raffle.bp)
        return app
