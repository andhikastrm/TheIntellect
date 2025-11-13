from flask import jsonify
from extensions import db
from models import User, Kucing, Device
from flask import current_app as app

@app.route('/')
def home():
    return jsonify({"message": "Selamat datang di API Pemantauan Kucing!"})

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{"id": u.id, "nama": u.nama, "email": u.email} for u in users])

@app.route('/kucing', methods=['GET'])
def get_kucing():
    data = Kucing.query.all()
    return jsonify([
        {"id": k.id, "nama": k.nama, "ras": k.ras, "pemilik": k.pemilik.nama} for k in data
    ])

@app.route('/devices', methods=['GET'])
def get_devices():
    devices = Device.query.all()
    return jsonify([
        {"id": d.id, "nomor_seri": d.nomor_seri, "status": d.status, "lokasi": d.lokasi}
        for d in devices
    ])
