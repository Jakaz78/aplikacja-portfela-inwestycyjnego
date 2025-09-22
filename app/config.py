import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", os.urandom(24).hex())
    JSON_AS_ASCII = False

    # Database
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{os.getenv('MYSQL_USER', 'root')}"
        f":{os.getenv('MYSQL_PASSWORD', '')}"
        f"@{os.getenv('MYSQL_HOST', '127.0.0.1')}"
        f":{os.getenv('MYSQL_PORT', '3306')}"
        f"/{os.getenv('MYSQL_DB', 'obligacje')}"
        f"?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # App settings
    THEMES = ['Dark', 'Light']
    LANGUAGES = ['Polski', 'English', 'Deutsch']
    DEFAULT_SETTINGS = {'theme': 'Dark', 'language': 'Polski'}
    FETCH_CPI = os.getenv('FETCH_CPI', 'false').lower() == 'true'

