from werkzeug.contrib.fixers import ProxyFix
from flask import Flask,render_template
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import  LoginManager
from flask_pagedown import PageDown
from flask_moment import  Moment
from  config import config
import pymysql
pymysql.install_as_MySQLdb()


bootstrap=Bootstrap()
db=SQLAlchemy()
moment=Moment()
pagedown=PageDown()

login_manager=LoginManager()
login_manager.session_protection='strong'
login_manager.login_view='auth.login'

def create_app(config_name):
    app=Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    app.config['BOOTSTRAP_SERVE_LOCAL'] = True

    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    moment.init_app(app)
    pagedown.init_app(app)


    from .main import main as main_blueprint
    from .auth import auth as auth_blueprint
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint,url_prefix='/auth')

    return app
