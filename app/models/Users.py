from app.extensions import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    username = db.Column(db.String(100), unique = True,  nullable = False)
    email = db.Column(db.String(100), unique = True, nullable = False)
    password_hash = db.Column(db.String(250), nullable = False)
    is_admin = db.Column(db.Boolean, default = False, nullable = False)
    created_at = db.Column(db.DateTime, server_default = func.now(), nullable = False)
    
    
    reservations = db.relationship("Reservation", backref = "user", lazy = True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    