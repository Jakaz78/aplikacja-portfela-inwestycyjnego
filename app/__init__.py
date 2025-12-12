from flask import Flask, request, redirect, url_for
from flask_login import current_user, LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .config import Config

# Inicjalizacja globalna
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 1. Inicjalizacja rozszerzeń
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from .blueprints.main import bp as main_bp
    from .blueprints.portfolio import bp as portfolio_bp
    from .blueprints.settings import bp as settings_bp
    from .blueprints.auth import bp as auth_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(portfolio_bp, url_prefix="/portfolio")
    app.register_blueprint(settings_bp, url_prefix="/settings")
    app.register_blueprint(auth_bp, url_prefix="/auth")

    from .models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # 4. Globalne wymuszanie logowania
    @app.before_request
    def require_login():
        # Lista wyjątków - publiczne miejsca
        if request.endpoint == 'static' or request.blueprint == 'auth':
            return

        if not current_user.is_authenticated:
            return redirect(url_for('auth.login', next=request.url))

    # 5. Import modeli dla migracji
    # Wystarczy prosty import na końcu, bez funkcji wrapper
    # Dzięki temu Alembic "zobaczy" modele
    from .models import (
        bond,
        portfolio,
        bond_definition,
        holding,
        transaction,
        user_settings,
        portfolio_history
    )  # noqa

    return app