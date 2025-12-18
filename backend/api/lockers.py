from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from database import db
from models import Locker, User
from config import Config

lockers_bp = Blueprint("lockers", __name__)

def _has_auth_header():
    # В задании нужно различие: неавторизованный видит меньше
    return bool(request.headers.get("Authorization"))

@lockers_bp.route("/", methods=["GET"])
def get_lockers():
    try:
        lockers = Locker.query.order_by(Locker.locker_number).all()
        lockers_data = []

        for locker in lockers:
            d = locker.to_dict()
            if not _has_auth_header() and d["user_info"]:
                # скрываем персональные данные
                d["user_info"] = {"username": "скрыто"}
            lockers_data.append(d)

        total = len(lockers)
        occupied = sum(1 for l in lockers if l.status == "occupied")
        free = total - occupied

        return jsonify({
            "lockers": lockers_data,
            "statistics": {"total": total, "occupied": occupied, "free": free}
        }), 200
    except Exception:
        return jsonify({"error": "Ошибка при получении списка ячеек"}), 500

@lockers_bp.route("/<int:locker_id>", methods=["GET"])
def get_locker(locker_id: int):
    locker = Locker.query.get_or_404(locker_id)
    d = locker.to_dict()
    if not _has_auth_header() and d["user_info"]:
        d["user_info"] = {"username": "скрыто"}
    return jsonify({"locker": d}), 200

@lockers_bp.route("/<int:locker_id>/reserve", methods=["POST"])
@jwt_required()
def reserve_locker(locker_id: int):
    claims = get_jwt()
    user = User.query.filter_by(username=claims["sub"]).first()
    if not user:
        return jsonify({"error": "Пользователь не найден"}), 404

    if user.reservations.count() >= Config.MAX_RESERVATIONS_PER_USER:
        return jsonify({"error": f"Максимум {Config.MAX_RESERVATIONS_PER_USER} бронирований"}), 400

    locker = Locker.query.get_or_404(locker_id)
    if locker.status == "occupied":
        return jsonify({"error": "Ячейка уже занята"}), 400

    try:
        locker.reserve(user.id, Config.RESERVATION_DURATION_DAYS)
        db.session.commit()
        return jsonify({"message": "Ячейка забронирована", "locker": locker.to_dict()}), 200
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Ошибка при бронировании"}), 500

@lockers_bp.route("/<int:locker_id>/cancel", methods=["POST"])
@jwt_required()
def cancel_reservation(locker_id: int):
    claims = get_jwt()
    user = User.query.filter_by(username=claims["sub"]).first()
    if not user:
        return jsonify({"error": "Пользователь не найден"}), 404

    locker = Locker.query.get_or_404(locker_id)

    # можно отменять только свою бронь, либо админ
    if locker.user_id != user.id and not user.is_admin:
        return jsonify({"error": "Нельзя отменить чужое бронирование"}), 403

    if locker.status != "occupied":
        return jsonify({"error": "Ячейка не занята"}), 400

    try:
        locker.release()
        db.session.commit()
        return jsonify({"message": "Бронирование отменено", "locker": locker.to_dict()}), 200
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Ошибка при отмене бронирования"}), 500

@lockers_bp.route("/my-reservations", methods=["GET"])
@jwt_required()
def my_reservations():
    claims = get_jwt()
    user = User.query.filter_by(username=claims["sub"]).first()
    if not user:
        return jsonify({"error": "Пользователь не найден"}), 404

    reservations = user.reservations.order_by(Locker.locker_number).all()
    return jsonify({
        "reservations": [l.to_dict() for l in reservations],
        "count": len(reservations),
        "max_allowed": Config.MAX_RESERVATIONS_PER_USER
    }), 200

@lockers_bp.route("/admin/clear", methods=["POST"])
@jwt_required()
def clear_all():
    claims = get_jwt()
    user = User.query.filter_by(username=claims["sub"]).first()
    if not user or not user.is_admin:
        return jsonify({"error": "Требуются права администратора"}), 403

    try:
        lockers = Locker.query.filter_by(status="occupied").all()
        for l in lockers:
            l.release()
        db.session.commit()
        return jsonify({"message": "Все бронирования очищены", "cleared_count": len(lockers)}), 200
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Ошибка при очистке бронирований"}), 500