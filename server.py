from flask import Flask, render_template, request, redirect, url_for, flash, make_response, jsonify
from flask_mysqldb import MySQL
from dotenv import load_dotenv
import os
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
#---------------------------------------------------------------------------------------------------------------------------->

# Definición de la clase User
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

#---------------------------------------------------------------------------------------------------------------------------->

# Crear instancia de Flask
app = Flask(__name__, static_url_path='/static')
# Cargar variables de entorno desde un archivo .env
load_dotenv()

#---------------------------------------------------------------------------------------------------------------------------->

# Configuración de la base de datos
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')

# Crear una instancia de MySQL
mysql = MySQL(app)

#---------------------------------------------------------------------------------------------------------------------------->
# Configuración de rutas protegidas
app.secret_key = 'mysecretkey'
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Please log in to access this page."

#---------------------------------------------------------------------------------------------------------------------------->

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

#---------------------------------------------------------------------------------------------------------------------------->
# Ruta de inicio que redirige al home
@app.route('/')
def index():
    return render_template('home.html')


@app.route('/estadisticas')
def estadisticas():
    return render_template('estadisticas.html')


#---------------------------------------------------------------------------------------------------------------------------->

# Ruta de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Si el usuario ya está autenticado, redirigir a la página de pacientes
    if current_user.is_authenticated:
        return redirect(url_for('pacientes'))
    
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
            return redirect(url_for('pacientes'))
        else:
            flash('Invalid credentials', 'error')
    
    # Renderizar la plantilla de login
    return render_template('login.html')

#---------------------------------------------------------------------------------------------------------------------------->

# Ruta de la página de pacientes
@app.route('/pacientes')
@login_required
def pacientes():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM pacientes')
    data = cur.fetchall()
    cur.close()
    # Configurar la respuesta para no almacenar en caché
    response = make_response(render_template('pacientes.html', clientes=data))
    response.headers['Cache-Control'] = 'no-store'
    return response

#---------------------------------------------------------------------------------------------------------------------------->

# Ruta de logout
@app.route('/logout')
@login_required
def logout():
    # Cerrar sesión
    logout_user()
    flash('You have logged out.', 'info')
    return redirect(url_for('login'))

#---------------------------------------------------------------------------------------------------------------------------->

# Agregar Pacientes
@app.route('/add_paciente', methods=['GET', 'POST'])
@login_required
def add_paciente():
    if request.method == 'POST':
        nombre = request.form['nombre']
        dni = request.form['dni']
        direccion = request.form['direccion']
        barrio = request.form['barrio']
        telefono = request.form['telefono']
        genero = request.form['genero']
        tipo_dengue = request.form['tipo_dengue']
        
        # Conexión a la base de datos y ejecución de la consulta
        cur = mysql.connection.cursor()
        try:
            cur.execute("INSERT INTO pacientes (Nombre, DNI, Direccion, Barrio, Telefono, Genero, tipo_Dengue) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                        (nombre, dni, direccion, barrio, telefono, genero, tipo_dengue))
            mysql.connection.commit()
            flash('Paciente agregado correctamente', 'success')
        except Exception as e:
            print(f"Error: {e}")
            mysql.connection.rollback()
            flash('Error al agregar paciente', 'danger')
        finally:
            cur.close()
        
        return redirect(url_for('pacientes'))
    
    return render_template('agregar.html')

#---------------------------------------------------------------------------------------------------------------------------->

@app.route('/editar_paciente/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_paciente(id):
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        nombre = request.form['nombre']
        dni = request.form['dni']
        direccion = request.form['direccion']
        barrio = request.form['barrio']
        telefono = request.form['telefono']
        genero = request.form['genero']
        tipo_dengue = request.form['tipo_dengue']
        
        # Conexión a la base de datos y ejecución de la consulta
        try:
            cur.execute("UPDATE pacientes SET Nombre=%s, DNI=%s, Direccion=%s, Barrio=%s, Telefono=%s, Genero=%s, tipo_Dengue=%s WHERE ID_Paciente=%s", 
                        (nombre, dni, direccion, barrio, telefono, genero, tipo_dengue, id))
            mysql.connection.commit()
            flash('Paciente actualizado correctamente', 'success')
        except Exception as e:
            print(f"Error: {e}")
            mysql.connection.rollback()
            flash('Error al actualizar paciente', 'danger')
        finally:
            cur.close()
        
        return redirect(url_for('pacientes'))
    else:
        cur.execute('SELECT * FROM pacientes WHERE ID_Paciente = %s', (id,))
        paciente = cur.fetchone()
        cur.close()
        return render_template('editar.html', paciente=paciente)
    
#---------------------------------------------------------------------------------------------------------------------------->

@app.route('/eliminar_paciente/<int:id>', methods=['POST'])
def eliminar_paciente(id):
    # Conexión a la base de datos y ejecución de la consulta
    cur = mysql.connection.cursor()
    try:
        cur.execute("DELETE FROM pacientes WHERE ID_Paciente = %s", (id,))
        mysql.connection.commit()
        flash('Paciente eliminado correctamente', 'success')
    except Exception as e:
        print(f"Error: {e}")
        mysql.connection.rollback()
        flash('Error al eliminar paciente', 'danger')
    finally:
        cur.close()
    
    return redirect(url_for('pacientes'))

#---------------------------------------------------------------------------------------------------------------------------->

@app.route('/datos_casos_por_barrio')
def datos_casos_por_barrio():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT Barrio, COUNT(*) as num_casos FROM pacientes GROUP BY Barrio")
        data = cur.fetchall()
        cur.close()

        barrios = []
        num_casos = []

        for row in data:
            barrios.append(row[0])
            num_casos.append(row[1])

        return jsonify({"barrios": barrios, "num_casos": num_casos})

    except Exception as e:
        print(f"Error al obtener datos: {e}")
        return jsonify({"barrios": [], "num_casos": []})

#---------------------------------------------------------------------------------------------------------------------------->

@app.route('/datos_casos_por_tipo_barrio')
def datos_casos_por_tipo_barrio():
    try:
        # Conexión a la base de datos
        cur = mysql.connection.cursor()

        # Consulta para obtener los datos de casos por barrio y tipo de dengue
        cur.execute("""
            SELECT Barrio,
                   SUM(CASE WHEN tipo_Dengue = 'A' THEN 1 ELSE 0 END) AS num_A,
                   SUM(CASE WHEN tipo_Dengue = 'B' THEN 1 ELSE 0 END) AS num_B,
                   SUM(CASE WHEN tipo_Dengue = 'C' THEN 1 ELSE 0 END) AS num_C
            FROM pacientes
            GROUP BY Barrio
        """)
        data = cur.fetchall()

        # Procesamiento de los datos para prepararlos para el frontend
        resultados = []

        for row in data:
            resultados.append({
                'barrio': row[0],
                'num_A': row[1],
                'num_B': row[2],
                'num_C': row[3]
            })

        # Cierre de cursor
        cur.close()

        # Devolución de datos en formato JSON
        return jsonify(resultados)

    except Exception as e:
        print(f"Error al obtener datos: {e}")
        return jsonify([])

#---------------------------------------------------------------------------------------------------------------------------->

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run(port=3000, debug=True)
