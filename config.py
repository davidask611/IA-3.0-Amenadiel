import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'silvestre'  # Asegúrate de que sea única y segura
    SESSION_EXPIRATION = 30  # Expiración de sesión del administrador (en segundos)
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB
    ALLOWED_MIME_TYPES = ['application/json', 'text/plain', 'application/pdf']  # Tipos MIME permitidos
