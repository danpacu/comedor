from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import datetime
import mysql.connector



def obtener_alumnos_por_clase(clase, db_connection):
    cursor = db_connection.cursor()
    select_query = "SELECT nombre FROM alumnos WHERE clase = %s"
    values = (clase,)
    cursor.execute(select_query, values)
    alumnos_clase = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return alumnos_clase

def generar_pdf():
    # Conexión a la base de datos
    db_config = {
        'host': 'localhost',
        'user': 'comedor',
        'password': '1213',
        'database': 'comedor'
    }
    db_connection = mysql.connector.connect(**db_config)

    # Obtener la orientación del PDF del usuario
    orientacion = input("Ingrese la orientación del PDF (vertical/horizontal): ")
    if orientacion.lower() == "vertical":
        tamaño_pagina = letter
    else:
        tamaño_pagina = landscape(letter)

    # Obtener la clase y el mes del usuario
    clase = input("Ingrese la clase: ")
    mes = input("Ingrese el mes: ")

    # Obtener la lista de alumnos de la clase seleccionada
    lista_alumnos = obtener_alumnos_por_clase(clase, db_connection)

    # Generar el PDF
    pdf = canvas.Canvas("reporte_comedor.pdf", pagesize=tamaño_pagina)

    # Configurar el tamaño y posición del tick
    tamaño_tick = 0.2 * inch
    posición_inicial_x = 1 * inch
    posición_inicial_y = 1 * inch

    # Calcular la posición del tick para cada día del mes
    fecha_inicio = datetime.datetime.strptime(f"01-{mes}", "%d-%m").date()
    fecha_fin = fecha_inicio.replace(day=28) + datetime.timedelta(days=4)
    días_mes = (fecha_fin - fecha_inicio).days + 1
    posición_x = posición_inicial_x
    posición_y = posición_inicial_y
    ticks_por_fila = 7

    # Generar los ticks en el PDF para cada alumno y cada día del mes
    for alumno in lista_alumnos:
        posición_x = posición_inicial_x
        posición_y -= tamaño_tick

        # Escribir el nombre del alumno
        pdf.drawString(posición_x - 0.8 * inch, posición_y, alumno)

        # Calcular la posición inicial para los ticks del alumno
        posición_x += 0.2 * inch
        posición_y -= 0.4 * inch

        for día in range(1, días_mes + 1):
            # Calcular la posición del tick en función del día y la fila
            fila = (día - 1) // ticks_por_fila
            columna = (día - 1) % ticks_por_fila
            posición_x = posición_inicial_x + columna * tamaño_tick
            posición_y = posición_inicial_y - fila * tamaño_tick

            # Dibujar el tick si el alumno se quedó al comedor ese día
            if alumno_asistió_comedor(alumno, fecha_inicio + datetime.timedelta(days=día - 1), db_connection):
                pdf.rect(posición_x, posición_y, tamaño_tick, tamaño_tick, fill=True)

    # Guardar el PDF generado
    pdf.save()

# Verificar si un alumno asistió al comedor en una fecha específica
def alumno_asistió_comedor(alumno, fecha, db_connection):
    cursor = db_connection.cursor()
    sql = "SELECT asistio FROM asistencia_comedor WHERE alumno_id = %s AND fecha = %s"
    values = (alumno, fecha)
    cursor.execute(sql, values)
    result = cursor.fetchone()
    cursor.close()
    return result is not None and result[0] > 0

# Ejecutar la función para generar el PDF
generar_pdf()
