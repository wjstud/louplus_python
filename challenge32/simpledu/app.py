from flask import Flask, render_template
from simpledu.config import configs
from simpledu.models import db, User
from flask_migrate import Migrate
from flask_login import LoginManager

def register_extensions(app):
    db.init_app(app)
    Migrate(app, db)

    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def user_loader(id):
        return User.query.get(id)

    login_manager.login_view = 'front.login'

def register_blueprints(app):
    from .handlers import front, course, admin, user, live
    app.register_blueprint(front)
    app.register_blueprint(course)
    app.register_blueprint(admin)
    app.register_blueprint(user)
    app.register_blueprint(live)

def create_app(config):
    ''' 根据传人的 config 加载不同的配置 '''

    app = Flask(__name__)
    app.config.from_object(configs.get(config))
    # SQLAlchemy 的初始化方式改为使用 init_app
    register_extensions(app)
    register_blueprints(app)

    return app
