from flask import Flask, render_template, request, redirect, url_for, flash, get_flashed_messages, make_response
from flask_mysqldb import MySQL
from dotenv import load_dotenv
import os
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required

# Definición de la clase User
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

# Crear instancia de Flask
app = Flask(__name__, static_url_path='/static')
# Cargar variables de entorno desde un archivo .env
load_dotenv()

# Configuración de la base de datos
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')

# Crear una instancia de MySQL
mysql = MySQL(app)

# Configuración de rutas protegidas
app.secret_key = 'mysecretkey'
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Please log in to access this page."

# Función para cargar el usuario desde la base de datos
@login_manager.user_loader
def load_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, username, password FROM admin WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    if user:
        return User(user[0], user[1], user[2])
    return None

# Ruta de inicio que redirige al login
@app.route('/')
def index():
    return redirect(url_for('login'))

# Ruta de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Si el usuario ya está autenticado, redirigir a la página de inicio
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    # Si se envía un formulario POST
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Verificar las credenciales en la base de datos
        with mysql.connection.cursor() as cur:
            cur.execute("SELECT id, username, password FROM admin WHERE username = %s AND password = %s", (username, password))
            user = cur.fetchone()
        
        # Si las credenciales son válidas, iniciar sesión
        if user:
            user_obj = User(user[0], user[1], user[2])
            login_user(user_obj)
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials', 'error')
    
    # Renderizar la plantilla de login
    return render_template('login.html')

# Ruta de la página de inicio
@app.route('/home')
@login_required
def home():
    # Configurar la respuesta para no almacenar en caché
    response = make_response(render_template('home.html'))
    response.headers['Cache-Control'] = 'no-store'
    return response

# Ruta de logout
@app.route('/logout')
@login_required
def logout():
    # Cerrar sesión
    logout_user()
    flash('You have logged out.', 'info')
    return redirect(url_for('login'))

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run(port=3000, debug=True)
