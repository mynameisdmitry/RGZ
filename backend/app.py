import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from database import db
from models import bcrypt, User, Locker
from api.auth import auth_bp
from api.lockers import lockers_bp
from api.users import users_bp

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # /home/wenby/RGZ
FRONT_DIR = os.path.join(ROOT_DIR, "frontend")

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)  # чтобы frontend через Live Server мог обращаться к backend
    db.init_app(app)
    bcrypt.init_app(app)
    JWTManager(app)

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(lockers_bp, url_prefix="/api/lockers")
    app.register_blueprint(users_bp, url_prefix="/api/users")

    with app.app_context():
        db.create_all()

        # создаём ячейки
        if Locker.query.count() == 0:
            for i in range(1, Config.LOCKER_COUNT + 1):
                db.session.add(Locker(locker_number=i))
            db.session.commit()

        # создаём администратора
        if not User.query.filter_by(username="admin").first():
            admin = User(
                username="admin",
                email="admin@example.com",
                first_name="Администратор",
                last_name="Системы",
                group="ADMIN",
                is_admin=True
            )
            admin.set_password(os.environ.get("ADMIN_PASSWORD", "Admin123!"))
            db.session.add(admin)
            db.session.commit()

    @app.route("/")
    def index():
        return send_from_directory(FRONT_DIR, "index.html")

    @app.route("/api/health")
    def health():
        return jsonify({"status": "healthy"})

    
    @app.route("/<path:path>")
    def frontend_assets(path):
        if path.startswith("api/"):
            abort(404)
    
        full = os.path.join(FRONT_DIR, path)
        if os.path.isfile(full):
            return send_from_directory(FRONT_DIR, path)
    
        # если путь не файл — отдаём главную 
        return send_from_directory(FRONT_DIR, "index.html")

    @app.route("/api")
    def api_info():
        return jsonify({
            "message": "Камера хранения API",
            "student": Config.STUDENT_NAME,
            "group": Config.STUDENT_GROUP,
            "version": "1.0.0"
        })
    
    return app
    

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)
