import os


class Config:
    # Asegúrate de que sea única y segura
    SECRET_KEY = os.environ.get('SECRET_KEY') or '123abc'
    # Expiración de sesión del administrador (en segundos)
    SESSION_EXPIRATION = 30
    ALLOWED_MIME_TYPES = ['application/json', 'text/plain',
                          'application/pdf']  # Tipos MIME permitidos
