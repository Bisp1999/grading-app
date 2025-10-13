import os
from urllib.parse import urlparse

# Absolute path to project root
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask-Babel configuration
    LANGUAGES = ['en', 'fr']
    BABEL_DEFAULT_LOCALE = 'en'
    BABEL_DEFAULT_TIMEZONE = 'UTC'

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'grading_app.db')

class ProductionConfig(Config):
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # Database configuration
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # Railway provides a postgresql:// URL, but SQLAlchemy needs postgresql+psycopg2://
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = database_url
    else:
        # Fallback for local production testing if DATABASE_URL is not set
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'prod.db')

    # Force HTTPS in production
    PREFERRED_URL_SCHEME = 'https'
    # Security headers
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
