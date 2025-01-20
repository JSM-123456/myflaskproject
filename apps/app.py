from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from pathlib import Path
from apps.config import config


db = SQLAlchemy()
csrf = CSRFProtect()
login_manager = LoginManager()
# login_view 속성에 미로그인 시 리다이렉트하는 엔드포인트를 지정
login_manager.login_view = "auth.signup"
# login_manager 속성에 로그인 후 표시할 메세지를 아무것도 표시하지 않도록 지정
login_manager.login_message = ""

def create_app(config_key) :
    app = Flask(__name__)

    app.config.from_object(config[config_key])
    csrf.init_app(app)
    db.init_app(app)
    Migrate(app, db)

    login_manager.init_app(app)

    from apps.crud import views as crud_views
    app.register_blueprint(crud_views.crud, url_prefix="/crud")

    from apps.auth import views as auth_views
    app.register_blueprint(auth_views.auth, url_prefix="/auth")

    return app