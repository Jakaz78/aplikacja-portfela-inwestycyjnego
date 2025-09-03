from flask import Flask
from .config import Config


def create_app(config_class=Config):
    # instance_relative_config — pozwala używać instance/ jako katalogu danych
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)
    config_class.init_app(app)

    # Importy lokalne, żeby nie tworzyć cykli
    from .blueprints.main import bp as main_bp
    from .blueprints.portfolio import bp as portfolio_bp
    from .blueprints.settings import bp as settings_bp

    app.register_blueprint(main_bp)                           # /, /statistics
    app.register_blueprint(portfolio_bp, url_prefix="/portfolio")  # /portfolio, /portfolio/import_csv
    app.register_blueprint(settings_bp, url_prefix="/settings")    # /settings

    return app