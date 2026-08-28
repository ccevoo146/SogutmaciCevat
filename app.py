from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
import requests

app = Flask(__name__)
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# ADMIN AYARLARI
app.secret_key = "sogutmaci-cevat-gizli-anahtar"
ADMIN_SIFRE = "Cevat1234"


# ==============================
# VERİTABANI
# ==============================

def veritabani_olustur():

    conn = sqlite3.connect("randevular.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS randevular (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ad TEXT NOT NULL,
            soyad TEXT NOT NULL,
            telefon TEXT NOT NULL,
            ilce TEXT NOT NULL,
            adres TEXT NOT NULL,
            hizmet TEXT NOT NULL,
            tarih TEXT NOT NULL,
            saat TEXT NOT NULL,
            aciklama TEXT
        )
    """)

    conn.commit()
    conn.close()


# Uygulama başlarken veritabanını oluştur
veritabani_olustur()


# ==============================
# ANA SAYFA
# ==============================

@app.route("/")
def home():

    return render_template("index.html")


# ==============================
# ADMIN GİRİŞ
# ==============================

@app.route("/admin", methods=["GET", "POST"])
def admin():

    if request.method == "POST":

        sifre = request.form.get("sifre")

        if sifre == ADMIN_SIFRE:

            session["admin_giris"] = True

            return redirect(url_for("admin_panel"))

        return render_template(
            "login.html",
            hata="Şifre yanlış!"
        )

    return render_template("login.html")


# ==============================
# ADMIN PANEL
# ==============================

@app.route("/admin/panel")
def admin_panel():

    if not session.get("admin_giris"):

        return redirect(url_for("admin"))

    conn = sqlite3.connect("randevular.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            ad,
            soyad,
            telefon,
            ilce,
            adres,
            hizmet,
            tarih,
            saat,
            aciklama
        FROM randevular
        ORDER BY id DESC
    """)

    randevular = cursor.fetchall()

    conn.close()

    return render_template(
        "admin.html",
        randevular=randevular
    )


# ==============================
# ADMIN ÇIKIŞ
# ==============================

@app.route("/admin/cikis")
def admin_cikis():

    session.pop("admin_giris", None)

    return redirect(url_for("admin"))


# ==============================
# RANDEVU
# ==============================

@app.route("/randevu", methods=["POST"])
def randevu():

    ad = request.form.get("ad")
    soyad = request.form.get("soyad")
    telefon = request.form.get("telefon")
    ilce = request.form.get("ilce")
    adres = request.form.get("adres")
    hizmet = request.form.get("hizmet")
    tarih = request.form.get("tarih")
    saat = request.form.get("saat")
    aciklama = request.form.get("aciklama")

    conn = sqlite3.connect("randevular.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO randevular
        (
            ad,
            soyad,
            telefon,
            ilce,
            adres,
            hizmet,
            tarih,
            saat,
            aciklama
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        ad,
        soyad,
        telefon,
        ilce,
        adres,
        hizmet,
        tarih,
        saat,
        aciklama
    ))

    conn.commit()
    conn.close()

    mesaj = f"""
🔔 YENİ RANDEVU GELDİ!

👤 Müşteri: {ad} {soyad}
📞 Telefon: {telefon}

📍 İlçe: {ilce}
🏠 Adres: {adres}

🔧 Hizmet: {hizmet}

📅 Tarih: {tarih}
⏰ Saat: {saat}

📝 Açıklama:
{aciklama}
"""

    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    response = requests.post(
        telegram_url,
        data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": mesaj
        }
    )

    print("TELEGRAM DURUM:", response.status_code)
    print("TELEGRAM CEVAP:", response.text)

    return """
    <!DOCTYPE html>

    <html lang="tr">

    <head>

        <meta charset="UTF-8">

        <meta name="viewport"
              content="width=device-width, initial-scale=1.0">

        <title>Randevu Alındı - Soğutmacı Cevat</title>

        <style>

            body {
                margin: 0;
                min-height: 100vh;

                display: flex;
                align-items: center;
                justify-content: center;

                font-family: Arial, sans-serif;

                background: #eefaff;
            }

            .success-box {
                width: 90%;
                max-width: 500px;

                padding: 45px 30px;

                background: white;

                border-radius: 20px;

                text-align: center;

                box-shadow:
                    0 20px 60px
                    rgba(16, 42, 67, 0.12);
            }

            .success-icon {
                font-size: 60px;
                margin-bottom: 15px;
            }

            h1 {
                color: #102a43;
                margin-bottom: 15px;
            }

            p {
                color: #627d98;
                line-height: 1.6;
            }

            a {
                display: inline-block;

                margin-top: 20px;

                padding: 13px 22px;

                background: #087ea4;

                color: white;

                text-decoration: none;

                border-radius: 8px;

                font-weight: bold;
            }

        </style>

    </head>

    <body>

        <div class="success-box">

            <div class="success-icon">
                ✅
            </div>

            <h1>
                Randevu Talebiniz Alındı!
            </h1>

            <p>
                Bilgileriniz başarıyla kaydedildi.
            </p>

            <p>
                En kısa sürede sizinle iletişime geçeceğiz.
            </p>

            <a href="/">
                Ana Sayfaya Dön
            </a>

        </div>

    </body>

    </html>
    """


# ==============================
# LOCAL ÇALIŞTIRMA
# ==============================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
        use_reloader=False
    )