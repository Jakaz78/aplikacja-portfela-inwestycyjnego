import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY")
    JSON_AS_ASCII = False

    # Database
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{os.getenv('MYSQL_USER')}"
        f":{os.getenv('MYSQL_PASSWORD')}"
        f"@{os.getenv('MYSQL_HOST')}"
        f":{os.getenv('MYSQL_PORT')}"
        f"/{os.getenv('MYSQL_DB')}"
        f"?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024
    SQLALCHEMY_ECHO = True  # Dla deweloperki
    # App
    THEMES = ['Dark', 'Light']
    LANGUAGES = ['Polski', 'English', 'Deutsch']
    DEFAULT_SETTINGS = {'theme': 'Dark', 'language': 'Polski'}
    #FETCH_CPI = os.getenv('FETCH_CPI', 'false').lower() == 'true'

