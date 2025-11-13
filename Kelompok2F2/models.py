from extensions import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    kucing = db.relationship('Kucing', backref='pemilik', lazy=True)
    devices = db.relationship('Device', backref='pemilik', lazy=True)
    notifikasi = db.relationship('Notifikasi', backref='penerima', lazy=True)
    pertanyaan = db.relationship('Pertanyaan', backref='penanya', lazy=True)

class Kucing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    ras = db.Column(db.String(100))
    tanggal_lahir = db.Column(db.String(20))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    riwayat = db.relationship('RiwayatKesehatan', backref='kucing', lazy=True)
    monitoring = db.relationship('Monitoring', backref='kucing', lazy=True)

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nomor_seri = db.Column(db.String(100), unique=True, nullable=False)
    status = db.Column(db.String(50))
    lokasi = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class RiwayatKesehatan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tanggal = db.Column(db.String(20))
    deskripsi = db.Column(db.String(200))
    kucing_id = db.Column(db.Integer, db.ForeignKey('kucing.id'), nullable=False)

class Monitoring(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    waktu = db.Column(db.String(20))
    aktivitas = db.Column(db.String(200))
    kucing_id = db.Column(db.Integer, db.ForeignKey('kucing.id'), nullable=False)

class Notifikasi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    isi = db.Column(db.String(200))
    status = db.Column(db.String(20), default="belum dibaca")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Pertanyaan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    isi = db.Column(db.String(200))
    jawaban = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120), nullable=False)
