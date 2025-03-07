import os
from .import database
from instance.config import Config
from AdminDashboard import database
from flask import Flask,current_app
from flask_login import LoginManager
from AdminDashboard.routes.utils import mail
from AdminDashboard.routes.models import User
from AdminDashboard.routes.auth_routes import bp
from AdminDashboard.routes.user_routes import bp as user_bp

def create_app(test_config=None):    
    app = Flask(__name__, instance_relative_config=True)
    
    app.config['STATIC_FOLDER'] = 'static'
    app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024
    app.config.from_object(Config) 

    if test_config is None:        
        app.config.from_pyfile('config.py', silent=True)
    else:        
        app.config.from_mapping(test_config)    
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass    
    
    app.register_blueprint(bp)    
    app.register_blueprint(user_bp)    
    mail.init_app(app)    
    database.init_app(app) #initialize the database at the app level
    login_manager = LoginManager(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))    

    return app

