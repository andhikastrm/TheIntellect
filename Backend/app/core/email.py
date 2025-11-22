# app/core/email.py — VERSI 100% MASUK GMAIL (PAKE EMAIL GUE)
import requests
from fastapi import HTTPException

def send_otp_email(email: str, otp: str):
    print(f"\nOTP UNTUK {email}: {otp} ← INI JUGA MUNcul DI TERMINAL BUAT CADANGAN\n")
    
    url = "https://api.brevo.com/v3/smtp/email"
    payload = {
        "sender": {"name": "Petricord", "email": "no-reply@petricord.me"},
        "to": [{"email": email}],
        "subject": "Kode OTP Petricord Kamu",
        "htmlContent": f"""
        <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#f8f9fa;padding:20px;">
          <div style="background:white;border-radius:16px;overflow:hidden;box-shadow:0 10px 30px rgba(0,0,0,0.1);">
            <div style="background:#6c5ce7;padding:30px;text-align:center;color:white;">
              <h1 style="margin:0;font-size:28px;">Petricord</h1>
            </div>
            <div style="padding:40px 30px;text-align:center;">
              <h2 style="color:#333;">Kode OTP Kamu</h2>
              <div style="font-size:48px;letter-spacing:12px;font-weight:bold;color:#6c5ce7;margin:30px 0;">
                {otp}
              </div>
              <p style="color:#666;font-size:16px;">
                Kode ini berlaku selama <strong>10 menit</strong>
              </p>
            </div>
          </div>
        </div>
        """,
        "textContent": f"Kode OTP Petricord: {otp}\nBerlaku 10 menit."
    }
    headers = {
        "accept": "application/json",
        "api-key": "xsmtpsib-7f8e9d8a8f8e9d8a8f8e9d8a8f8e9d8a8f8e9d8a8f8e9d8a8f8e9d8a8f8e9d8a",
        "content-type": "application/json"
    }
    
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=10)
        if r.status_code == 201:
            print("EMAIL OTP BERHASIL DIKIRIM VIA BREVO (masuk Gmail 100%)")
        else:
            print("Brevo gagal:", r.text)
    except:
        print("Koneksi error, tapi OTP tetap muncul di terminal")