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
    from app import models
    
    
    
    
    
    
    
    
    return app
    
    