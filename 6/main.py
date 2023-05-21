
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from io import BytesIO
import mysql.connector
from telebot.types import Message
import telebot

from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
import calendar
from datetime import datetime

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
    /comedor - Registrar asistencia al comedor para una clase
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
    bot.reply_to(message, "Ingrese la clase:")
    bot.register_next_step_handler(message, handle_clase_comprueba)

def handle_clase_comprueba(message):
    clase = message.text
    # Obtén los alumnos de la clase desde la base de datos
    cursor = db_connection.cursor()
    select_query = "SELECT nombre FROM alumnos WHERE clase = %s"
    values = (clase,)
    cursor.execute(select_query, values)
    alumnos_clase = cursor.fetchall()
    cursor.close()

    if alumnos_clase:
        lista_alumnos = "\n".join([alumno[0] for alumno in alumnos_clase])
        bot.reply_to(message, f"Alumnos de la clase {clase}:\n{lista_alumnos}")
    else:
        bot.reply_to(message, f"No hay alumnos registrados en la clase {clase}.")



@bot.message_handler(commands=['comedor'])
def comedor(message):
    bot.reply_to(message, "Ingrese la clase:")
    bot.register_next_step_handler(message, handle_clase_comedor)

def handle_clase_comedor(message):
    clase = message.text
    # Obtén los alumnos de la clase desde la base de datos
    cursor = db_connection.cursor()
    select_query = "SELECT nombre FROM alumnos WHERE clase = %s"
    values = (clase,)
    cursor.execute(select_query, values)
    alumnos_clase = cursor.fetchall()
    cursor.close()

    if alumnos_clase:
        # Obtén solo los nombres de los alumnos de la lista de resultados
        alumnos = [alumno[0] for alumno in alumnos_clase]
        bot.reply_to(message, f"Inicia el registro de asistencia al comedor para la clase {clase}.")
        registrar_asistencia_comedor(message.chat.id, clase, alumnos, [])
    else:
        bot.reply_to(message, f"No hay alumnos registrados en la clase {clase}.")
        bot.reply_to(message, "Operación cancelada.")

def registrar_asistencia_comedor(chat_id, clase, alumnos_clase, asistencias):
    if len(alumnos_clase) > 0:
        alumno = alumnos_clase[0]
        bot.send_message(chat_id, f"¿El alumno {alumno} se queda a comedor? (Sí/No)")
        bot.register_next_step_handler_by_chat_id(chat_id, lambda msg: handle_asistencia_comedor(msg, clase, alumnos_clase, asistencias))
    else:
        # Se han revisado todos los alumnos de la clase
        # Mostrar resultados y preguntar si se desea registrar asistencia para otra clase
        mostrar_resultados_asistencia(chat_id, clase, alumnos_clase, asistencias)
        bot.send_message(chat_id, "¿Desea registrar asistencia al comedor para otra clase? (Sí/No)")
        bot.register_next_step_handler_by_chat_id(chat_id, handle_otra_clase_comedor)

def handle_asistencia_comedor(message, clase, alumnos_clase, asistencias):
    respuesta = message.text.lower()
    if respuesta == "si":
        asistencias.append(True)
    elif respuesta == "no":
        asistencias.append(False)
    else:
        bot.send_message(message.chat.id, "Respuesta inválida. Por favor, responda con 'Sí' o 'No'.")

    # Luego, puedes llamar a la función para registrar la asistencia del siguiente alumno
    registrar_asistencia_comedor(message.chat.id, clase, alumnos_clase[1:], asistencias)

def handle_otra_clase_comedor(message):
    respuesta = message.text.lower()
    if respuesta == "sí":
        bot.reply_to(message, "Ingrese la nueva clase:")
        bot.register_next_step_handler(message, handle_clase_comedor)
    elif respuesta == "no":
        bot.send_message(message.chat.id, "Registro de asistencia al comedor finalizado.")
    else:
        bot.send_message(message.chat.id, "Respuesta inválida. Por favor, responda con 'Sí' o 'No'.")

def mostrar_resultados_asistencia(chat_id, clase, alumnos_clase, asistencias):
    mensaje = f"Resultados de asistencia al comedor para la clase {clase}:\n"
    for i, alumno in enumerate(alumnos_clase):
        asistencia = "Asistió" if asistencias[i] else "No asistió"
        mensaje += f"- {alumno}: {asistencia}\n"
    bot.send_message(chat_id, mensaje)


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
    select_query = "SELECT nombre, comensal_musulman FROM alumnos WHERE clase = %s"
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
    header = ["Nombre"] + dias_mes
    data.append(header)

    comensales_musulmanes = [0] * len(dias_mes)
    comensales_no_musulmanes = [0] * len(dias_mes)

    for alumno in alumnos_clase:
        fila_alumno = [alumno[0]]
        for dia in dias_mes:
            if alumno[1] == "Sí":
                comensales_musulmanes[dias_mes.index(dia)] += 1
                fila_alumno.append("✓")
            elif alumno[1] == "No":
                comensales_no_musulmanes[dias_mes.index(dia)] += 1
                fila_alumno.append("✓")
            else:
                comensales_no_musulmanes[dias_mes.index(dia)] += 1
                fila_alumno.append("")
        data.append(fila_alumno)

    fila_comensales_musulmanes = ["Comensales Musulmanes"] + comensales_musulmanes
    fila_comensales_no_musulmanes = ["Comensales No Musulmanes"] + comensales_no_musulmanes
    data.append(fila_comensales_musulmanes)
    data.append(fila_comensales_no_musulmanes)

    table = Table(data)
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])
    table.setStyle(style)

    elements = [table]

    # Dibujar el contenido en el canvas
    table.wrapOn(canvas_obj, 50, 50)
    table.drawOn(canvas_obj, 50, 50)

    # Guardar el canvas en el buffer
    canvas_obj.save()

    pdf_buffer.seek(0)
    return pdf_buffer


def obtener_dias_del_mes(mes: str):
    mes_numero = obtener_numero_mes(mes)
    year = datetime.now().year

    if mes_numero is None:
        mes_numero = 1  # Asignar un valor predeterminado
        print("Advertencia: El valor del mes es None. Se utilizará el mes 1 por defecto.")

    _, num_dias = calendar.monthrange(year, mes_numero)

    dias_mes = [str(i) for i in range(1, num_dias + 1)]
    return dias_mes


def obtener_numero_mes(mes: str):
    meses = {
        'enero': 1,
        'febrero': 2,
        'marzo': 3,
        'abril': 4,
        'mayo': 5,
        'junio': 6,
        'julio': 7,
        'agosto': 8,
        'septiembre': 9,
        'octubre': 10,
        'noviembre': 11,
        'diciembre': 12
    }
    return meses.get(mes.lower(), None)

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
