from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from database import db
from models import User, Locker
from validators import Validator

users_bp = Blueprint("users", __name__)

@users_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    claims = get_jwt()
    user = User.query.filter_by(username=claims["sub"]).first()
    if not user:
        return jsonify({"error": "Пользователь не найден"}), 404

    data = request.get_json() or {}

    try:
        if "email" in data and data["email"]:
            ok, msg = Validator.validate_email(data["email"])
            if not ok:
                return jsonify({"error": msg}), 400
            existing = User.query.filter(User.email == data["email"], User.id != user.id).first()
            if existing:
                return jsonify({"error": "Этот email уже используется"}), 400
            user.email = data["email"]

        if "first_name" in data:
            ok, msg = Validator.validate_name(data["first_name"], "Имя")
            if not ok:
                return jsonify({"error": msg}), 400
            user.first_name = data["first_name"]

        if "last_name" in data:
            ok, msg = Validator.validate_name(data["last_name"], "Фамилия")
            if not ok:
                return jsonify({"error": msg}), 400
            user.last_name = data["last_name"]

        if "group" in data:
            ok, msg = Validator.validate_group(data["group"])
            if not ok:
                return jsonify({"error": msg}), 400
            user.group = data["group"]

        db.session.commit()
        return jsonify({"message": "Профиль обновлен", "user": user.to_dict()}), 200
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Ошибка при обновлении профиля"}), 500

@users_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    claims = get_jwt()
    user = User.query.filter_by(username=claims["sub"]).first()
    if not user:
        return jsonify({"error": "Пользователь не найден"}), 404
    return jsonify({"user": user.to_dict()}), 200

@users_bp.route("/me", methods=["DELETE"])
@jwt_required()
def delete_me():
    claims = get_jwt()
    user = User.query.filter_by(username=claims["sub"]).first()
    if not user:
        return jsonify({"error": "Пользователь не найден"}), 404

    try:
        lockers = Locker.query.filter_by(user_id=user.id).all()
        for l in lockers:
            l.release()

        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "Аккаунт успешно удален"}), 200
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Ошибка при удалении аккаунта"}), 500

# админ: список пользователей
@users_bp.route("/all", methods=["GET"])
@jwt_required()
def all_users():
    claims = get_jwt()
    current = User.query.filter_by(username=claims["sub"]).first()
    if not current or not current.is_admin:
        return jsonify({"error": "Требуются права администратора"}), 403

    users = User.query.order_by(User.id).all()
    return jsonify({"users": [u.to_dict() for u in users]}), 200

# общая статистика (можно вызывать без авторизации)
@users_bp.route("/stats", methods=["GET"])
def stats():
    total_users = User.query.count()
    total_lockers = Locker.query.count()
    occupied = Locker.query.filter_by(status="occupied").count()
    free = total_lockers - occupied
    return jsonify({
        "total_users": total_users,
        "total_lockers": total_lockers,
        "occupied_lockers": occupied,
        "free_lockers": free
    }), 200