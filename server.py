from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from dotenv import load_dotenv
import os
from flask_login import LoginManager, UserMixin, login_user, current_user
from flask_login import login_required


# Definición de la clase User
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

app = Flask(__name__, static_url_path='/static')
app.secret_key = 'mysecretkey'
load_dotenv()

app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')

mysql = MySQL(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Por favor inicia sesión para acceder a esta página."

@login_manager.user_loader
def load_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, username, password FROM admin WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    if user:
        return User(user[0], user[1], user[2])  # Aquí se usa la clase User definida arriba
    return None

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Usando 'with' para asegurar que la conexión se cierre correctamente
        with mysql.connection.cursor() as cur:
            cur.execute("SELECT id, username, password FROM admin WHERE username = %s AND password = %s", (username, password))
            user = cur.fetchone()
        
        if user:
            user_obj = User(user[0], user[1], user[2])
            login_user(user_obj)
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Credenciales Inválidas', 'error')
    
    return render_template('login.html')


@app.route('/home')
@login_required
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(port=3000, debug=True)
