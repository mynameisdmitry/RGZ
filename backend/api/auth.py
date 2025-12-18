from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from database import db
from models import User
from validators import Validator

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}

    required_fields = ["username", "password", "email", "first_name", "last_name", "group"]
    for field in required_fields:
        if field not in data or not str(data[field]).strip():
            return jsonify({"error": f"Поле {field} обязательно для заполнения"}), 400

    validations = [
        ("username", Validator.validate_username(data["username"])),
        ("password", Validator.validate_password(data["password"])),
        ("email", Validator.validate_email(data["email"])),
        ("first_name", Validator.validate_name(data["first_name"], "Имя")),
        ("last_name", Validator.validate_name(data["last_name"], "Фамилия")),
        ("group", Validator.validate_group(data["group"]))
    ]
    for _, (is_valid, message) in validations:
        if not is_valid:
            return jsonify({"error": message}), 400

    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"error": "Пользователь с таким именем уже существует"}), 400
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Пользователь с таким email уже существует"}), 400

    try:
        user = User(
            username=data["username"],
            email=data["email"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            group=data["group"]
        )
        user.set_password(data["password"])
        db.session.add(user)
        db.session.commit()

        token = user.generate_token()
        return jsonify({"message": "Регистрация успешна", "token": token, "user": user.to_dict()}), 201
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Ошибка при регистрации"}), 500

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    if "username" not in data or "password" not in data:
        return jsonify({"error": "Требуется имя пользователя и пароль"}), 400

    user = User.query.filter_by(username=data["username"]).first()
    if not user or not user.check_password(data["password"]):
        return jsonify({"error": "Неверное имя пользователя или пароль"}), 401

    token = user.generate_token()
    return jsonify({"message": "Вход выполнен успешно", "token": token, "user": user.to_dict()}), 200

@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    claims = get_jwt()
    user = User.query.filter_by(username=claims["sub"]).first()
    if not user:
        return jsonify({"error": "Пользователь не найден"}), 404
    return jsonify({"user": user.to_dict()}), 200