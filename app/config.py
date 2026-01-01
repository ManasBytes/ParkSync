import os 

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "..", "instance")


class Config:
    SECRET_KEY = "dev-secret-key"
    
    SQLALCHEMY_DATABASE_URI = (
        f"sqlite:///{os.path.join(INSTANCE_DIR, "app.db")}"
    )
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
