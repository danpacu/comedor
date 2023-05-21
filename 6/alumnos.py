import mysql.connector

# Configuración de la base de datos MySQL
host = 'localhost'
user = 'comedor'
contraseña = '1213'
base_de_datos = 'comedor'

# Función para crear la tabla de alumnos si no existe
def crear_tabla_alumnos():
    conexion = mysql.connector.connect(host=host, user=user, password=contraseña, database=base_de_datos)
    cursor = conexion.cursor()

    # Crear la tabla de alumnos si no existe
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alumnos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100),
            apellidos VARCHAR(100),
            musulman BOOLEAN,
            beca BOOLEAN,
            clase VARCHAR(10)
        )
    """)
        # Crear la tabla asistencia_comedor si no existe
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS asistencia_comedor (
    id INT AUTO_INCREMENT PRIMARY KEY,
    alumno VARCHAR(255),
    clase VARCHAR(255),
    respuesta VARCHAR(255)
    )
    '''
    db_cursor.execute(create_table_query)

    conexion.commit()
    cursor.close()
    conexion.close()

# Función para agregar un nuevo alumno a la tabla
def agregar_alumno(nombre, apellidos, musulman, beca, clase):
    conexion = mysql.connector.connect(host=host, user=user, password=contraseña, database=base_de_datos)
    cursor = conexion.cursor()

    # Insertar el nuevo alumno en la tabla
    consulta = "INSERT INTO alumnos (nombre, apellidos, musulman, beca, clase) VALUES (%s, %s, %s, %s, %s)"
    valores = (nombre, apellidos, musulman, beca, clase)
    cursor.execute(consulta, valores)

    conexion.commit()
    cursor.close()
    conexion.close()

# Función para obtener la lista de alumnos
def obtener_lista_alumnos():
    conexion = mysql.connector.connect(host=host, user=user, password=contraseña, database=base_de_datos)
    cursor = conexion.cursor()

    # Obtener la lista de alumnos
    cursor.execute("SELECT * FROM alumnos")
    lista_alumnos = cursor.fetchall()

    cursor.close()
    conexion.close()

    return lista_alumnos
