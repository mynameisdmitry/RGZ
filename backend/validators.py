import re
from email_validator import validate_email, EmailNotValidError

class Validator:
    @staticmethod
    def validate_username(username: str):
        if not username or len(username.strip()) == 0:
            return False, "Имя пользователя не может быть пустым"
        if len(username) < 3 or len(username) > 50:
            return False, "Имя пользователя должно быть от 3 до 50 символов"
        pattern = r"^[a-zA-Z0-9_.-]+$"
        if not re.match(pattern, username):
            return False, "Имя пользователя может содержать только латинские буквы, цифры, точку, дефис и подчеркивание"
        return True, "OK"

    @staticmethod
    def validate_password(password: str):
        if not password or len(password.strip()) == 0:
            return False, "Пароль не может быть пустым"
        if len(password) < 8:
            return False, "Пароль должен содержать минимум 8 символов"
        if not re.search(r"[A-Za-z]", password):
            return False, "Пароль должен содержать хотя бы одну букву"
        if not re.search(r"\d", password):
            return False, "Пароль должен содержать хотя бы одну цифру"
        if not re.search(r"[@$!%*#?&]", password):
            return False, "Пароль должен содержать хотя бы один специальный символ (@$!%*#?&)"
        return True, "OK"

    @staticmethod
    def validate_email(email: str):
        if not email or len(email.strip()) == 0:
            return False, "Email не может быть пустым"
        try:
            validate_email(email)
            return True, "OK"
        except EmailNotValidError as e:
            return False, str(e)

    @staticmethod
    def validate_name(name: str, field_name="Имя"):
        if not name or len(name.strip()) == 0:
            return False, f"{field_name} не может быть пустым"
        if len(name) < 2 or len(name) > 50:
            return False, f"{field_name} должно быть от 2 до 50 символов"
        pattern = r"^[a-zA-Zа-яА-ЯёЁ\s-]+$"
        if not re.match(pattern, name):
            return False, f"{field_name} может содержать только буквы, пробелы и дефисы"
        return True, "OK"

    @staticmethod
    def validate_group(group: str):
        if not group or len(group.strip()) == 0:
            return False, "Группа не может быть пустой"
        if len(group) > 20:
            return False, "Название группы не должно превышать 20 символов"
        pattern = r"^[А-Яа-яA-Za-z0-9-]+$"
        if not re.match(pattern, group):
            return False, "Группа может содержать только буквы, цифры и дефисы"
        return True, "OK"