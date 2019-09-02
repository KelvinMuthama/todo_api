from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from api.config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)

    from api.main.routes import user_login
    from api.owner.routes import owner
    from api.task.routes import task

    app.register_blueprint(user_login)
    app.register_blueprint(owner)
    app.register_blueprint(task)

    return app
