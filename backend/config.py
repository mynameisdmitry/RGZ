import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Данные студента (показываем на всех страницах фронта)
    STUDENT_NAME = "Игуменшев Дмитрий Евгеньевич"
    STUDENT_GROUP = "ФБИ-33"

    # Flask
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key"

    # PostgreSQL
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or \
        "postgresql://locker_user:dima2005@localhost/locker_storage"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or "jwt-secret-key"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

    # Логика приложения
    MAX_RESERVATIONS_PER_USER = 5
    LOCKER_COUNT = 120
    RESERVATION_DURATION_DAYS = 7