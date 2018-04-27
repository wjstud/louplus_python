from flask import Flask, render_template
from simpledu.config import configs
from simpledu.models import db, Course

def register_blueprints(app):
    from .handlers import front, course, admin, user
    app.register_blueprint(front)
    app.register_blueprint(course)
    app.register_blueprint(admin)
    app.register_blueprint(user)

def create_app(config):
    ''' 根据传人的 config 加载不同的配置 '''

    app = Flask(__name__)
    app.config.from_object(configs.get(config))
    # SQLAlchemy 的初始化方式改为使用 init_app
    db.init_app(app)
    register_blueprints(app)

    return app
