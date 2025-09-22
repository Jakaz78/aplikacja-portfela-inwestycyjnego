from flask import Flask, request, redirect, url_for
from flask_login import current_user, LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .config import Config

# Inicjalizacja rozszerzeń
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    # Inicjalizacja rozszerzeń
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Rejestracja blueprintów
    register_blueprints(app)

    # Middleware i hooks
    configure_auth_middleware(app)
    configure_user_loader()

    # Import modeli dla migracji
    import_models()

    return app


def register_blueprints(app):
    """Rejestruje wszystkie blueprinty"""
    from .blueprints.main import bp as main_bp
    from .blueprints.portfolio import bp as portfolio_bp
    from .blueprints.settings import bp as settings_bp
    from .blueprints.auth import bp as auth_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(portfolio_bp, url_prefix="/portfolio")
    app.register_blueprint(settings_bp, url_prefix="/settings")
    app.register_blueprint(auth_bp, url_prefix="/auth")


def configure_auth_middleware(app):
    """Konfiguruje globalne wymaganie logowania"""

    @app.before_request
    def require_login():
        # Publiczne endpointy
        if request.endpoint in ('static', 'auth.login', 'auth.logout'):
            return None

        # Cały blueprint auth jest publiczny
        if request.blueprint == 'auth':
            return None

        # Wymagaj logowania dla reszty
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login', next=request.url))


def configure_user_loader():
    """Konfiguruje ładowanie użytkowników"""
    from .models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        if user_id and user_id.isdigit():
            return User.query.get(int(user_id))
        return None


def import_models():
    """Importuje wszystkie modeli dla migracji"""
    from .models import user, bond  # noqa: F401
    from .models.portfolio import Portfolio  # noqa: F401
    from .models.bond_definition import BondDefinition  # noqa: F401
    from .models.holding import Holding  # noqa: F401
    from .models.transaction import Transaction  # noqa: F401
