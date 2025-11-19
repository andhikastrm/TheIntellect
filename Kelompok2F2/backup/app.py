from flask import Flask
from extensions import db
from routes import routes_bp  # Import blueprint dari routes.py

app = Flask(__name__)

# Konfigurasi Database (Sesuaikan dengan database kamu)
# Contoh pakai SQLite sementara biar jalan
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///petricord.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'kucing_lucu_banget_123' # Ganti dengan secret key yang aman

# Inisialisasi DB
db.init_app(app)

# Daftarkan Blueprint (PENTING!)
# Ini yang bikin routes.py terbaca oleh aplikasi utama
app.register_blueprint(routes_bp)

if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Buat tabel database jika belum ada
    app.run(debug=True)