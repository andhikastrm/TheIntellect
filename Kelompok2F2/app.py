from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# Inisialisasi Flask
app = Flask(__name__)
CORS(app)

# Konfigurasi database (ganti sesuai kebutuhanmu)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kelompok2f2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inisialisasi database
db = SQLAlchemy(app)

# =======================
# MODELS
# =======================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    pets = db.relationship('Pet', backref='owner', lazy=True)
    devices = db.relationship('Device', backref='owner', lazy=True)

class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    ras = db.Column(db.String(100))
    tanggal_lahir = db.Column(db.String(20))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nomor_seri = db.Column(db.String(100), unique=True, nullable=False)
    status = db.Column(db.String(50))
    lokasi = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# =======================
# ROUTES
# =======================

@app.route('/')
def home():
    return jsonify({"message": "Selamat datang di API Kelompok2F2!"})

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{"id": u.id, "nama": u.nama, "email": u.email} for u in users])

@app.route('/pets', methods=['GET'])
def get_pets():
    pets = Pet.query.all()
    return jsonify([{"id": p.id, "nama": p.nama, "ras": p.ras, "owner": p.owner.nama} for p in pets])

@app.route('/devices', methods=['GET'])
def get_devices():
    devices = Device.query.all()
    return jsonify([{"id": d.id, "nomor_seri": d.nomor_seri, "status": d.status, "lokasi": d.lokasi} for d in devices])

# =======================
# MAIN PROGRAM
# =======================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
