# config.py
import os
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Configuration centrale de VitalHelp (locale + production)"""

    # --- Sécurité Flask ---
    SECRET_KEY = os.getenv("SECRET_KEY", "fallback-only-for-dev")

    # --- Base de données : priorité à DATABASE_URL (Render) ---
    DATABASE_URL = os.getenv("DATABASE_URL")
    if DATABASE_URL:
        # Render donne "postgres://..." → SQLAlchemy veut "postgresql+psycopg://"
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
        elif DATABASE_URL.startswith("postgresql://"):
            DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # Mode local : lecture des variables DB_*
        DB_USER = os.getenv("DB_USER")
        DB_PASSWORD = os.getenv("DB_PASSWORD")
        DB_HOST = os.getenv("DB_HOST", "localhost")
        DB_PORT = os.getenv("DB_PORT", "7722")   # ton port personnalisé
        DB_NAME = os.getenv("DB_NAME")
        SQLALCHEMY_DATABASE_URI = (
            f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024
    UPLOAD_FOLDER = os.path.join(basedir, "static", "uploads", "avatars")
    ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

    # --- IA Groq ---
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")