import os

# Base directory for the application
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Basic configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-pos-key'
    
    # SQLite Database connection
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
