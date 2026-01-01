from flask import Flask, render_template
from .extensions import db, login_manager
from .config import Config

import os



def create_app() :
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    
    #instance folder creator
    os.makedirs(os.path.join(app.root_path, "..", "instance"), exist_ok=True)
    
    
    #initializers
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page'
    
    #importing models
    from app import models
    
    
    #user loader
    @login_manager.user_loader
    def load_user(user_id):
        return models.User.query.get(int(user_id))
    
    
    from app.auth import auth_bp
    from app.admin import admin_bp
    from app.user import user_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)
    
    
    
    
    
    @app.route('/')
    @app.route('/home')
    def home():
        return render_template('home.html')
    
    @app.errorhandler(404)
    def not_found(e):
        return render_template('404.html'), 404
    
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('403.html'), 403
    
    
    
    
    
    
    
    
    return app
    
    