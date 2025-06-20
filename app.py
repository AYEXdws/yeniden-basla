import os
import re # Kelime filtresi için eklendi
import psycopg2
import psycopg2.extras
from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Yasaklı kelimeler küçük harfle tanımlanmalı
YASAKLI_KELIMELER = ["argo1", "küfür1", "istenmeyen1", "hakaret1"]

def get_db_connection():
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    return conn

# ... (index, kayit, giris, cikis, kaynaklar, profil fonksiyonları aynı kalacak) ...
# Bir önceki mesajdaki hallerini kullanabilirsin veya aşağıya ekliyorum.

@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("""
        SELECT mesajlar.id, kullanicilar.kullanici_adi, mesajlar.icerik, mesajlar.olusturma_tarihi
        FROM mesajlar
        JOIN kullanicilar ON mesajlar.kullanici_id = kullanicilar.id
        ORDER BY mesajlar.olusturma_tarihi DESC
    """)
    mesajlar = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', mesajlar=mesajlar)

@app.route('/kayit', methods=['GET', 'POST'])
def kayit():
    if 'user_id' in session: return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not username or not password:
            flash('Kullanıcı adı ve şifre boş bırakılamaz.', 'danger')
            return render_template('register.html')
        password_hash = generate_password_hash(password)
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO kullanicilar (kullanici_adi, sifre_hash) VALUES (%s, %s)",(username, password_hash))
            conn.commit()
            flash('Başarıyla kayıt oldunuz! Lütfen giriş yapın.', 'success')
            return redirect(url_for('giris'))
        except psycopg2.errors.UniqueViolation:
            flash('Bu kullanıcı adı zaten alınmış.', 'danger')
        finally:
            cur.close()
            conn.close()
    return render_template('register.html')

@app.route('/giris', methods=['GET', 'POST'])
def giris():
    if 'user_id' in session: return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM kullanicilar WHERE kullanici_adi = %s", (username,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        if user and check_password_hash(user['sifre_hash'], password):
            session.permanent = True
            session['user_id'] = user['id']
            session['username'] = user['kullanici_adi']
            flash('Giriş başarılı!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Kullanıcı adı veya şifre yanlış.', 'danger')
    return render_template('login.html')

@app.route('/cikis')
def cikis():
    session.clear()
    flash('Başarıyla çıkış yaptınız.', 'success')
    return redirect(url_for('index'))

@app.route('/profil/<string:kullanici_adi>')
def profil(kullanici_adi):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM kullanicilar WHERE kullanici_adi = %s", (kullanici_adi,))
    kullanici = cur.fetchone()
    if kullanici is None: abort(404)
    cur.execute("SELECT id, icerik, olusturma_tarihi FROM mesajlar WHERE kullanici_id = %s ORDER BY olusturma_tarihi DESC", (kullanici['id'],))
    mesajlar = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('profil.html', kullanici=kullanici, mesajlar=mesajlar)

@app.route('/kaynaklar')
def kaynaklar():
    return render_template('kaynaklar.html')

@app.route('/yeni-mesaj', methods=['POST'])
def yeni_mesaj():
    if 'user_id' not in session:
        flash('Mesaj göndermek için giriş yapmalısınız.', 'danger')
        return redirect(url_for('giris'))
    if 'son_mesaj_zamani' in session:
        son_zaman = datetime.fromisoformat(session['son_mesaj_zamani'])
        if datetime.now() - son_zaman < timedelta(seconds=60):
            flash('Çok sık mesaj gönderiyorsun. Lütfen 60 saniye bekle.', 'danger')
            return redirect(url_for('index'))
    icerik = request.form['icerik']
    if not icerik.strip():
        flash('Boş mesaj gönderemezsin.', 'danger')
        return redirect(url_for('index'))
    
    # --- YENİ VE GÜNCEL KELİME FİLTRESİ ---
    temiz_icerik = icerik
    for kelime in YASAKLI_KELIMELER:
        temiz_icerik = re.sub(kelime, '****', temiz_icerik, flags=re.IGNORECASE)
    # -----------------------------------------

    kullanici_id = session['user_id']
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO mesajlar (icerik, kullanici_id) VALUES (%s, %s)",(temiz_icerik, kullanici_id))
    conn.commit()
    cur.close()
    conn.close()
    session['son_mesaj_zamani'] = datetime.now().isoformat()
    flash('Mesajın başarıyla gönderildi!', 'success')
    return redirect(url_for('index'))

@app.route('/mesaj/sil/<int:mesaj_id>', methods=['POST'])
def mesaj_sil(mesaj_id):
    if 'user_id' not in session: abort(403)
    kullanici_id = session['user_id']
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM mesajlar WHERE id = %s AND kullanici_id = %s", (mesaj_id, kullanici_id))
    mesaj = cur.fetchone()
    if mesaj:
        cur.execute("DELETE FROM mesajlar WHERE id = %s", (mesaj_id,))
        conn.commit()
        flash('Mesajın başarıyla silindi.', 'success')
    else:
        flash('Bu işlemi yapmaya yetkiniz yok.', 'danger')
    cur.close()
    conn.close()
    return redirect(request.referrer or url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)