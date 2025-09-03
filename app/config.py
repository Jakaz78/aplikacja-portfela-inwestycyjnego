import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Trafią do app.config (bo UPPERCASE)
    SECRET_KEY = os.getenv("SECRET_KEY") or os.urandom(24)
    JSON_AS_ASCII = False

    # Ustawienia aplikacyjne
    THEMES = ['Dark', 'Light']
    LANGUAGES = ['Polski', 'English', 'Deutsch']
    DEFAULT_SETTINGS = {
        'theme': 'Dark',
        'language': 'Polski'
    }

    @staticmethod
    def init_app(app):
        """
        Tworzy katalog na dane w instance_path: instance/data
        i ustawia UPLOAD_FOLDER.
        """
        data_dir = Path(app.instance_path) / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        app.config['UPLOAD_FOLDER'] = str(data_dir)