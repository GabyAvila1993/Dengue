from flask import Flask, flash, jsonify, redirect, render_template, request, url_for
from flask_mysqldb import MySQL

import os
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.secret_key = "mysecretkey"
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Por favor inicia sesión para acceder a esta página."
# Configuración de la base de datos MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'Dengue'

# Inicialización de MySQL
mysql = MySQL(app)

class User(UserMixin):
    def __init__(self, id_usuario, Correo, contraseña):
        self.id_usuario = id_usuario
        self.Correo = Correo
        self.contraseña = contraseña

@login_manager.user_loader
def load_user(id_usuario):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id_usuario, Correo, contraseña FROM usuario WHERE id_usario = %s", (id_usuario,))
    user = cur.fetchone()
    cur.close()
    if user:
        return User(user[0], user[1], user[2])
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        Correo = request.form['Correo']
        contraseña = request.form['contraseña']
        
        with mysql.connection.cursor() as cur:
            cur.execute("SELECT id_usuario, Correo, contraseña FROM usuario WHERE Correo = %s AND contraseña = %s", (Correo, contraseña))
            user = cur.fetchone()
        
        if user:
            user_obj = User(user[0], user[1], user[2])
            login_user(user_obj)
            flash('Login successful!', 'success')
            return redirect(url_for('data'))
        else:
            flash('Credenciales Invalidas', 'error')
    return render_template('login.html')

# Ruta de inicio
@app.route('/')
def inicio():
    return render_template('tipos.html')

## Ruta para obtener datos de casos por barrio

## Ruta para obtener datos de casos por barrio
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

# Ruta principal que renderiza la página de estadísticas
@app.route('/estadisticas')
def estadisticas():
    return render_template('estadisticas.html')

# Ruta para agregar un nuevo paciente
@app.route('/add_paciente', methods=['GET', 'POST'])
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
        except Exception as e:
            print(f"Error: {e}")
            mysql.connection.rollback()
        finally:
            cur.close()
        
        return redirect(url_for('mostrar_pacientes'))
    
    return render_template('agregar.html')

# Ruta para mostrar todos los pacientes
@app.route('/pacientes')
def mostrar_pacientes():
    cur = mysql.connection.cursor()
    try:
        cur.execute("SELECT * FROM pacientes")
        data = cur.fetchall()
    except Exception as e:
        print(f"Error: {e}")
        data = []
    finally:
        cur.close()
    
    return render_template('pacientes.html', pacientes=data)

@app.route('/editar_paciente/<int:id>', methods=['GET', 'POST'])
def editar_paciente(id):
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
        
        return redirect(url_for('mostrar_pacientes'))
    
    # Obtener los datos del paciente a editar
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM pacientes WHERE ID_Paciente = %s", (id,))
    paciente = cur.fetchone()  # Esto debería devolver un diccionario con los datos del paciente
    cur.close()
    
    if paciente:
        return render_template('editar.html', paciente=paciente)
    else:
        flash('Paciente no encontrado', 'danger')
        return redirect(url_for('mostrar_pacientes'))

# Ruta para eliminar un paciente
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
    
    return redirect(url_for('mostrar_pacientes'))



if __name__ == '__main__':
    app.run(port=5000, debug=True)
