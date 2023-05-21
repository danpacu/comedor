import mysql.connector

# Configuración de la base de datos MySQL
host = 'localhost'
user = 'comedor'
contraseña = '1213'
base_de_datos = 'comedor'

# Función para crear la tabla de clases si no existe
def crear_tabla_clases():
    conexion = mysql.connector.connect(host=host, user=user, password=contraseña, database=base_de_datos)
    cursor = conexion.cursor()

    # Crear la tabla de clases si no existe
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clases (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(10)
        )
    """)

    conexion.commit()
    cursor.close()
    conexion.close()

# Función para agregar una nueva clase a la tabla
def agregar_clase(nombre_clase):
    conexion = mysql.connector.connect(host=host, user=user, password=contraseña, database=base_de_datos)
    cursor = conexion.cursor()

    # Insertar la nueva clase en la tabla
    consulta = "INSERT INTO clases (nombre) VALUES (%s)"
    valores = (nombre_clase,)
    cursor.execute(consulta, valores)

    conexion.commit()
    cursor.close()
    conexion.close()

# Función para obtener la lista de clases
def obtener_lista_clases():
    conexion = mysql.connector.connect(host=host, user=user, password=contraseña, database=base_de_datos)
    cursor = conexion.cursor()

    # Obtener la lista de clases
    cursor.execute("SELECT * FROM clases")
    lista_clases = cursor.fetchall()

    cursor.close()
    conexion.close()

    return lista_clases

# Función para correlacionar clases con asistencia al comedor y generar vista del mes
def comedor():
    conexion = mysql.connector.connect(host=host, user=user, password=contraseña, database=base_de_datos)
    cursor = conexion.cursor()

    # Obtener la lista de clases
    cursor.execute("SELECT * FROM clases")
    lista_clases = cursor.fetchall()

    for clase in lista_clases:
        nombre_clase = clase[1]

        # Crear una vista para la clase en la base de datos
        cursor.execute(f"CREATE OR REPLACE VIEW vista_{nombre_clase} AS SELECT * FROM comedor WHERE clase = '{nombre_clase}'")

        # Generar la vista del mes
        cursor.execute(f"SELECT * FROM vista_{nombre_clase} WHERE fecha BETWEEN '2023-05-01' AND '2023-05-31'")
        vista_mes = cursor.fetchall()

        print(f"Vista del mes para la clase {nombre_clase}:")
        for registro in vista_mes:
            print(registro)

    cursor.close()
    conexion.close()
