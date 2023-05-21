from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from io import BytesIO
import mysql.connector
from telebot.types import Message
import telebot
import calendar
from datetime import datetime
from reportlab.pdfgen import canvas


bot = telebot.TeleBot("")

def conectar_base_datos():
    # Establecer la conexión con la base de datos MySQL
    db_connection = mysql.connector.connect(
        host="localhost",
        user="comedor",
        password="1213",
        database="comedor"
    )
    return db_connection

db_connection = conectar_base_datos()


# Variables para controlar el estado de la asistencia al comedor
clase_actual = ""
alumnos_clase = []
indice_alumno = 0

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "¡Bienvenido! Usa /help para ver la lista de comandos disponibles.")

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = """
    Lista de comandos disponibles:
    /start - Iniciar el bot
    /help - Mostrar la lista de comandos disponibles
    /add_alumno - Añadir un alumno a una clase
    /add_clase - Añadir una clase a la base de datos
    /comprueba - Mostrar los alumnos de una clase
    /comedor - Registrar asistencia al comedor para un alumno
    /listado - Generar un listado en formato PDF
    /borrar_alumno - Borrar un alumno de una clase
    """
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['add_alumno'])
def add_alumno(message):
    bot.reply_to(message, "Ingrese el nombre del alumno:")
    bot.register_next_step_handler(message, handle_alumno)

def handle_alumno(message):
    nombre_alumno = message.text
    bot.reply_to(message, "Ingrese la clase:")
    bot.register_next_step_handler(message, handle_clase, nombre_alumno)

def handle_clase(message, nombre_alumno):
    clase = message.text
    bot.reply_to(message, "¿Es musulmán el alumno? (Sí/No):")
    bot.register_next_step_handler(message, handle_musulman, nombre_alumno, clase)

def handle_musulman(message, nombre_alumno, clase):
    musulman = message.text
    bot.reply_to(message, "¿Tiene beca el alumno? (Sí/No):")
    bot.register_next_step_handler(message, lambda msg: handle_beca(msg, nombre_alumno, clase, musulman))

def handle_beca(message, nombre_alumno, clase, musulman):
    beca = message.text.lower()  # Convertir a minúsculas para facilitar la comparación
    if beca == 'sí':
        beca = 1
    else:
        beca = 0
        

    # Insertar el alumno en la base de datos
    cursor = db_connection.cursor()
    insert_query = "INSERT INTO alumnos (nombre, clase, beca) VALUES (%s, %s, %s)"
    values = (nombre_alumno, clase, beca)
    cursor.execute(insert_query, values)
    db_connection.commit()
    cursor.close()

    bot.reply_to(message, f"Alumno {nombre_alumno} agregado a la clase {clase} con beca {beca}.")

@bot.message_handler(commands=['add_clase'])
def add_clase(message):
    bot.reply_to(message, "Ingrese el nombre de la clase:")
    bot.register_next_step_handler(message, handle_clase_add_clase)

def handle_clase_add_clase(message):
    clase = message.text
    # Guardar la clase en la base de datos
    cursor = db_connection.cursor()
    insert_query = "INSERT INTO clases (nombre) VALUES (%s)"
    values = (clase,)
    cursor.execute(insert_query, values)
    db_connection.commit()
    cursor.close()

    bot.reply_to(message, f"Clase {clase} añadida.")

@bot.message_handler(commands=['comprueba'])
def comprueba(message):
    bot.reply_to(message, "Ingrese el nombre de la clase:")
    bot.register_next_step_handler(message, handle_comprueba)

def handle_comprueba(message):
    clase = message.text

    # Obtener la lista de alumnos de la clase
    cursor = db_connection.cursor()
    select_query = "SELECT nombre FROM alumnos WHERE clase = %s"
    values = (clase,)
    cursor.execute(select_query, values)
    alumnos = cursor.fetchall()
    cursor.close()

    if alumnos:
        alumno_list = "\n".join([alumno[0] for alumno in alumnos])
        bot.reply_to(message, f"Los alumnos de la clase {clase} son:\n{alumno_list}")
    else:
        bot.reply_to(message, f"No se encontraron alumnos en la clase {clase}.")

# Manejar comando /comedor
@bot.message_handler(commands=['comedor'])
def handle_comedor(message):
    bot.reply_to(message, "¿De qué clase quieres anotar la asistencia al comedor?")
    bot.register_next_step_handler(message, obtener_clase)

def obtener_clase(message):
    clase = message.text
    bot.reply_to(message, f"Clase seleccionada: {clase}\nAhora, por cada alumno, responde si se queda a comedor o no.")

    # Obtener lista de alumnos de la clase desde la base de datos
    select_query = "SELECT nombre_alumno FROM alumnos WHERE clase = %s"
    db_cursor.execute(select_query, (clase,))
    alumnos_clase = db_cursor.fetchall()

    # Iniciar el proceso de obtención de respuestas
    obtener_respuesta_comedor(message, clase, alumnos_clase)

def obtener_respuesta_comedor(message, clase, alumnos_clase):
    if len(alumnos_clase) > 0:
        alumno = alumnos_clase.pop(0)[0]
        bot.reply_to(message, f"¿El alumno {alumno} se queda a comedor? (Sí/No)")
        bot.register_next_step_handler(message, registrar_respuesta_comedor, clase, alumnos_clase, alumno)
    else:
        finalizar_registro_comedor(message)

def registrar_respuesta_comedor(message, clase, alumnos_clase, alumno):
    respuesta = message.text.lower()

    # Insertar en la base de datos la respuesta del alumno
    insert_query = "INSERT INTO asistencia_comedor (alumno, clase, respuesta) VALUES (%s, %s, %s)"
    db_cursor.execute(insert_query, (alumno, clase, '✔️' if respuesta == 'si' else ''))
    db_connection.commit()

    # Obtener siguiente respuesta
    obtener_respuesta_comedor(message, clase, alumnos_clase)

def finalizar_registro_comedor(message):
    bot.reply_to(message, "Has finalizado el registro de asistencia al comedor.")


@bot.message_handler(commands=['borrar_alumno'])
def borrar_alumno(message):
    bot.reply_to(message, "Ingrese la clase:")
    bot.register_next_step_handler(message, handle_borrar_alumno)

def handle_borrar_alumno(message):
    clase = message.text
    # Obtener la lista de alumnos de la clase
    cursor = db_connection.cursor()
    select_query = "SELECT nombre FROM alumnos WHERE clase = %s"
    values = (clase,)
    cursor.execute(select_query, values)
    alumnos = cursor.fetchall()
    cursor.close()

    if alumnos:
        alumno_list = "\n".join([alumno[0] for alumno in alumnos])
        bot.reply_to(message, f"Los alumnos de la clase {clase} son:\n{alumno_list}")
        bot.reply_to(message, "Ingrese el nombre del alumno a borrar:")
        bot.register_next_step_handler(message, handle_confirm_borrar_alumno, clase)
    else:
        bot.reply_to(message, f"No se encontraron alumnos en la clase {clase}.")

def handle_confirm_borrar_alumno(message, clase):
    nombre_alumno = message.text

    # Borrar el alumno de la base de datos
    cursor = db_connection.cursor()
    delete_query = "DELETE FROM alumnos WHERE nombre = %s AND clase = %s"
    values = (nombre_alumno, clase)
    cursor.execute(delete_query, values)
    db_connection.commit()
    cursor.close()

    bot.reply_to(message, f"Alumno {nombre_alumno} borrado de la clase {clase}.")

@bot.message_handler(commands=['listado'])
def generar_listado_pdf(message):
    chat_id = message.chat.id
    # Solicitar la clase al usuario
    bot.send_message(chat_id, "Ingrese la clase:")
    bot.register_next_step_handler(message, obtener_clase)


def obtener_clase(message):
    chat_id = message.chat.id
    clase = message.text

    # Solicitar el mes al usuario
    bot.send_message(chat_id, "Ingrese el mes:")
    bot.register_next_step_handler(message, obtener_mes, clase)


def obtener_mes(message, clase):
    chat_id = message.chat.id
    mes = message.text

    # Generar el listado PDF
    pdf_buffer = generar_listado_pdf_func(clase, mes)

    # Enviar el archivo PDF al usuario
    bot.send_document(chat_id, pdf_buffer)


def generar_listado_pdf_func(clase: str, mes: str):
    cursor = db_connection.cursor()
    select_query = "SELECT nombre, comensal_musulman, beca FROM alumnos WHERE clase = %s"
    values = (clase,)
    cursor.execute(select_query, values)
    alumnos_clase = cursor.fetchall()
    cursor.close()

    dias_mes = obtener_dias_del_mes(mes)

    pdf_buffer = BytesIO()

    # Crear el objeto canvas
    canvas_obj = canvas.Canvas(pdf_buffer, pagesize=landscape(A4))

    # Ajustar tamaño de página a A4 horizontal
    canvas_obj.setPageSize(landscape(A4))

    data = []
    header = ["Nombre"] + dias_mes + ["Comensal Musulmán", "Beca"]
    data.append(header)

    comensales_musulmanes = [0] * len(dias_mes)
    comensales_no_musulmanes = [0] * len(dias_mes)
    becas = [0] * len(dias_mes)
    dias_comedor = [1, 2, 3, 4, 5]  # Reemplaza con los días correspondientes

    for alumno in alumnos_clase:
        fila_alumno = [alumno[0]]
        for dia in dias_mes:
            if dia in dias_comedor:
                if alumno[1] == "Sí":
                    comensales_musulmanes[dias_mes.index(dia)] += 1
                fila_alumno.append("✓")
            elif alumno[1] == "No":
                comensales_no_musulmanes[dias_mes.index(dia)] += 1
                fila_alumno.append("✓")
            else:
                comensales_no_musulmanes[dias_mes.index(dia)] += 1
                fila_alumno.append("")
        else:
            fila_alumno.append("")

        if alumno[2] == "Sí":
            becas[dias_mes.index(dia)] += 1
        elif alumno[2] == "No":
            becas[dias_mes.index(dia)] += 1
        else:
            becas[dias_mes.index(dia)] += 1

        fila_alumno.append(alumno[1])
        fila_alumno.append(alumno[2])
        data.append(fila_alumno)

    fila_comensales_musulmanes = ["Comensales Musulmanes"] + comensales_musulmanes + [""]
    fila_comensales_no_musulmanes = ["Comensales No Musulmanes"] + comensales_no_musulmanes + [""]
    fila_becas = ["Becas"] + becas + [""]
    data.append(fila_comensales_musulmanes)
    data.append(fila_comensales_no_musulmanes)
    data.append(fila_becas)

    # Crear la tabla
    tabla = Table(data)
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 11),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
    ]))

    # Obtener el tamaño de la tabla y calcular la altura de las filas
    table_width, table_height = tabla.wrapOn(canvas_obj, landscape(A4)[0] - 80, 0)
    row_heights = [18] + [14] * len(data[1:]) + [15]

    # Obtener la altura disponible en la página
    available_height = landscape(A4)[1] - 80  # Margen superior e inferior de 40

    # Verificar si la tabla cabe en la página
    if table_height > available_height:
        # La tabla no cabe en la página, dividirla en múltiples páginas
        paginas = tabla.split(landscape(A4)[0], table_height)
        for i, pagina in enumerate(paginas):
            # Crear la página
            canvas_obj.showPage()
            canvas_obj.setFont('Helvetica-Bold', 11)
            canvas_obj.drawString(40, landscape(A4)[1] - 40, f"Clase: {clase} - Mes: {mes}")
            canvas_obj.setFont('Helvetica', 11)
            canvas_obj.drawString(40, landscape(A4)[1] - 60, f"Página {i+1}")

            # Dibujar la tabla en la página
            tabla_copiada = copy.deepcopy(pagina)
            tabla_copiada.wrapOn(canvas_obj, landscape(A4)[0] - 80, available_height)
            tabla_copiada.drawOn(canvas_obj, 40, landscape(A4)[1] - 80 - sum(row_heights[:len(pagina._argH)]))

    else:
        # La tabla cabe en una sola página
        # Crear la página
        canvas_obj.showPage()
        canvas_obj.setFont('Helvetica-Bold', 14)
        canvas_obj.drawString(40, landscape(A4)[1] - 40, f"Clase: {clase} - Mes: {mes}")
        canvas_obj.setFont('Helvetica', 12)
        canvas_obj.drawString(40, landscape(A4)[1] - 60, f"Página 1")

        # Dibujar la tabla en la página
        tabla.wrapOn(canvas_obj, landscape(A4)[0] - 80, available_height)
        tabla.drawOn(canvas_obj, 40, landscape(A4)[1] - 80 - sum(row_heights))

    # Guardar el objeto canvas en el buffer
    canvas_obj.save()

    # Mover el puntero del buffer al inicio
    pdf_buffer.seek(0)

    return pdf_buffer



def obtener_dias_del_mes(mes):
    # Obtener el número de días del mes
    if mes.lower() in ("enero", "marzo", "mayo", "julio", "agosto", "octubre", "diciembre"):
        return list(range(1, 32))
    elif mes.lower() in ("abril", "junio", "septiembre", "noviembre"):
        return list(range(1, 31))
    elif mes.lower() == "febrero":
        return list(range(1, 29))
    else:
        return []

@bot.message_handler(commands=['borrar_alumno'])
def borrar_alumno(message):
    bot.reply_to(message, "Ingrese el nombre de la clase:")
    bot.register_next_step_handler(message, handle_borrar_alumno_clase)


def handle_borrar_alumno_clase(message):
    clase = message.text
    # Obtener la lista de alumnos de la clase
    cursor = db_connection.cursor()
    select_query = "SELECT nombre FROM alumnos WHERE clase = %s"
    values = (clase,)
    cursor.execute(select_query, values)
    alumnos = cursor.fetchall()
    cursor.close()

    if alumnos:
        alumno_list = "\n".join([alumno[0] for alumno in alumnos])
        bot.reply_to(message, f"Los alumnos de la clase {clase} son:\n{alumno_list}")
        bot.reply_to(message, "Ingrese el nombre del alumno que desea borrar:")
        bot.register_next_step_handler(message, handle_borrar_alumno_nombre, clase)
    else:
        bot.reply_to(message, f"No se encontraron alumnos en la clase {clase}.")


def handle_borrar_alumno_nombre(message, clase):
    nombre_alumno = message.text

    # Eliminar el alumno de la base de datos
    cursor = db_connection.cursor()
    delete_query = "DELETE FROM alumnos WHERE nombre = %s AND clase = %s"
    values = (nombre_alumno, clase)
    cursor.execute(delete_query, values)
    db_connection.commit()
    cursor.close()

    bot.reply_to(message, f"Alumno {nombre_alumno} eliminado de la clase {clase}.")

bot.polling()
