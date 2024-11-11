from flask import Flask, request, redirect, url_for, flash, render_template, send_from_directory
from flask_mysqldb import MySQL
import os
import re
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'

# Configuración de la base de datos MySQL
app.config['MYSQL_HOST'] = '127.0.0.1'  # Dirección del servidor MySQL
app.config['MYSQL_USER'] = 'root'       # Usuario de la base de datos
app.config['MYSQL_PASSWORD'] = 'Mao123456'  # Contraseña de la base de datos
app.config['MYSQL_DB'] = 'proyecto_practicas'  # Nombre de la base de datos

mysql = MySQL(app)

UPLOAD_FOLDER = 'Carpeta de archivos subidos'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Verificar que la carpeta uploads existe
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Ruta para subir archivos
@app.route('/archivos_registrados', methods=['GET', 'POST'])
def archivos_registrados():
    """Ruta para subir archivos"""
    if request.method == 'POST':
        if 'archivo' not in request.files:
            flash('No se seleccionó ningún archivo', 'error')
            return redirect(request.url)

        archivo = request.files['archivo']

        if archivo.filename == '':
            flash('No se seleccionó ningún archivo', 'error')
            return redirect(request.url)

        if archivo and allowed_file(archivo.filename):
            filename = secure_filename(archivo.filename)
            archivo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash(f'Archivo {filename} subido exitosamente', 'success')
            return redirect(url_for('archivos_registrados'))
        else:
            flash('Tipo de archivo no permitido', 'error')

    # Obtener lista de archivos para mostrar en la página
    archivos = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('archivos_registrados.html', archivos=archivos)

# Ruta para eliminar archivos
@app.route('/eliminar_archivo/<nombre_archivo>', methods=['POST'])
def eliminar_archivo(nombre_archivo):
    """Ruta para eliminar un archivo"""
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], nombre_archivo)
    try:
        os.remove(file_path)
        flash(f'Archivo {nombre_archivo} eliminado correctamente', 'success')
    except Exception as e:
        flash(f'Error al eliminar archivo: {str(e)}', 'error')
    return redirect(url_for('archivos_registrados'))

# Ruta para descargar archivos
@app.route('/descargar_archivo/<nombre_archivo>')
def descargar_archivo(nombre_archivo):
    """Ruta para descargar un archivo"""
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], nombre_archivo, as_attachment=True)
    except Exception as e:
        flash(f'Error al descargar el archivo: {str(e)}', 'error')
        return redirect(url_for('archivos_registrados'))



def validar_usuario(usuario, password):
    """Valida el usuario en el archivo de texto"""
    if os.path.exists('usuarios.txt'):
        with open('usuarios.txt', 'r') as f:
            for line in f:
                user, pwd = line.strip().split(',')
                if user == usuario and pwd == password:
                    return True
    return False

@app.route('/', methods=['GET', 'POST'])
def index():
    """Ruta principal de la aplicación"""
    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password']
        if validar_usuario(usuario, password):
            return redirect(url_for('panel_maestro'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
    return render_template('index.html')

@app.route('/panel_maestro')
def panel_maestro():
    """Panel maestro de administración"""
    return render_template('panel_maestro.html')

@app.route('/registro', methods=['GET', 'POST'])
def registrar():
    """Ruta para registrar un nuevo usuario"""
    if request.method == 'POST':
        nuevo_usuario = request.form['usuario']
        nueva_password = request.form['contraseña']
        if nuevo_usuario and nueva_password:
            with open('usuarios.txt', 'a') as f:
                f.write(f"{nuevo_usuario},{nueva_password}\n")
            flash('Usuario creado exitosamente', 'success')
            return redirect(url_for('index'))
        else:
            flash('Debe llenar ambos campos', 'error')
    return render_template('registro.html')


@app.route('/agregar_estudiante', methods=['GET', 'POST'])
def agregar_estudiante():
    """Ruta para agregar un nuevo estudiante"""
    if request.method == 'POST':
        # Obtener los datos del formulario
        cedula_estudiante = request.form.get('cedula_estudiante')
        nombres = request.form.get('nombres')
        apellidos = request.form.get('apellidos')
        telefono = request.form.get('telefono')
        correo = request.form.get('correo')
        Nombre_Tutor_Academico = request.form.get('Nombre_Tutor_Academico')
        Nombre_Tutor_Empresarial = request.form.get('Nombre_Tutor_Empresarial')
        Nombre_Empresa = request.form.get('Nombre_Empresa')

        # Validación de campos
        if not (cedula_estudiante.isdigit() and nombres and apellidos and telefono and correo and Nombre_Tutor_Academico and Nombre_Tutor_Empresarial and Nombre_Empresa):
            flash('Todos los campos son obligatorios y la cédula debe ser numérica.', 'error')
            return render_template('agregar_estudiante.html')

        # Validar correo electrónico
        if not re.match(r"[^@]+@[^@]+\.[^@]+", correo):
            flash('Correo electrónico no válido.', 'error')
            return render_template('agregar_estudiante.html')

        # Validar número de teléfono (Ejemplo básico para validar un teléfono de 10 dígitos)
        if not re.match(r"^\d{10}$", telefono):
            flash('Número de teléfono no válido. Debe tener 10 dígitos.', 'error')
            return render_template('agregar_estudiante.html')

        # Convertir cédula a entero
        cedula_estudiante = int(cedula_estudiante)

        # Si todo es válido, insertar en la base de datos
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("""
                INSERT INTO estudiante (cedula_estudiante, nombres, apellidos, telefono, correo, Nombre_Tutor_Academico, Nombre_Tutor_Empresarial, Nombre_Empresa)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (cedula_estudiante, nombres, apellidos, telefono, correo, Nombre_Tutor_Academico, Nombre_Tutor_Empresarial, Nombre_Empresa))
            mysql.connection.commit()
            flash('Estudiante agregado correctamente', 'success')
            return redirect(url_for('agregar_estudiante'))
        except Exception as e:
            mysql.connection.rollback()  # Revertir cambios si ocurre un error
            flash(f'Error al agregar estudiante: {str(e)}', 'error')
        finally:
            cursor.close()

    return render_template('agregar_estudiante.html')

@app.route('/agregar_notas', methods=['GET', 'POST'])
def agregar_notas():
    if request.method == 'POST':
        cedula_estudiante = request.form['cedula_estudiante']
        autoevaluacion_tutor_academico = request.form.get('autoevaluacion_tutor_academico', '0') == '1'
        certifiacion_practica = request.form.get('certifiacion_practica', '0') == '1'
        evaluacion_estudiante_tutor = request.form.get('evaluacion_estudiante_tutor', '0') == '1'
        evaluacion_tutor_empresarial = request.form['evaluacion_tutor_empresarial']
        
        # Aquí se agrega la lógica para insertar los datos en la base de datos
        cursor = mysql.connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO evaluacion (
                    cedula_estudiante, 
                    autoevaluacion_tutor_academico, 
                    certifiacion_practica, 
                    evaluacion_estudiante_tutor, 
                    evaluacion_tutor_empresarial
                ) 
                VALUES (%s, %s, %s, %s, %s)
            """, (
                cedula_estudiante, 
                autoevaluacion_tutor_academico, 
                certifiacion_practica, 
                evaluacion_estudiante_tutor, 
                evaluacion_tutor_empresarial
            ))
            mysql.connection.commit()  # Confirmar cambios
            flash('Evaluación guardada correctamente', 'success')
        except Exception as e:
            mysql.connection.rollback()  # Revertir cambios si ocurre un error
            flash(f'Error al guardar la evaluación: {str(e)}', 'error')
        finally:
            cursor.close()

        return redirect(url_for('agregar_notas'))

    return render_template('agregar_notas.html')



@app.route('/agregar_semanas', methods=['GET', 'POST'])
def agregar_semanas():
    """Ruta para agregar información sobre semanas de trabajo de los estudiantes"""
    if request.method == 'POST':
        # Obtener los datos del formulario
        numero_semana = request.form.get('numero_semana')
        fecha_inicio = request.form.get('fecha_inicio')
        fecha_final = request.form.get('fecha_final')  # Cambié 'fecha_fin' a 'fecha_final'
        cedula_estudiante = request.form.get('cedula_estudiante')
        horas_registradas = request.form.get('horas_registradas')
        nota_tutor_academico = request.form.get('nota_tutor_academico')

        # Verificar si todos los campos requeridos fueron proporcionados
        if numero_semana and fecha_inicio and fecha_final and cedula_estudiante and horas_registradas and nota_tutor_academico:
            cursor = mysql.connection.cursor()
            try:
                # Insertar en la tabla 'semana'
                cursor.execute("""INSERT INTO semana (numero_semana, fecha_inicio, fecha_final)
                                  VALUES (%s, %s, %s)""", (numero_semana, fecha_inicio, fecha_final))
                mysql.connection.commit()

                # Insertar en la tabla 'registro_semana'
                cursor.execute("""INSERT INTO registro_semana (numero_semana, cedula_estudiante, horas_registradas, nota_tutor_academico)
                                  VALUES (%s, %s, %s, %s)""", (numero_semana, cedula_estudiante, horas_registradas, nota_tutor_academico))
                mysql.connection.commit()

                flash('Semana y nota agregadas correctamente', 'success')
            except Exception as e:
                mysql.connection.rollback()  # Revertir cambios si ocurre un error
                flash(f'Error al agregar semana: {str(e)}', 'error')
            finally:
                cursor.close()

        return redirect(url_for('agregar_semanas'))

    return render_template('agregar_semanas.html')


@app.route('/agregar_encuentro', methods=['GET', 'POST'])
def agregar_encuentro():
    if request.method == 'POST':
        cedula_estudiante = request.form['cedula_estudiante']
        numero_encuentro = request.form['numero_encuentro']
        nota_encuentro = request.form['nota_encuentro']

        if cedula_estudiante and numero_encuentro and nota_encuentro:
            cursor = mysql.connection.cursor()
            try:
                cursor.execute("""
                    INSERT INTO encuentro (numero_encuentro, cedula_estudiante, nota_encuentro)
                    VALUES (%s, %s, %s)
                """, (numero_encuentro, cedula_estudiante, nota_encuentro))
                mysql.connection.commit()
                flash('Encuentro agregado correctamente', 'success')
            except Exception as e:
                mysql.connection.rollback()
                flash(f'Error al agregar encuentro: {str(e)}', 'error')
            finally:
                cursor.close()

        return redirect(url_for('agregar_encuentro'))

    return render_template('agregar_encuentro.html')

@app.route('/agregar_informe', methods=['GET', 'POST'])
def agregar_informe():
    if request.method == 'POST':
        cedula_estudiante = request.form['cedula_estudiante']
        numero_informe = request.form['numero_informe']
        entrega = request.form.get('entrega', 'off') == 'on'
        nota_evaluacion = request.form['nota_evaluacion']
        nota_sustentacion = request.form['nota_sustentacion']

        if cedula_estudiante and numero_informe:
            cursor = mysql.connection.cursor()
            try:
                # Verificar si la cedula_estudiante existe en la tabla estudiante
                cursor.execute("SELECT COUNT(*) FROM estudiante WHERE cedula_estudiante = %s", (cedula_estudiante,))
                result = cursor.fetchone()
                
                if result[0] == 0:
                    flash('El estudiante no existe. Verifique la cédula.', 'error')
                else:
                    # Si el estudiante existe, insertar el informe
                    cursor.execute("""
                        INSERT INTO informe (numero_informe, cedula_estudiante, entrega, nota_evaluacion, nota_sustentacion)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (numero_informe, cedula_estudiante, entrega, nota_evaluacion, nota_sustentacion))
                    mysql.connection.commit()
                    flash('Informe agregado correctamente', 'success')
            except Exception as e:
                mysql.connection.rollback()
                flash(f'Error al agregar informe: {str(e)}', 'error')
            finally:
                cursor.close()

        return redirect(url_for('agregar_informe'))

    return render_template('agregar_informe.html')



@app.route('/consultas', methods=['GET', 'POST'])
def consultas():
    """Ruta para realizar consultas sobre estudiantes por cédula"""
    if request.method == 'POST':
        cedula = request.form['codigo']  # Asume que el input se llama 'codigo'
        estudiante = buscar_estudiante_por_cedula(cedula)
        if estudiante:
            mensaje = f'Datos del estudiante con cédula {cedula} encontrados.'
        else:
            mensaje = f'Estudiante con cédula {cedula} no encontrado'
            estudiante = None  # Asegúrate de pasar un valor nulo si no se encuentra
        # Redirigimos a una nueva plantilla con los datos del estudiante
        return render_template('resultados.html', mensaje=mensaje, estudiante=estudiante)
    return render_template('consultas.html')


def buscar_estudiante_por_cedula(cedula):
    """Buscar un estudiante en la base de datos usando la cédula"""
    cursor = mysql.connection.cursor()
    cursor.execute('''
    SELECT 
        estudiante.cedula_estudiante, estudiante.nombres, estudiante.apellidos, 
        estudiante.telefono, estudiante.correo, estudiante.Nombre_Tutor_Academico, 
        estudiante.Nombre_Tutor_Empresarial, estudiante.Nombre_Empresa, 
        SUM(registro_semana.horas_registradas) AS horas_totales, 
        AVG(registro_semana.nota_tutor_academico) AS promedio_nota_tutor_academico, 
        AVG(encuentro.nota_encuentro) AS promedio_nota_encuentro, 
        AVG(informe.nota_sustentacion) AS promedio_nota_sustentacion, 
        MAX(evaluacion.evaluacion_tutor_empresarial) AS evaluacion_tutor_empresarial
    FROM estudiante
    LEFT JOIN registro_semana ON estudiante.cedula_estudiante = registro_semana.cedula_estudiante
    LEFT JOIN encuentro ON estudiante.cedula_estudiante = encuentro.cedula_estudiante
    LEFT JOIN informe ON estudiante.cedula_estudiante = informe.cedula_estudiante
    LEFT JOIN evaluacion ON estudiante.cedula_estudiante = evaluacion.cedula_estudiante
    WHERE estudiante.cedula_estudiante = %s
    GROUP BY estudiante.cedula_estudiante
''', (cedula,))

    result = cursor.fetchone()
    cursor.close()
    
    if result:
        return {
            "cedula": result[0],
            "nombres": result[1],
            "apellidos": result[2],
            "telefono": result[3],
            "correo": result[4],
            "Nombre_Tutor_Academico": result[5],
            "Nombre_Tutor_Empresarial": result[6],
            "Nombre_Empresa": result[7],
            "horas_totales": result[8],
            "promedio_nota_tutor_academico": result[9],
            "promedio_nota_encuentro": result[10],
            "promedio_nota_sustentacion": result[11],
            "evaluacion_tutor_empresarial": result[12]
        }
    return None
@app.route('/eliminar', methods=['GET', 'POST'])
def eliminar():
    """Ruta para eliminar un estudiante por cédula"""
    if request.method == 'POST':
        cedula = request.form['codigo']  # La cédula se envía a través de 'codigo' en el formulario
        estudiante = buscar_estudiante_por_cedula(cedula)
        if estudiante:
            # Realizar eliminación en la base de datos
            cursor = mysql.connection.cursor()
            try:
                # Primero, eliminar registros en 'encuentro' que dependan del estudiante
                cursor.execute('DELETE FROM encuentro WHERE cedula_estudiante = %s', (cedula,))
                
                cursor.execute('DELETE FROM evaluacion WHERE cedula_estudiante = %s', (cedula,))

                cursor.execute('DELETE FROM informe WHERE cedula_estudiante = %s', (cedula,))
                
                cursor.execute('DELETE FROM registro_semana WHERE cedula_estudiante = %s', (cedula,))
                
                # Luego, eliminar el estudiante
                cursor.execute('DELETE FROM estudiante WHERE cedula_estudiante = %s', (cedula,))
                
                mysql.connection.commit()
                flash(f'Estudiante con cédula {cedula} eliminado correctamente', 'success')
            except Exception as e:
                mysql.connection.rollback()  # Si ocurre un error, revertimos
                flash(f'Error al eliminar estudiante: {str(e)}', 'error')
            finally:
                cursor.close()
        else:
            flash(f'Estudiante con cédula {cedula} no encontrado', 'error')
    return render_template('eliminar.html')

@app.route('/mostrar_tabla')
def mostrar_tabla():
    """Función para mostrar todos los datos de los estudiantes, incluyendo notas, registros y promedios"""
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("""
            SELECT 
                e.cedula_estudiante, e.nombres, e.apellidos, e.telefono, e.correo, e.Nombre_Tutor_Academico,
                e.Nombre_Tutor_Empresarial, e.Nombre_Empresa,
                COALESCE(SUM(rs.horas_registradas), 0) AS total_horas,
                COALESCE(SUM(rs.nota_tutor_academico) * (0.25 / 16), 0) AS promedio_nota_tutor_academico,
                COALESCE(SUM(enc.nota_encuentro) * (0.09 / 3), 0) AS promedio_nota_encuentros,
                COALESCE(ev.evaluacion_tutor_empresarial * 0.06, 0) AS nota_calificacion_escenario,
                COALESCE(SUM(inf.nota_sustentacion) * (0.6 / 2), 0) AS promedio_nota_sustentacion
            FROM estudiante e
            LEFT JOIN registro_semana rs ON e.cedula_estudiante = rs.cedula_estudiante
            LEFT JOIN encuentro enc ON e.cedula_estudiante = enc.cedula_estudiante
            LEFT JOIN informe inf ON e.cedula_estudiante = inf.cedula_estudiante
            LEFT JOIN evaluacion ev ON e.cedula_estudiante = ev.cedula_estudiante
            GROUP BY e.cedula_estudiante
        """)

        # Recupera todos los resultados de la consulta
        estudiantes = cursor.fetchall()
        # Imprime los resultados para verificar que se están recuperando correctamente
        print("Datos recuperados:", estudiantes)  # Depuración

    except Exception as e:
        flash(f'Error al recuperar datos: {str(e)}', 'error')
        estudiantes = []
    finally:
        cursor.close()

    # Pasar los datos a la plantilla
    return render_template('mostrar_tabla.html', estudiantes=estudiantes)




if __name__ == '__main__':
    app.run(debug=True)




