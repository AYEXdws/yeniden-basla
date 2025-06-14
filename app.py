import os
import psycopg2
import psycopg2.extras  # DictCursor için gerekli olan import
from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# .env dosyasındaki değişkenleri yükler
load_dotenv()

app = Flask(__name__)
# .env dosyasından gizli anahtarı yükler
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Veritabanı bağlantısı kuran bir fonksiyon
def get_db_connection():
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    return conn

# Ana sayfa route'u
@app.route('/')
def index():
    conn = get_db_connection()
    # DictCursor, veritabanından gelen verileri sözlük gibi kullanmamızı sağlar (örn: mesaj['kullanici_adi'])
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("""
        SELECT kullanicilar.kullanici_adi, mesajlar.icerik, mesajlar.olusturma_tarihi
        FROM mesajlar
        JOIN kullanicilar ON mesajlar.kullanici_id = kullanicilar.id
        ORDER BY mesajlar.olusturma_tarihi DESC
    """)
    mesajlar = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', mesajlar=mesajlar)

# Kayıt olma route'u
@app.route('/kayit', methods=['GET', 'POST'])
def kayit():
    if 'user_id' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_hash = generate_password_hash(password)
        
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO kullanicilar (kullanici_adi, sifre_hash) VALUES (%s, %s)",
                (username, password_hash)
            )
            conn.commit()
            flash('Başarıyla kayıt oldunuz! Lütfen giriş yapın.', 'success')
            return redirect(url_for('giris'))
        except psycopg2.errors.UniqueViolation:
            flash('Bu kullanıcı adı zaten alınmış. Lütfen farklı bir tane deneyin.', 'danger')
        finally:
            cur.close()
            conn.close()
    return render_template('register.html')

# Giriş yapma route'u
@app.route('/giris', methods=['GET', 'POST'])
def giris():
    if 'user_id' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        # Giriş yaparken de DictCursor kullanalım
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM kullanicilar WHERE kullanici_adi = %s", (username,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        
        if user and check_password_hash(user['sifre_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['kullanici_adi']
            flash('Giriş başarılı!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Kullanıcı adı veya şifre yanlış.', 'danger')
    return render_template('login.html')

# Çıkış yapma route'u
@app.route('/cikis')
def cikis():
    session.clear()
    flash('Başarıyla çıkış yaptınız.', 'success')
    return redirect(url_for('index'))

# Profil sayfası route'u
@app.route('/profil/<string:kullanici_adi>')
def profil(kullanici_adi):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM kullanicilar WHERE kullanici_adi = %s", (kullanici_adi,))
    kullanici = cur.fetchone()
    if kullanici is None:
        abort(404)
    cur.execute("SELECT icerik, olusturma_tarihi FROM mesajlar WHERE kullanici_id = %s ORDER BY olusturma_tarihi DESC", (kullanici['id'],))
    mesajlar = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('profil.html', kullanici=kullanici, mesajlar=mesajlar)

# Kaynaklar sayfası route'u
@app.route('/kaynaklar')
def kaynaklar():
    return render_template('kaynaklar.html')

# Yeni mesaj gönderme route'u
@app.route('/yeni-mesaj', methods=['POST'])
def yeni_mesaj():
    if 'user_id' not in session:
        flash('Mesaj göndermek için giriş yapmalısınız.', 'danger')
        return redirect(url_for('giris'))
    icerik = request.form['icerik']
    kullanici_id = session['user_id']
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO mesajlar (icerik, kullanici_id) VALUES (%s, %s)",
        (icerik, kullanici_id)
    )
    conn.commit()
    cur.close()
    conn.close()
    flash('Mesajın başarıyla gönderildi!', 'success')
    return redirect(url_for('index'))

# Uygulamayı doğrudan çalıştırdığımızda sunucuyu başlatır
if __name__ == '__main__':
    app.run(debug=True)