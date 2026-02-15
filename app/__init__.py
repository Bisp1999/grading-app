from flask import Flask, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_babel import Babel
from flask_migrate import Migrate
import os

# Initialize extensions

db = SQLAlchemy()
login_manager = LoginManager()
babel = Babel()
migrate = Migrate()


def get_locale():
    from flask import session, request
    # Check if user is logged in and has a preferred language
    from flask_login import current_user
    if current_user.is_authenticated and hasattr(current_user, 'preferred_language') and current_user.preferred_language:
        return current_user.preferred_language
    
    # Check session for language preference
    if 'language' in session:
        return session['language']
    
    # Default to browser language or English
    return request.accept_languages.best_match(['en', 'fr']) or 'en'


def create_app(config_name=None):
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    from config import config
    app.config.from_object(config[config_name])
    
    # Session configuration
    app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    babel.init_app(app, locale_selector=get_locale)

    # Make Babel functions available in templates
    @app.context_processor
    def inject_conf_vars():
        from flask_babel import get_locale
        static_version = (
            app.config.get('STATIC_VERSION')
            or os.environ.get('STATIC_VERSION')
            or os.environ.get('RAILWAY_GIT_COMMIT_SHA')
            or os.environ.get('RAILWAY_DEPLOYMENT_ID')
            or 'dev'
        )
        return {
            'get_locale': get_locale,
            'LANGUAGES': {'en': 'English', 'fr': 'Français'},
            'static_version': static_version,
        }

    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
