import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

def get_db_connection():
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
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

@app.route('/giris', methods=['GET', 'POST'])
def giris():
    if 'user_id' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM kullanicilar WHERE kullanici_adi = %s", (username,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        
        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
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

# YENİ EKLENDİ - Profil Sayfası Route'u
@app.route('/profil/<string:kullanici_adi>')
def profil(kullanici_adi):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM kullanicilar WHERE kullanici_adi = %s", (kullanici_adi,))
    kullanici = cur.fetchone()
    if kullanici is None:
        abort(404)
    cur.execute("SELECT icerik, olusturma_tarihi FROM mesajlar WHERE kullanici_id = %s ORDER BY olusturma_tarihi DESC", (kullanici[0],))
    mesajlar = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('profil.html', kullanici=kullanici, mesajlar=mesajlar)

# YENİ EKLENDİ - Kaynaklar Sayfası Route'u
@app.route('/kaynaklar')
def kaynaklar():
    return render_template('kaynaklar.html')

if __name__ == '__main__':
    app.run(debug=True)