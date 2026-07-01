from flask import Flask
from app.webapp import web_bp
from app.database import close_db  # ⬅️ ini penting

def create_app():
    app = Flask(__name__)
    app.secret_key = 'rahasia-super-unik'  # Penting agar flash() bekerja

    app.register_blueprint(web_bp)

    # ⬇️ Tambahkan ini agar koneksi DB otomatis ditutup setelah setiap request
    app.teardown_appcontext(close_db)

    return app
