import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings:
    # A URL completa já vem do Docker/.env. Sem senhas isoladas no código!
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    # Configurações gerais da aplicação
    DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    # Configurações de Email/SMTP
    SMTP_USER = os.getenv("SMTP_USER")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))

    # Configurações do Google Drive
    GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")
    GOOGLE_DRIVE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
    GOOGLE_DRIVE_FILE_NAME = os.getenv("GOOGLE_DRIVE_FILE_NAME", "BancoDeDados.xlsx")

settings = Settings()

