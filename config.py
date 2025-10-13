import os
from urllib.parse import urlparse

# Absolute path to project root
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database configuration
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL:
        # Railway PostgreSQL
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # Local SQLite for development (absolute path to avoid cwd issues)
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'grading_app.db')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask-Babel configuration
    LANGUAGES = ['en', 'fr']
    BABEL_DEFAULT_LOCALE = 'en'
    BABEL_DEFAULT_TIMEZONE = 'UTC'

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'grading_app.db')

class ProductionConfig(Config):
    DEBUG = False
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
