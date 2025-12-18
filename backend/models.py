from datetime import datetime, timedelta
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token
from database import db

bcrypt = Bcrypt()

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    group = db.Column(db.String(20), nullable=False, default="ПИ-202")
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # ВАЖНО: lazy='dynamic' чтобы работали count()/all()
    reservations = db.relationship("Locker", backref="reserved_by", lazy="dynamic")

    def set_password(self, password: str):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password: str):
        return bcrypt.check_password_hash(self.password_hash, password)

    def generate_token(self):
        additional_claims = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "group": self.group,
            "is_admin": self.is_admin
        }
        return create_access_token(identity=self.username, additional_claims=additional_claims)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "group": self.group,
            "is_admin": self.is_admin,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class Locker(db.Model):
    __tablename__ = "lockers"

    id = db.Column(db.Integer, primary_key=True)
    locker_number = db.Column(db.Integer, unique=True, nullable=False)
    status = db.Column(db.String(20), default="free", nullable=False)  # free / occupied
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    reserved_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def reserve(self, user_id: int, duration_days: int = 7):
        self.status = "occupied"
        self.user_id = user_id
        self.reserved_at = datetime.utcnow()
        self.expires_at = datetime.utcnow() + timedelta(days=duration_days)

    def release(self):
        self.status = "free"
        self.user_id = None
        self.reserved_at = None
        self.expires_at = None

    def to_dict(self):
        user_info = None
        if self.reserved_by:
            user_info = {
                "id": self.reserved_by.id,
                "username": self.reserved_by.username,
                "first_name": self.reserved_by.first_name,
                "last_name": self.reserved_by.last_name,
                "group": self.reserved_by.group
            }
        return {
            "id": self.id,
            "locker_number": self.locker_number,
            "status": self.status,
            "user_info": user_info,
            "reserved_at": self.reserved_at.isoformat() if self.reserved_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None
        }