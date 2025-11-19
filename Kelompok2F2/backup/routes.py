from flask import Blueprint, jsonify, render_template, request, redirect, flash, url_for, session
from models import User, Kucing, Device
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
import random

# Blueprint
routes_bp = Blueprint("routes_bp", __name__)


# ======================================================
# HOME PAGE (Redirect ke login)
# ======================================================
@routes_bp.route('/')
def home():
    return redirect(url_for('routes_bp.login'))


# ======================================================
# REGISTER PAGE (Tahap 1: Input Data & Kirim OTP)
# ======================================================
@routes_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Ambil data dari form
        nama_depan = request.form.get("nama_depan")
        nama_belakang = request.form.get("nama_belakang")
        email = request.form.get("email")
        password = request.form.get("password")
        konfirmasi = request.form.get("konfirmasi")

        # Validasi Password
        if password != konfirmasi:
            flash("Password tidak cocok!", "error")
            return redirect(url_for('routes_bp.register'))

        # Cek apakah email sudah terdaftar di DB
        user_exist = User.query.filter_by(email=email).first()
        if user_exist:
            flash("Email sudah terdaftar!", "error")
            return redirect(url_for('routes_bp.register'))

        # SIMPAN DATA SEMENTARA DI SESSION (Belum masuk Database)
        # Data ini hanya akan disimpan jika OTP berhasil diverifikasi nanti
        session['temp_user'] = {
            'nama': f"{nama_depan} {nama_belakang}",
            'email': email,
            'password': generate_password_hash(password, method='pbkdf2:sha256')
        }

        # GENERATE KODE OTP (4 Digit Acak)
        otp_code = str(random.randint(1000, 9999))
        session['otp_code'] = otp_code
        
        # --- SIMULASI PENGIRIMAN OTP ---
        # Kode ini akan muncul di Terminal VS Code Anda (bagian bawah)
        print(f"\n===========================================")
        print(f"🔑 KODE OTP UNTUK {email}: {otp_code}")
        print(f"===========================================\n")

        flash("Kode OTP telah dikirim (Cek Terminal Server)", "info")
        
        # Arahkan ke halaman verifikasi OTP
        return redirect(url_for('routes_bp.verify_otp_page'))

    # Render halaman register
    return render_template("login&register/register.html")


# ======================================================
# HALAMAN VERIFIKASI OTP (Tahap 2: Cek Kode)
# ======================================================
@routes_bp.route("/verify-otp", methods=["GET", "POST"])
def verify_otp_page():
    # Jika user belum isi form register (tidak ada data temp_user di session), tendang balik ke register
    if 'temp_user' not in session:
        flash("Silakan isi form pendaftaran terlebih dahulu.", "warning")
        return redirect(url_for('routes_bp.register'))

    if request.method == "POST":
        # Ambil token OTP dari input hidden di HTML (otp.html)
        # Pastikan di otp.html input hiddennya bernama 'otp_token'
        input_otp = request.form.get("otp_token")
        
        # Ambil kode asli yang disimpan di session saat register
        server_otp = session.get('otp_code')

        if input_otp == server_otp:
            # === OTP BENAR ===
            # Ambil data user yang disimpan sementara di session
            data = session['temp_user']
            
            # Buat User Baru dan Simpan ke Database Permanen
            new_user = User(
                nama=data['nama'],
                email=data['email'],
                password=data['password']
            )
            db.session.add(new_user)
            db.session.commit()

            # Bersihkan session (Hapus data sementara agar aman)
            session.pop('temp_user', None)
            session.pop('otp_code', None)

            flash("Registrasi Berhasil! Silakan Login.", "success")
            return redirect(url_for('routes_bp.login'))
        else:
            # === OTP SALAH ===
            flash("Kode OTP Salah! Silakan coba lagi.", "error")
            return redirect(url_for('routes_bp.verify_otp_page'))

    # Tampilkan halaman OTP
    return render_template("/Login&Register/OTP.html")


# ======================================================
# LOGIN PAGE
# ======================================================
@routes_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # Cari user di database
        user = User.query.filter_by(email=email).first()

        # Cek password hash
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash(f"Selamat datang kembali, {user.nama}!", "success")
            return redirect(url_for('routes_bp.dashboard'))
        else:
            flash("Email atau password salah!", "error")
            return redirect(url_for('routes_bp.login'))

    return render_template("login&register/login.html")


# ======================================================
# DASHBOARD
# ======================================================
@routes_bp.route("/dashboard")
def dashboard():
    if 'user_id' not in session:
        flash("Silakan login terlebih dahulu.", "warning")
        return redirect(url_for('routes_bp.login'))
        
    return "<h1>Dashboard Utama</h1><p>Login Sukses!</p><a href='/logout'>Logout</a>"


# ======================================================
# LOGOUT
# ======================================================
@routes_bp.route("/logout")
def logout():
    session.clear()
    flash("Anda telah logout.", "info")
    return redirect(url_for('routes_bp.login'))


# ======================================================
# API ENDPOINTS
# ======================================================
@routes_bp.route('/api')
def api_home():
    return jsonify({"message": "Selamat datang di API Pemantauan Kucing!"})

@routes_bp.route('/api/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([
        {"id": u.id, "nama": u.nama, "email": u.email}
        for u in users
    ])

@routes_bp.route('/api/kucing', methods=['GET'])
def get_kucing():
    data = Kucing.query.all()
    return jsonify([
        {"id": k.id, "nama": k.nama, "ras": k.ras, "pemilik": k.pemilik.nama}
        for k in data
    ])

@routes_bp.route('/api/devices', methods=['GET'])
def get_devices():
    devices = Device.query.all()
    return jsonify([
        {"id": d.id, "nomor_seri": d.nomor_seri, "status": d.status, "lokasi": d.lokasi}
        for d in devices
    ])
