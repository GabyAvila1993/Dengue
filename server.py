from flask import Flask, render_template, request, redirect, url_for

from flask_mysqldb import MySQL
app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'ministerio_salud'
mysql = MySQL(app) 

# En esta ruta debemos colocar el login
@app.route('/')
def inicio():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    # Aquí deberías validar el usuario y contraseña con la base de datos
    if username == 'test' and password == 'test':  # Validación de ejemplo
        return "Login exitoso"
    else:
        return "Usuario o contraseña incorrectos"

# En esta ruta colocamos el formulario para registro
@app.route('/register')
def registrar_contacto():
    return render_template('registro.html')

@app.route('/cargar_datos', methods=['POST'])
def agragar_datos():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        telefono = request.form['telefono']
        email = request.form['email']
        direccion = request.form['direccion']
        
        print(nombre)
        print(apellido)
        print(telefono)
        print(email)
        print(direccion)
        return "Datos recibidos"

# Opcional, colocar los tipos de dengue que hay y mostrarlos
@app.route('/tipo')
def tipos_dengue():
    return "Tipos de dengue"

# Colocar los contagios de los usuarios
@app.route('/casos')
def tipos_de_casos():
    return "Tipos de Casos"

# Para poder editar los contactos agregados
@app.route('/edit')
def editar():
    return "editar"

# Para poder eliminar los contactos agregados
@app.route('/delete')
def eliminar():
    return "eliminar"

if __name__ == '__main__':
    app.run(port=5000, debug=True)
