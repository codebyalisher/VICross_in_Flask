import os
import logging
from .import database
from instance.config import Config
from AdminDashboard import database
from flask import Flask,current_app
from flask_login import LoginManager
from AdminDashboard.routes.utils import mail
from AdminDashboard.routes.models import User
from AdminDashboard.routes.auth_routes import bp
from AdminDashboard.routes.sockets_events import socketio
from AdminDashboard.routes.user_routes import bp as user_bp
from AdminDashboard.routes.company_routes import bp as company_bp
from AdminDashboard.routes.websockets_routes import bp as websocket_bp
from AdminDashboard.routes.trade_booths_routes import bp as tradebooth_bp
from AdminDashboard.routes.sockets_events import handle_connect, handle_disconnect, handle_message ,handle_join_room, handle_leave_room


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
    logging.basicConfig(filename='error.log', level=logging.INFO,format='%(asctime)s - %(levelname)s - %(message)s')
    app.register_blueprint(bp)    
    app.register_blueprint(user_bp)    
    app.register_blueprint(tradebooth_bp)    
    app.register_blueprint(company_bp)    
    app.register_blueprint(websocket_bp)    
    mail.init_app(app)    
    database.init_app(app) #initialize the database at the app level
    login_manager = LoginManager(app)
    socketio.init_app(app) 
  
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))    

    return app

