from flask import Flask
from flask_bootstrap import Bootstrap
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
bootstrap = Bootstrap()
csrf = CSRFProtect()
db = SQLAlchemy()
login_manager = LoginManager()

from .views import page
from .models import User

def create_app(config):
    app.config.from_object(config)

    csrf.init_app(app)
    bootstrap.init_app(app)
    app.register_blueprint(page)
    login_manager.init_app(app)
    login_manager.login_view = '.login'

    with app.app_context():
        db.init_app(app)
        db.create_all()
    return app