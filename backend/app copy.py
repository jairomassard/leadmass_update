import os
import json
import base64
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import requests
import threading
import psycopg2
import pandas as pd
import pytz
from datetime import datetime
from fpdf import FPDF
from flask import make_response
from email.mime.text import MIMEText
from google.oauth2 import service_account
from googleapiclient.discovery import build
from twilio.rest import Client
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, To
from pytz import timezone
from concurrent.futures import ThreadPoolExecutor, TimeoutError


# Cargar las variables del archivo .env
load_dotenv()

# Ahora puedes acceder a SENDGRID_API_KEY con os.environ
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')

app = Flask(__name__, static_folder="static/dist")

# Permitir solicitudes desde cualquier parte
# CORS(app)
CORS(app, resources={r"/*": {"origins": "*"}})


conn = psycopg2.connect(
    host=os.getenv("PGHOST"),
    database=os.getenv("PGDATABASE"),
    user=os.getenv("PGUSER"),
    password=os.getenv("PGPASSWORD"),
    port=os.getenv("PGPORT")
)


cursor = conn.cursor()

# Configurar la zona horaria a 'America/Bogota' después de la conexión
cursor.execute("SET timezone = 'America/Bogota';")

# Configuración de Twilio usando variables de entorno
ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER')
CONTENT_SID = os.getenv('TWILIO_CONTENT_SID')
client = Client(ACCOUNT_SID, AUTH_TOKEN)

# Función para obtener la hora de Colombia
def get_current_time_colombia():
    """Obtiene la hora actual en la zona horaria de Colombia."""
    colombia_tz = timezone("America/Bogota")
    return datetime.now(colombia_tz)

# Función para obtener usuario por nombre y contraseña
def obtener_usuario(usuario, password):
    query = "SELECT * FROM usuarios WHERE usuario = %s AND password = %s"
    cursor.execute(query, (usuario, password))
    user = cursor.fetchone()
    if user:
        return {
            'id': user[0],
            'usuario': user[1],
            'password': user[2],
            'concesionario': user[3],
            'es_administrador': user[4],
            'tipo_usuario': user[5],
            'fecha_creacion': user[6],
            'activo': user[7]
        }
    return None

# Asignar nuevo lead automatico
def asignar_nuevo_lead_automatico(vendedor_id):
    print(f"🚀 Intentando asignar un nuevo lead al vendedor {vendedor_id}...")

    # Obtener la información del vendedor
    cursor.execute("SELECT concesionario FROM usuarios WHERE id = %s", (vendedor_id,))
    concesionario_nombre = cursor.fetchone()

    if not concesionario_nombre:
        print("❌ No se encontró concesionario para este vendedor.")
        return

    # Obtener ID del concesionario
    cursor.execute("SELECT id FROM concesionarios WHERE nombre_concesionario = %s", (concesionario_nombre,))
    resultado = cursor.fetchone()

    if not resultado:
        print(f"❌ Error: No se encontró el ID del concesionario para '{concesionario_nombre}'.")
        return

    concesionario_id = resultado[0]  # Ahora es un número

    print(f"✅ Concesionario ID obtenido: {concesionario_id}")

    # Buscar leads en este concesionario
    cursor.execute("""
        SELECT id FROM leads 
        WHERE concesionario_id = %s 
        AND estatus = 'nuevo' 
        AND asignado = false 
        LIMIT 1
    """, (concesionario_id,))
    
    lead_disponible = cursor.fetchone()

    if not lead_disponible:
        print("🚫 No hay leads disponibles en este concesionario.")
        return
    
    lead_id = lead_disponible[0]

    # Asignar el lead al vendedor
    fecha_asignacion = get_current_time_colombia()
    cursor.execute("""
        UPDATE leads 
        SET asignado_a = %s, estatus = 'asignado', asignado = true, fecha_asignacion = %s 
        WHERE id = %s
    """, (vendedor_id, fecha_asignacion, lead_id))
    
    conn.commit()
    print(f"✅ Lead {lead_id} asignado automáticamente al vendedor {vendedor_id}.")


# Función para crear el PDF
def create_pdf(leads, vendedor=None, filtro_estado=None, filtroTestDrive=None, vendedor_nombre_completo=None):
    pdf = FPDF(orientation='L')  # 'L' establece la orientación horizontal
    pdf.add_page()
    
    # Reducir los márgenes para aprovechar mejor el espacio
    pdf.set_left_margin(5)
    pdf.set_right_margin(5)

    pdf.set_font("Arial", "B", 10)

    # Encabezado del reporte
    pdf.cell(0, 10, "Reporte de Leads", 0, 1, "C")
    pdf.set_font("Arial", size=9)

    # Incluir el filtro aplicado en el encabezado
    if vendedor_nombre_completo:
        pdf.cell(0, 8, f"Leads de Vendedor: {vendedor_nombre_completo}", 0, 1, "L")
    if filtro_estado:
        pdf.cell(0, 8, f"Filtro de Estado: {filtro_estado}", 0, 1, "L")
    if filtroTestDrive:
        pdf.cell(0, 8, f"Filtro de Estado: {filtroTestDrive}", 0, 1, "L")    
    pdf.ln(5)  # Espacio entre encabezado y tabla

    # Cabeceras de la tabla (sin el "ID")
    column_headers = ["Nombres", "Apellidos", "Identificación", "Teléfono", "Dirección", 
                      "Ciudad", "Correo", "Fecha Lead", "Origen Lead", "Marca de Interés", 
                      "Modelo Interesado", "Estatus", "Test Drive", "Seguimientos"]

    # Calcular ancho de cada columna para que encajen en la página (sin el "ID")
    page_width = pdf.w - 10  # Restar márgenes
    col_width = page_width / len(column_headers)  # Ancho calculado dinámicamente

    pdf.set_font("Arial", "B", 6)
    for header in column_headers:
        pdf.cell(col_width, 6, header, 1, 0, "C")
    pdf.ln()

    # Función para ajustar texto en cada celda
    def fit_text_in_cell(text, width):
        if text is None:
            text = ""
        max_chars = int(width / 1.3)  # Ajuste según el ancho de la columna
        if len(text) > max_chars:
            return text[:max_chars - 3] + "..."  # Truncar con "..."
        return text

    # Contenido de los leads (sin la columna "ID")
    pdf.set_font("Arial", size=7)  # Tamaño de fuente más pequeño para el contenido
    for lead in leads:
        pdf.cell(col_width, 6, fit_text_in_cell(str(lead.get("vendedor_nombre", "")), col_width), 1)
        pdf.cell(col_width, 6, fit_text_in_cell(lead.get("nombres", ""), col_width), 1)
        pdf.cell(col_width, 6, fit_text_in_cell(lead.get("apellidos", ""), col_width), 1)
        pdf.cell(col_width, 6, fit_text_in_cell(lead.get("identificacion", ""), col_width), 1)
        pdf.cell(col_width, 6, fit_text_in_cell(lead.get("telefono", ""), col_width), 1)
        pdf.cell(col_width, 6, fit_text_in_cell(lead.get("direccion", ""), col_width), 1)
        pdf.cell(col_width, 6, fit_text_in_cell(lead.get("ciudad", ""), col_width), 1)
        pdf.cell(col_width, 6, fit_text_in_cell(lead.get("correo", ""), col_width), 1)
        pdf.cell(col_width, 6, fit_text_in_cell(str(lead.get("fecha_lead", "")), col_width), 1)
        pdf.cell(col_width, 6, fit_text_in_cell(lead.get("origen_lead", ""), col_width), 1)
        pdf.cell(col_width, 6, fit_text_in_cell(lead.get("marca_interes", ""), col_width), 1)
        pdf.cell(col_width, 6, fit_text_in_cell(lead.get("modelo_interesado", ""), col_width), 1)
        pdf.cell(col_width, 6, fit_text_in_cell(lead.get("estatus", ""), col_width), 1)
        pdf.cell(col_width, 6, fit_text_in_cell(lead.get("test_drive", ""), col_width), 1)
        pdf.cell(col_width, 6, fit_text_in_cell(lead.get("seguimientos", ""), col_width), 1)
        pdf.ln()

    return pdf.output(dest="S").encode("latin1")

def create_pdf_gerente(leads, vendedor=None, filtro_estado=None, filtroTestDrive=None, 
                       vendedor_nombre_completo=None, filtro_marca=None, fechaDesde=None, fechaHasta=None):
    pdf = FPDF(orientation='L')  # 'L' establece la orientación horizontal
    pdf.add_page()
    
    # Reducir los márgenes para aprovechar mejor el espacio
    pdf.set_left_margin(5)
    pdf.set_right_margin(5)

    pdf.set_font("Arial", "B", 10)

    # Encabezado del reporte
    pdf.cell(0, 10, "Reporte de Leads", 0, 1, "C")
    pdf.set_font("Arial", size=9)

    # Incluir los filtros aplicados en el encabezado

    if vendedor_nombre_completo:
        pdf.cell(0, 8, f"Leads de Vendedor: {vendedor_nombre_completo}", 0, 1, "L")
    if filtro_estado:
        pdf.cell(0, 8, f"Filtro de Estado: {filtro_estado}", 0, 1, "L")
    if filtroTestDrive:
        pdf.cell(0, 8, f"Filtro de Test Drive: {filtroTestDrive}", 0, 1, "L")
    if filtro_marca:
        pdf.cell(0, 8, f"Marca de Interés: {filtro_marca}", 0, 1, "L")  # ✅ Nuevo filtro añadido
    if fechaDesde or fechaHasta:
        pdf.cell(0, 8, f"Rango de Fechas: {fechaDesde or 'Inicio'} - {fechaHasta or 'Fin'}", 0, 1, "L")    
    pdf.ln(5)  # Espacio entre encabezado y tabla

    # Cabeceras de la tabla
    column_headers = ["Vendedor", "Nombres", "Apellidos", "Identificación", "Teléfono", "Dirección", 
                      "Ciudad", "Correo", "Fecha Lead", "Origen Lead", "Marca de Interés", 
                      "Modelo Interesado", "Estatus", "Test Drive", "Seguimientos"]

    # Calcular ancho de cada columna para que encajen en la página (sin el "ID")
    page_width = pdf.w - 10  # Restar márgenes
    col_width = page_width / len(column_headers)  # Ancho calculado dinámicamente

    pdf.set_font("Arial", "B", 6)
    for header in column_headers:
        pdf.cell(col_width, 6, header, 1, 0, "C")
    pdf.ln()

    # Función para ajustar texto en cada celda
    def fit_text_in_cell(text, width):
        # Manejar valores None y convertirlos a cadenas vacías
        text = str(text) if text is not None else ""
        # Filtrar caracteres no compatibles con latin-1
        text = text.encode("latin-1", "replace").decode("latin-1")
        max_chars = int(width / 1.3)  # Ajuste según el ancho de la columna
        return text[:max_chars - 3] + "..." if len(text) > max_chars else text

    # Contenido de los leads (sin la columna "ID")
    pdf.set_font("Arial", size=7)  # Tamaño de fuente más pequeño para el contenido
    for lead in leads:
        pdf.cell(col_width, 6, fit_text_in_cell(lead.get("vendedor_nombre", ""), col_width), 1)
        pdf.cell(col_width, 6, fit_text_in_cell(lead.get("nombres", ""), col_width), 1)
        pdf.cell(col_width, 6, fit_text_in_cell(lead.get("apellidos", ""), col_width), 1)
        pdf.cell(col_width, 6, fit_text_in_cell(lead.get("identificacion", ""), col_width), 1)
        pdf.cell(col_width, 6, fit_text_in_cell(lead.get("telefono", ""), col_width), 1)
        pdf.cell(col_width, 6, fit_text_in_cell(lead.get("direccion", ""), col_width), 1)
        pdf.cell(col_width, 6, fit_text_in_cell(lead.get("ciudad", ""), col_width), 1)
        pdf.cell(col_width, 6, fit_text_in_cell(lead.get("correo", ""), col_width), 1)
        pdf.cell(col_width, 6, fit_text_in_cell(str(lead.get("fecha_lead", "")), col_width), 1)
        pdf.cell(col_width, 6, fit_text_in_cell(lead.get("origen_lead", ""), col_width), 1)
        pdf.cell(col_width, 6, fit_text_in_cell(lead.get("marca_interes", ""), col_width), 1)
        pdf.cell(col_width, 6, fit_text_in_cell(lead.get("modelo_interesado", ""), col_width), 1)
        pdf.cell(col_width, 6, fit_text_in_cell(lead.get("estatus", ""), col_width), 1)
        pdf.cell(col_width, 6, fit_text_in_cell(lead.get("test_drive", ""), col_width), 1)
        pdf.cell(col_width, 6, fit_text_in_cell(lead.get("seguimientos", ""), col_width), 1)
        pdf.ln()

    return pdf.output(dest="S").encode("latin1")

def obtener_credenciales():
    if os.getenv("GOOGLE_CREDENTIALS_JSON"):
        # Railway: cargar desde variable de entorno
        credentials_info = json.loads(os.getenv("GOOGLE_CREDENTIALS_JSON"))
        creds = service_account.Credentials.from_service_account_info(
            credentials_info,
            scopes=['https://www.googleapis.com/auth/gmail.send']
        )
    else:
        # Local: cargar desde archivo
        # Ruta absoluta a las credenciales
        CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), 'credentials', 'notificacionleads-service-account.json')
        creds = service_account.Credentials.from_service_account_file(
            CREDENTIALS_FILE,
            scopes=['https://www.googleapis.com/auth/gmail.send']
        )
    return creds

# Función para enviar notificación de correo desde sendgrid
def enviar_correo(destinatario, asunto, mensaje):
    """Función para enviar correo usando SendGrid."""
    remitente = os.getenv('SENDGRID_FROM_EMAIL', 'default_email@example.com')  # Email por defecto si no se encuentra la variable
    
    # Procesar destinatario: si es cadena, convertirla en lista; si ya es lista, usarla como está
    if isinstance(destinatario, str):
        # Reemplazar punto y coma por coma y dividir en lista, eliminando espacios
        destinatarios_lista = [email.strip() for email in destinatario.replace(';', ',').split(',') if email.strip()]
    elif isinstance(destinatario, list):
        destinatarios_lista = destinatario
    else:
        raise ValueError("El parámetro 'destinatario' debe ser una cadena o una lista")

    # Verificar que haya al menos un destinatario válido
    if not destinatarios_lista:
        raise ValueError("No se proporcionaron destinatarios válidos")

    # Crear el mensaje con múltiples destinatarios
    message = Mail(
        from_email=remitente,
        subject=asunto,
        html_content=mensaje
    )
    # Agregar todos los destinatarios como una lista de objetos To
    message.to = [To(email) for email in destinatarios_lista]

    try:
        sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(f"Correo enviado exitosamente a {destinatarios_lista}. Código de respuesta: {response.status_code}")
        return response.status_code  # Opcional: devolver el código para mayor control
    except Exception as e:
        print(f"Error al enviar el correo: {str(e)}")
        raise  # Relanzar la excepción para que el endpoint lo maneje


# Función para enviar notificación de WhatsApp
def enviar_notificacion_whatsapp(vendedor_telefono):
    client = Client(ACCOUNT_SID, AUTH_TOKEN)

    # Enviar mensaje usando el Content SID de una plantilla de Twilio
    message = client.messages.create(
        from_=TWILIO_WHATSAPP_NUMBER,
        to=f'whatsapp:{vendedor_telefono}',
        content_sid=CONTENT_SID,
        content_variables=json.dumps({"1": "12/1", "2": "3pm"})  # Se ajusta según la plantilla
    )

    print(f"Mensaje de WhatsApp enviado: SID {message.sid}")
    return message.sid


# Función para enviar webhook
# Esto es necesario ponberlo afuera de la funcion

# Definir múltiples webhooks como variables de entorno
def obtener_configuracion_webhooks():
    """Obtiene la configuración de los webhooks desde la base de datos."""
    try:
        cursor.execute("""
            SELECT webhook_interno, webhook_make, webhook_zapier, habilitar_webhook
            FROM configuracion_general 
            LIMIT 1
        """)
        configuracion = cursor.fetchone()

        if configuracion:
            return {
                "interno": configuracion[0] or "",
                "make": configuracion[1] or "",
                "zapier": configuracion[2] or "",
                "habilitar_webhook": configuracion[3]
            }
        else:
            return {"interno": "", "make": "", "zapier": "", "habilitar_webhook": False}

    except Exception as e:
        print(f"❌ Error al obtener la configuración de los webhooks desde la BD: {e}")
        return {"interno": "", "make": "", "zapier": "", "habilitar_webhook": False}

def clean_data(lead_data):
    """
    Convierte todos los valores en strings para evitar problemas con Make y Zapier.
    """
    cleaned_data = {}
    for key, value in lead_data.items():
        if value is None:
            cleaned_data[key] = ""  # Convertir None en string vacío
        elif isinstance(value, (int, float, bool)):
            cleaned_data[key] = str(value)  # Convertir números y booleanos a string
        elif isinstance(value, datetime):
            cleaned_data[key] = value.isoformat()  # Convertir objetos datetime a string en formato ISO
        elif isinstance(value, (list, dict)):
            cleaned_data[key] = json.dumps(value)  # Convertir listas y diccionarios a JSON string
        else:
            cleaned_data[key] = value  # Mantener string tal cual

    return cleaned_data


def request_webhook(url, method="POST", data=None):
    """Envía datos a un webhook usando GET o POST y maneja errores con logs detallados."""
    try:
        headers = {"Content-Type": "application/json"}

        if method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=15)
        else:
            response = requests.get(url, timeout=15)

        print(f"🔗 Webhook ejecutado: {url}")
        print(f"📡 Respuesta del servidor: {response.status_code}, {response.text}")

        return response.status_code, response.text

    except requests.exceptions.RequestException as e:
        print(f"❌ Error al ejecutar el webhook {url}: {e}")
        return None, str(e)

def enviar_webhook(lead_data):
    """Envía los datos del nuevo lead directamente a los webhooks configurados en la base de datos."""
    try:
        configuracion = obtener_configuracion_webhooks()

        # Si los webhooks están deshabilitados, no enviar nada.
        if not configuracion["habilitar_webhook"]:
            print("🚫 Envío de webhooks deshabilitado. No se enviarán datos.")
            return

        print(f"📡 Enviando datos a los webhooks...")

        # Verificar que tenemos datos válidos
        if not lead_data:
            print("⚠️ No hay datos para enviar al webhook.")
            return

        # **Limpieza de datos antes de enviarlos**
        clean_lead_data = clean_data(lead_data)

        print(f"📡 Datos exactos enviados a Make/Zapier:\n{json.dumps(clean_lead_data, indent=2)}")

        # Enviar al webhook interno (GET)
        if configuracion["interno"]:
            thread_interno = threading.Thread(target=request_webhook, args=(configuracion["interno"], "GET"))
            thread_interno.start()

        # Enviar al webhook de Make (POST con JSON limpio)
        if configuracion["make"]:
            status_make, response_make = request_webhook(configuracion["make"], "POST", clean_lead_data)
            if status_make in [200, 201]:
                print("✅ Datos enviados correctamente a Make.")
            else:
                print(f"⚠️ Error al enviar datos a Make. Status: {status_make}, Respuesta: {response_make}")

        # Enviar al webhook de Zapier (POST con objeto JSON plano)
        if configuracion["zapier"]:
            status_zapier, response_zapier = request_webhook(configuracion["zapier"], "POST", clean_lead_data)
            if status_zapier in [200, 201]:
                print("✅ Datos enviados correctamente a Zapier.")
            else:
                print(f"⚠️ Error al enviar datos a Zapier. Status: {status_zapier}, Respuesta: {response_zapier}")

    except Exception as e:
        print(f"❌ Error crítico al enviar datos al webhook: {e}")





# ENDPOINTS DE ARRANQUE
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, "index.html")

@app.route('/get-current-time', methods=['GET'])
def get_current_time():
    """Devuelve la hora actual en la zona horaria de Colombia."""
    current_time = get_current_time_colombia()
    return jsonify({
        "date": current_time.strftime("%Y-%m-%d"),  # Devuelve solo la fecha
        "datetime": current_time.strftime("%Y-%m-%d %H:%M:%S")  # También puedes incluir la hora completa si es necesario
    })

@app.route("/debug-db")
def debug_db():
    cursor.execute("SELECT current_database(), current_user, inet_server_addr(), inet_server_port();")
    info = cursor.fetchone()
    return jsonify({
        "database": info[0],  # Nombre de la base de datos
        "user": info[1],      # Usuario conectado
        "host": info[2],      # Dirección IP del servidor
        "port": info[3],      # Puerto de conexión
    })


# Ruta para login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    usuario = data['usuario']
    password = data['password']

    user = obtener_usuario(usuario, password)

    if user:
        # Actualiza la fecha de última conexión
        cursor.execute("UPDATE usuarios SET ultima_conexion = %s WHERE id = %s", (get_current_time_colombia(), user['id']))
        conn.commit()

        # Responde según el tipo de usuario
        if user['tipo_usuario'] == 'vendedor':
            return jsonify({
                'message': 'Login exitoso',
                'tipo_usuario': user['tipo_usuario'],
                'vendedor_id': user['id'],  # Asegúrate de que el vendedor_id se envía aquí
                'id': user['id']
            }), 200
        elif user['tipo_usuario'] == 'supervisor':
            return jsonify({
                'message': 'Login exitoso',
                'tipo_usuario': user['tipo_usuario'],
                'id': user['id']
            }), 200
        elif user['tipo_usuario'] == 'administrador':
            return jsonify({
                'message': 'Login exitoso',
                'tipo_usuario': 'administrador',
                'id': user['id']
            }), 200
        elif user['tipo_usuario'] == 'expert':  # Agregar lógica para expert
            return jsonify({
                'message': 'Login exitoso',
                'tipo_usuario': 'expert',
                'id': user['id']
            }), 200
        elif user['tipo_usuario'] == 'gerente':  # Lógica específica para gerente
            return jsonify({
                'message': 'Login exitoso',
                'tipo_usuario': 'gerente',
                'id': user['id']
            }), 200
        else:
            return jsonify({'message': 'Tipo de usuario no reconocido'}), 400
    else:
        return jsonify({'message': 'Credenciales incorrectas'}), 401

@app.route('/get-configuracion-general', methods=['GET'])
def get_configuracion_general():
    """Obtiene la configuración general incluyendo los webhooks."""
    try:
        cursor.execute("""
            SELECT enviar_correo, destinatarios, webhook_interno, webhook_make, webhook_zapier, habilitar_webhook
            FROM configuracion_general 
            LIMIT 1
        """)
        configuracion = cursor.fetchone()

        if configuracion:
            return jsonify({
                "enviar_correo": configuracion[0],
                "destinatarios": configuracion[1],
                "webhook_interno": configuracion[2] or "",  # Si es NULL, se devuelve vacío
                "webhook_make": configuracion[3] or "",
                "webhook_zapier": configuracion[4] or "",
                "habilitar_webhook": configuracion[5]
            }), 200
        else:
            return jsonify({
                "enviar_correo": False,
                "destinatarios": "",
                "webhook_interno": "",
                "webhook_make": "",
                "webhook_zapier": "",
                "habilitar_webhook": False
            }), 200

    except Exception as e:
        print(f"Error al obtener la configuración general: {e}")
        return jsonify({"error": "Error al obtener la configuración general."}), 500



@app.route('/update-configuracion-general', methods=['POST'])
def update_configuracion_general():
    """Actualiza la configuración general, incluyendo los webhooks."""
    data = request.json
    try:
        # Verificar si ya existe una configuración
        cursor.execute("SELECT COUNT(*) FROM configuracion_general")
        existe = cursor.fetchone()[0] > 0

        if existe:
            cursor.execute("""
                UPDATE configuracion_general
                SET enviar_correo = %s, destinatarios = %s, 
                    webhook_interno = %s, webhook_make = %s, webhook_zapier = %s, habilitar_webhook = %s
                WHERE id = 1
            """, (
                data['enviar_correo'], data['destinatarios'],
                data['webhook_interno'], data['webhook_make'], data['webhook_zapier'], data['habilitar_webhook']
            ))
        else:
            cursor.execute("""
                INSERT INTO configuracion_general (enviar_correo, destinatarios, webhook_interno, webhook_make, webhook_zapier, habilitar_webhook)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                data['enviar_correo'], data['destinatarios'],
                data['webhook_interno'], data['webhook_make'], data['webhook_zapier'], data['habilitar_webhook']
            ))

        conn.commit()
        return jsonify({"message": "Configuración actualizada correctamente."}), 200

    except Exception as e:
        conn.rollback()
        print(f"Error al actualizar la configuración general: {e}")
        return jsonify({"error": "Error al actualizar la configuración general."}), 500



# Ruta para agregar un lead dejando registro de auditoria
@app.route('/add-lead', methods=['POST'])
def add_lead():
    data = request.json

    # Validación de datos obligatorios
    if data['habeas_data'] != 'Si' or data['aceptacion_tratamiento_datos'] != 'Si':
        return jsonify({"error": "Debe aceptar Habeas Data y Tratamiento de Datos"}), 400
    if not data.get('concesionario_id'):
        return jsonify({"error": "Debe seleccionar un concesionario"}), 400

    try:
        #fecha_aceptacion = datetime.utcnow()
        fecha_aceptacion = get_current_time_colombia()

        lead_values = (
            data['nombres'],
            data['apellidos'],
            data.get('identificacion'),
            data['telefono'],
            data['direccion'],
            data['ciudad'],
            data['correo'],
            get_current_time_colombia().date(),
            data['origen_lead'],
            data['marca_interes'],
            data['modelo_interesado'],
            data.get('estatus', 'nuevo'),
            data.get('asignado', False),
            data.get('test_drive', 'No'),
            data.get('precio_venta'),
            data['capturado_por'],
            data['habeas_data'],
            data['aceptacion_tratamiento_datos'],
            data['firma_digital'],
            data['concesionario_id'],
            fecha_aceptacion
        )

        # Inserción del lead con retorno del ID
        lead_query = """
            INSERT INTO leads (nombres, apellidos, identificacion, telefono, direccion, ciudad, correo, fecha_lead, 
                               origen_lead, marca_interes, modelo_interesado, estatus, asignado, test_drive, precio_venta, 
                               capturado_por, habeas_data, aceptacion_tratamiento_datos, firma_digital, concesionario_id, fecha_aceptacion)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """

        cursor.execute(lead_query, lead_values)
        lead_id = cursor.fetchone()[0]
        

        # Obtener el nombre del concesionario
        cursor.execute("SELECT nombre_concesionario FROM concesionarios WHERE id = %s", (data['concesionario_id'],))
        concesionario_nombre = cursor.fetchone()
        concesionario_nombre = concesionario_nombre[0] if concesionario_nombre else "Concesionario desconocido"

        # Registro detallado en la auditoría
        comentarios_auditoria = (
            f"Lead creado: nombres={data['nombres']}, apellidos={data['apellidos']}, "
            f"correo={data['correo']}, origen_lead={data['origen_lead']}, "
            f"marca_interes={data['marca_interes']}, modelo_interesado={data['modelo_interesado']}, "
            f"estatus={data.get('estatus', 'nuevo')}."
        )
        auditoria_query = """
            INSERT INTO auditoria (usuario_id, accion, tabla_afectada, registro_id, comentarios)
            VALUES (%s, %s, %s, %s, %s)
        """
        auditoria_values = (
            data['capturado_por'], 'Creación', 'leads', lead_id, comentarios_auditoria
        )
        cursor.execute(auditoria_query, auditoria_values)

        # Verificar configuración para envío de correo
        cursor.execute("SELECT enviar_correo, destinatarios FROM configuracion_general")
        configuracion = cursor.fetchone()
        enviar_correo_flag, destinatarios = configuracion if configuracion else (False, None)

        if enviar_correo_flag and destinatarios:
            try:
                # Enviar correo
                asunto = "Nuevo Lead Capturado"
                mensaje = f"""
                Cordial saludo equipo CDN,<br><br>
                Desde el sistema LeadsMass se ha capturado un nuevo lead. Este es el contenido del Lead para ser registrado en el sistema CRM Salesforce:<br>
                <ul>
                    <li><b>Nombres:</b> {data['nombres']}</li>
                    <li><b>Apellidos:</b> {data['apellidos']}</li>
                    <li><b>Identificación:</b> {data.get('identificacion')}</li>
                    <li><b>Celular:</b> {data['telefono']}</li>
                    <li><b>Dirección:</b> {data['direccion']}</li>
                    <li><b>Ciudad:</b> {data['ciudad']}</li>
                    <li><b>Correo:</b> {data['correo']}</li>
                    <li><b>Fecha del Lead:</b> {get_current_time_colombia().date()}</li>
                    <li><b>Origen del Lead:</b> {data['origen_lead']}</li>
                    <li><b>Marca:</b> {data['marca_interes']}</li>
                    <li><b>Modelo Interesado:</b> {data['modelo_interesado']}</li>
                    <li><b>Concesionario Asignado:</b> {concesionario_nombre}</li>
                </ul>
                El Lead acepta la política de Habeas data y tratamiento de datos del Grupo Inchcape y deja su firma digital en nuestra sistema LeadsMass.<br><br>
                Cordialmente,<br>Sistema LeadsMass
                """
                enviar_correo(destinatario=destinatarios, asunto=asunto, mensaje=mensaje)

                # Registro en la auditoría del correo enviado
                auditoria_query = """
                    INSERT INTO auditoria (usuario_id, accion, tabla_afectada, registro_id, comentarios)
                    VALUES (%s, %s, %s, %s, %s)
                """
                auditoria_values = (
                    data['capturado_por'], 'Correo Captura Lead Expert', 'leads', lead_id, "Correo enviado correctamente"
                )
                cursor.execute(auditoria_query, auditoria_values)
            except Exception as e:
                print(f"Error al enviar el correo: {e}")

        # Confirmar todas las transacciones
        conn.commit()
        print("✅ Lead insertado con ID:", lead_id)

        # 🔥 Llamar al webhook después de confirmar la inserción
        enviar_webhook(data)

        return jsonify({"message": "Lead agregado exitosamente"}), 200

    except Exception as e:
        # Rollback en caso de cualquier error
        conn.rollback()
        return jsonify({"error": "Error al guardar el lead", "details": str(e)}), 500



# Ruta para obtener los leads
@app.route('/get-leads', methods=['GET'])
def get_leads():
    #cursor.execute("SELECT * FROM leads;")
    # Incluir el nuevo campo precio_venta al seleccionar leads
    cursor.execute("SELECT id, nombres, apellidos, identificacion, telefono, direccion, ciudad, correo, fecha_lead, origen_lead, marca_interes, modelo_interesado, estatus, asignado, seguimientos, test_drive, capturado_por, habeas_data, aceptacion_tratamiento_datos, precio_venta FROM leads;")
    leads = cursor.fetchall()
    result = []
    for lead in leads:
        result.append({
            "id": lead[0],
            "nombres": lead[1],
            "apellidos": lead[2],
            "identificacion": lead[3],
            "telefono": lead[4],
            "direccion": lead[5],
            "ciudad": lead[6],
            "correo": lead[7],
            "fecha_lead": str(lead[8]),
            "origen_lead": lead[9],
            "marca_interes": lead[10],
            "modelo_interesado": lead[11],
            "estatus": lead[12],
            "asignado": lead[13],
            "seguimientos": lead[14],  # Nuevo campo de seguimientos
            "test_drive": lead[15],
            "capturado_por": lead[16],
            "habeas_data": lead[17],
            "aceptacion_tratamiento_datos": lead[18],
            # Nuevo campo de precio de venta (puede ser None)
            "precio_venta": lead[19] if len(lead) > 19 else None
        })
    return jsonify(result), 200


@app.route('/get-all-leads', methods=['GET'])
def get_all_leads():
    vendedor_id = request.args.get('vendedor_id')

    if vendedor_id:
        query = """
            SELECT id, nombres, apellidos, identificacion, telefono, direccion, ciudad, correo, fecha_lead,
                   origen_lead, marca_interes, modelo_interesado, estatus, asignado, asignado_a,
                   fecha_asignacion, seguimientos, test_drive, precio_venta
            FROM leads
            WHERE asignado_a = %s
        """
        cursor.execute(query, (vendedor_id,))
    else:
        query = """
            SELECT id, nombres, apellidos, identificacion, telefono, direccion, ciudad, correo, fecha_lead,
                   origen_lead, marca_interes, modelo_interesado, estatus, asignado, asignado_a,
                   fecha_asignacion, seguimientos, test_drive, precio_venta
            FROM leads
        """
        cursor.execute(query)

    leads = cursor.fetchall()

    result = []
    for lead in leads:
        # Chequear la longitud del lead y continuar solo si todos los elementos están presentes
        if len(lead) >= 18:
            result.append({
                "id": lead[0],
                "nombres": lead[1],
                "apellidos": lead[2],
                "identificacion": lead[3],
                "telefono": lead[4],
                "direccion": lead[5],
                "ciudad": lead[6],
                "correo": lead[7],
                "fecha_lead": str(lead[8]) if lead[8] else "",
                "origen_lead": lead[9],
                "marca_interes": lead[10],
                "modelo_interesado": lead[11],
                "estatus": lead[12],
                "asignado": lead[13],
                "asignado_a": lead[14],
                "fecha_asignacion": str(lead[15]) if lead[15] else None,
                "seguimientos": lead[16] if lead[16] else "",
                "test_drive": lead[17],
                # Precio de venta (puede ser None)
                "precio_venta": lead[18],
            })
        else:
            # Log para depuración si hay leads incompletos
            print(f"Lead incompleto encontrado: {lead}")

    return jsonify(result), 200

@app.route('/get-all-leads-supervisor', methods=['GET'])
def get_all_leads_supervisor():
    # Obtener el usuario autenticado (simulado aquí con un parámetro para pruebas)
    usuario_id = request.args.get('usuario_id')  # Debería ser el ID del usuario autenticado

    if not usuario_id:
        return jsonify({"error": "ID de usuario no proporcionado"}), 400
    
    # Verificar el concesionario asociado al usuario
    query_concesionario = """
        SELECT concesionario 
        FROM usuarios 
        WHERE id = %s AND tipo_usuario = 'supervisor'
    """
    cursor.execute(query_concesionario, (usuario_id,))
    concesionario = cursor.fetchone()
    print("Concesionario asociado al supervisor:", concesionario)  # Log para verificar
    
    if not concesionario or not concesionario[0]:
        return jsonify({"error": "El usuario no tiene un concesionario asignado o no es supervisor"}), 403

    concesionario_nombre = concesionario[0]

    # Obtener leads del concesionario asignado
    query_leads = """
        SELECT id, nombres, apellidos, identificacion, telefono, direccion, ciudad, correo, fecha_lead,
               origen_lead, marca_interes, modelo_interesado, estatus, asignado, asignado_a,
               fecha_asignacion, seguimientos, test_drive, precio_venta
        FROM leads
        WHERE concesionario_id = (
            SELECT id
            FROM concesionarios
            WHERE nombre_concesionario = %s
        )
    """
    cursor.execute(query_leads, (concesionario_nombre,))
    leads = cursor.fetchall()

    # Formatear los leads en un objeto JSON
    result = []
    for lead in leads:
        if len(lead) >= 18:
            result.append({
                "id": lead[0],
                "nombres": lead[1],
                "apellidos": lead[2],
                "identificacion": lead[3],
                "telefono": lead[4],
                "direccion": lead[5],
                "ciudad": lead[6],
                "correo": lead[7],
                "fecha_lead": str(lead[8]) if lead[8] else "",
                "origen_lead": lead[9],
                "marca_interes": lead[10],
                "modelo_interesado": lead[11],
                "estatus": lead[12],
                "asignado": lead[13],
                "asignado_a": lead[14],
                "fecha_asignacion": str(lead[15]) if lead[15] else None,
                "seguimientos": lead[16] if lead[16] else "",
                "test_drive": lead[17],
                "precio_venta": lead[18],
            })

    return jsonify(result), 200

# Ruta para obtener los leads asignados al vendedor
@app.route('/get-leads-vendedor', methods=['GET'])
def get_leads_vendedor():
    vendedor_id = request.args.get('vendedor')
    
    if not vendedor_id:
        return jsonify({"message": "No se proporcionó un ID de vendedor"}), 400

    try:
        cursor.execute("""
            SELECT id, nombres, apellidos, identificacion, telefono, direccion, ciudad, correo,
                   fecha_lead, origen_lead, marca_interes, modelo_interesado, estatus, asignado,
                   asignado_a, fecha_asignacion, seguimientos, test_drive, precio_venta
            FROM leads
            WHERE asignado_a = %s
        """, (int(vendedor_id),))
        leads = cursor.fetchall()

        leads_list = []
        for lead in leads:
            leads_list.append({
                "id": lead[0],
                "nombres": lead[1],
                "apellidos": lead[2],
                "identificacion": lead[3],
                "telefono": lead[4],
                "direccion": lead[5],
                "ciudad": lead[6],
                "correo": lead[7],
                "fecha_lead": str(lead[8]),
                "origen_lead": lead[9],
                "marca_interes": lead[10],
                "modelo_interesado": lead[11],
                "estatus": lead[12],
                "asignado": lead[13],
                "asignado_a": lead[14],
                "fecha_asignacion": str(lead[15]) if lead[15] else None,
                "seguimientos": lead[16],
                "test_drive": lead[17],
                # Precio de venta puede ser None
                "precio_venta": lead[18]
            })
        return jsonify(leads_list), 200

    except Exception as e:
        print(f"Error al obtener leads para el vendedor {vendedor_id}: {e}")
        return jsonify({"error": str(e)}), 500


# Ruta para cargar leads desde un archivo CSV
@app.route('/upload-leads', methods=['POST'])
def upload_leads():
    try:
        file = request.files['file']
        usuario_id = request.form.get('usuario_id')  # Obtener el usuario que realiza la acción

        if not file:
            return jsonify({"error": "No se cargó ningún archivo"}), 400
        if not usuario_id:
            return jsonify({"error": "Usuario no identificado"}), 400

        try:
            # Leer el archivo CSV usando punto y coma como delimitador
            df = pd.read_csv(file, delimiter=';')
            # Normalizar encabezados para manejar mayúsculas/minúsculas y espacios
            df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
        except Exception as e:
            print(f"Error leyendo el archivo CSV: {e}")
            return jsonify({"error": "El archivo no pudo ser leído. Asegúrese de que sea un CSV válido."}), 400

        # Variables para contadores
        leads_cargados = 0
        leads_rechazados = 0
        motivos_rechazo = {
            "habeas_data": 0,
            "tratamiento_datos": 0
        }

        # Obtener la fecha actual
        fecha_actual = get_current_time_colombia().date()

        # Iterar por las filas del archivo
        for index, row in df.iterrows():
            try:
                # Manejar el campo 'Habeas Data'
                habeas_data_value = str(row.get('habeas_data', 'No')).strip().capitalize()
                if habeas_data_value != 'Si':
                    motivos_rechazo["habeas_data"] += 1
                    leads_rechazados += 1
                    continue

                # Manejar el campo 'Tratamiento Datos'
                tratamiento_datos_value = str(row.get('aceptacion_tratamiento_datos', 'No')).strip().capitalize()
                if tratamiento_datos_value != 'Si':
                    motivos_rechazo["tratamiento_datos"] += 1
                    leads_rechazados += 1
                    continue

                # Convertir 'Asignado' a booleano manejando valores NaN
                asignado_value = str(row.get('asignado', 'No')).strip().lower() == 'sí' if pd.notnull(row.get('asignado')) else False

                # Manejar el campo 'Test Drive'
                test_drive_value = str(row.get('test_drive', 'No')).strip().capitalize()

                # Convertir 'Fecha Lead' a tipo de fecha o asignar fecha actual si no es válida
                fecha_lead = row.get('fecha_lead', '').strip()
                if fecha_lead:
                    try:
                        fecha_lead = datetime.strptime(fecha_lead, "%Y-%m-%d").date()  # Formato AAAA-MM-DD
                    except ValueError:
                        return jsonify({"error": f"Error en la fila {index + 1}: La fecha '{fecha_lead}' no es válida. Use el formato AAAA-MM-DD."}), 400
                else:
                    fecha_lead = fecha_actual

                # Preparar el valor del precio de venta, si está presente en el archivo. Si no, dejarlo en None.
                try:
                    precio_venta_value = float(row.get('precio_venta')) if pd.notnull(row.get('precio_venta')) and str(row.get('precio_venta')).strip() != '' else None
                except Exception:
                    precio_venta_value = None

                # Insertar el lead en la base de datos. Incluye el nuevo campo `precio_venta`.
                query = """
                    INSERT INTO leads (nombres, apellidos, identificacion, telefono, direccion, ciudad, correo, fecha_lead,
                        origen_lead, marca_interes, modelo_interesado, estatus, asignado, test_drive, precio_venta, habeas_data, aceptacion_tratamiento_datos)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id;
                """
                cursor.execute(query, (
                    str(row.get('nombres', '')).strip(),
                    str(row.get('apellidos', '')).strip(),
                    str(row.get('identificacion', '')).strip(),
                    str(row.get('telefono', '')).strip(),
                    str(row.get('direccion', '')).strip(),
                    str(row.get('ciudad', '')).strip(),
                    str(row.get('correo', '')).strip(),
                    fecha_lead,
                    str(row.get('origen_lead', '')).strip(),
                    str(row.get('marca_interes', '')).strip(),
                    str(row.get('modelo_interesado', '')).strip(),
                    str(row.get('estatus', 'nuevo')).strip(),
                    asignado_value,
                    test_drive_value,
                    precio_venta_value,
                    habeas_data_value,
                    tratamiento_datos_value
                ))
                lead_id = cursor.fetchone()[0]
                conn.commit()
                leads_cargados += 1

                # Registrar en la auditoría con detalles del lead
                detalles_creacion = f"Lead creado con nombres: {row.get('nombres', '').strip()}, " \
                                    f"apellidos: {row.get('apellidos', '').strip()}, " \
                                    f"correo: {row.get('correo', '').strip()}."
                auditoria_query = """
                    INSERT INTO auditoria (usuario_id, accion, tabla_afectada, registro_id, comentarios)
                    VALUES (%s, %s, %s, %s, %s)
                """
                auditoria_values = (
                    usuario_id, 'Creación', 'leads', lead_id, detalles_creacion
                )
                cursor.execute(auditoria_query, auditoria_values)
                conn.commit()

            except Exception as e:
                print(f"Error al procesar la fila {index + 1}: {e}")
                leads_rechazados += 1

        # Registrar rechazos en la auditoría
        for razon, cantidad in motivos_rechazo.items():
            if cantidad > 0:
                auditoria_query = """
                    INSERT INTO auditoria (usuario_id, accion, tabla_afectada, comentarios)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(auditoria_query, (
                    usuario_id, 'Rechazo', 'leads',
                    f"{cantidad} leads rechazados por {razon}"
                ))
                conn.commit()

        # Resumen de resultados
        return jsonify({
            "message": f"Carga completada. Leads cargados: {leads_cargados}, Leads rechazados: {leads_rechazados}",
            "rechazos": motivos_rechazo
        }), 200

    except Exception as e:
        conn.rollback()
        print(f"Error procesando el archivo de leads: {e}")
        return jsonify({"error": "Ocurrió un error al procesar el archivo de leads.", "details": str(e)}), 500


# Ruta para actualizar un lead
# Ruta para actualizar un lead
@app.route('/update-lead', methods=['POST'])
def update_lead():
    data = request.json
    print(f"📥 Datos recibidos en el backend: {data}")  # 🚀 Agrega este print

    # Validar que el ID del lead y el usuario_id estén presentes en la solicitud
    if not data.get('id'):
        print("❌ Error: Falta el ID del lead")
        return jsonify({"error": "El campo 'id' del lead es obligatorio"}), 400
    if not data.get('usuario_id'):
        print("❌ Error: Falta el usuario_id")
        return jsonify({"error": "El campo 'usuario_id' es obligatorio"}), 400

    try:
        # Consultar los valores actuales del lead antes de actualizar
        cursor.execute("SELECT * FROM leads WHERE id = %s", (data['id'],))
        lead_actual = cursor.fetchone()

        if not lead_actual:
            return jsonify({"error": "Lead no encontrado"}), 404

        # Obtener el orden de las columnas en la tabla "leads"
        columnas = [desc[0] for desc in cursor.description]

        # Mantener los valores originales de `habeas_data` y `aceptacion_tratamiento_datos`
        if 'habeas_data' not in data:
            data['habeas_data'] = lead_actual[columnas.index('habeas_data')]
        if 'aceptacion_tratamiento_datos' not in data:
            data['aceptacion_tratamiento_datos'] = lead_actual[columnas.index('aceptacion_tratamiento_datos')]

        # ✅ **Validar fecha_lead**: Si viene `undefined`, `None` o vacía, no actualizarla
        fecha_lead = data.get('fecha_lead')

        if not fecha_lead or 'undefined' in fecha_lead:
            print(f"⚠️ Ignorando actualización de fecha_lead inválida: {fecha_lead}")
            fecha_lead = None
        else:
            try:
                fecha_lead = datetime.strptime(fecha_lead, "%Y-%m-%d").date()
            except ValueError:
                print(f"❌ Error: Formato de fecha_lead inválido: {fecha_lead}")
                fecha_lead = None

        # 🔹 Registrar cambios para auditoría
        campos_modificados = []
        for campo, valor_nuevo in data.items():
            if campo in ['id', 'usuario_id']:
                continue  # Ignorar campos que no son datos modificables
            if campo in columnas:
                indice = columnas.index(campo)
                valor_anterior = lead_actual[indice]
                if str(valor_anterior) != str(valor_nuevo):  # Comparar como cadenas
                    campos_modificados.append({
                        "campo": campo,
                        "valor_anterior": valor_anterior,
                        "valor_nuevo": valor_nuevo
                    })

        # ✅ **Construir consulta dinámica para excluir campos nulos**
        # Incluimos el nuevo campo `precio_venta` en la actualización
        query = """
            UPDATE leads
            SET nombres = %s, apellidos = %s, identificacion = %s, telefono = %s, direccion = %s, ciudad = %s, correo = %s,
                origen_lead = %s, marca_interes = %s, modelo_interesado = %s, estatus = %s, asignado = %s,
                seguimientos = %s, test_drive = %s, habeas_data = %s, aceptacion_tratamiento_datos = %s, precio_venta = %s
        """

        # Ordenar los parámetros en el mismo orden que las columnas en el query
        params = [
            data['nombres'], data['apellidos'], data['identificacion'], data['telefono'],
            data['direccion'], data['ciudad'], data['correo'], data['origen_lead'],
            data['marca_interes'], data['modelo_interesado'], data['estatus'], data['asignado'],
            data.get('seguimientos', ''), data.get('test_drive', 'No'),
            data['habeas_data'], data['aceptacion_tratamiento_datos'],
            data.get('precio_venta')
        ]

        # Si el frontend envía una fecha válida, la incluimos en la actualización
        if fecha_lead is not None:
            query += ", fecha_lead = %s"
            params.append(fecha_lead)

        # Finalmente, se incluye el ID del lead para la cláusula WHERE
        query += " WHERE id = %s"
        params.append(data['id'])

        # ✅ **Ejecutar la consulta**
        cursor.execute(query, params)
        conn.commit()
        print(f"✅ Lead {data['id']} actualizado correctamente.")  # Log de éxito

        # ✅ **Insertar auditoría**
        for cambio in campos_modificados:
            auditoria_query = """
                INSERT INTO auditoria (usuario_id, accion, tabla_afectada, registro_id, campo_modificado, valor_anterior, valor_nuevo, comentarios)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            auditoria_values = (
                data['usuario_id'], 'Actualización', 'leads', data['id'], cambio['campo'],
                str(cambio['valor_anterior']), str(cambio['valor_nuevo']), f"Actualización de campo {cambio['campo']}"
            )
            cursor.execute(auditoria_query, auditoria_values)
        conn.commit()

        # 🚀 **Verificar si el vendedor aún tiene leads "asignado"**
        cursor.execute("""
            SELECT id FROM leads WHERE asignado_a = %s AND estatus = 'asignado'
        """, (data['usuario_id'],))
        lead_asignado = cursor.fetchone()

        if not lead_asignado:
            print(f"✅ Vendedor {data['usuario_id']} ya no tiene leads asignados. Intentando asignar nuevo lead...")
            asignar_nuevo_lead_automatico(data['usuario_id'])  # Llamar función para asignación automática

        return jsonify({"message": "Lead actualizado exitosamente"}), 200

    except Exception as e:
        conn.rollback()
        print(f"❌ Error al actualizar lead: {e}")  # Log de error
        return jsonify({"error": "Error al actualizar el lead", "details": str(e)}), 500


@app.route('/update-lead-gerente', methods=['POST'])
def update_lead_gerente():
    data = request.json
    print(f"📥 (Gerente) Datos recibidos: {data}")

    # 🔹 Validar si se recibe el id del lead y el usuario_id del gerente
    if not data.get('id'):
        print("❌ Error: Falta el ID del lead")
        return jsonify({"error": "El campo 'id' del lead es obligatorio"}), 400
    if not data.get('usuario_id'):
        print("❌ Error: Falta el usuario_id del gerente")
        return jsonify({"error": "El campo 'usuario_id' es obligatorio"}), 400

    try:
        # Consultar valores actuales antes de actualizar
        cursor.execute("SELECT * FROM leads WHERE id = %s", (data['id'],))
        lead_actual = cursor.fetchone()

        if not lead_actual:
            return jsonify({"error": "Lead no encontrado"}), 404

        columnas = [desc[0] for desc in cursor.description]

        # 🔹 Excluir actualización de habeas_data y aceptacion_tratamiento_datos
        if 'habeas_data' not in data:
            data['habeas_data'] = lead_actual[columnas.index('habeas_data')]
        if 'aceptacion_tratamiento_datos' not in data:
            data['aceptacion_tratamiento_datos'] = lead_actual[columnas.index('aceptacion_tratamiento_datos')]

        # 🔹 Lógica para asignación manual de vendedor
        if data['estatus'] != "nuevo" and 'vendedor_id' in data:
            data['asignado_a'] = data['vendedor_id']  # Guardar el vendedor en asignado_a
            data['asignado'] = True  # Marcar como asignado
        else:
            data['asignado_a'] = None  # Si no tiene vendedor, dejar vacío
            data['asignado'] = False  # Marcar como no asignado

        # 🔹 Registrar cambios para auditoría
        cambios_realizados = []
        for campo, nuevo_valor in data.items():
            if campo in ['id', 'usuario_id']:
                continue  
            if campo in columnas:
                indice = columnas.index(campo)
                valor_anterior = lead_actual[indice]
                if str(valor_anterior) != str(nuevo_valor):  
                    cambios_realizados.append({
                        "campo": campo,
                        "valor_anterior": valor_anterior,
                        "valor_nuevo": nuevo_valor
                    })

        # 🔹 Construir la consulta de actualización dinámica
        # Se añade `precio_venta` como un campo actualizable por el gerente
        query = """
            UPDATE leads
            SET nombres = %s, apellidos = %s, identificacion = %s, telefono = %s, direccion = %s, ciudad = %s, correo = %s, 
                origen_lead = %s, marca_interes = %s, modelo_interesado = %s, estatus = %s, asignado = %s, asignado_a = %s, 
                seguimientos = %s, test_drive = %s, habeas_data = %s, aceptacion_tratamiento_datos = %s, precio_venta = %s
            WHERE id = %s
        """
        params = [
            data['nombres'], data['apellidos'], data['identificacion'], data['telefono'],
            data['direccion'], data['ciudad'], data['correo'], data['origen_lead'],
            data['marca_interes'], data['modelo_interesado'], data['estatus'], data['asignado'], data['asignado_a'],
            data.get('seguimientos', ''), data.get('test_drive', 'No'),
            data['habeas_data'], data['aceptacion_tratamiento_datos'], data.get('precio_venta'), data['id']
        ]

        # 🔹 Ejecutar la consulta
        cursor.execute(query, params)
        conn.commit()
        print(f"✅ Lead {data['id']} actualizado correctamente por gerente.") 

        # 🔹 Registrar en la auditoría
        for cambio in cambios_realizados:
            auditoria_query = """
                INSERT INTO auditoria (usuario_id, accion, tabla_afectada, registro_id, campo_modificado, valor_anterior, valor_nuevo, comentarios)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            auditoria_values = (
                data['usuario_id'], 'Actualización por gerente', 'leads', data['id'], cambio['campo'],
                str(cambio['valor_anterior']), str(cambio['valor_nuevo']), f"Modificado por gerente"
            )
            cursor.execute(auditoria_query, auditoria_values)
        conn.commit()

        return jsonify({"message": "Lead actualizado por el gerente correctamente"}), 200

    except Exception as e:
        conn.rollback()
        print(f"❌ Error en la actualización por gerente: {e}")  
        return jsonify({"error": "Error en la actualización por gerente", "details": str(e)}), 500


# Ruta para obtener la información del usuario logueado
@app.route('/user-info', methods=['GET'])
def user_info():
    user_data = {
        'es_administrador': True
    }
    return jsonify(user_data), 200

# Ruta para obtener concesionarios
@app.route('/get-concesionarios', methods=['GET'])
def get_concesionarios():
    cursor.execute("SELECT id, nombre_concesionario, ciudad, marcas FROM concesionarios")
    concesionarios = cursor.fetchall()

    if not concesionarios:
        return jsonify([]), 200  # ✅ Si no hay datos, devolver un array vacío

    concesionarios_list = []
    for row in concesionarios:
        try:
            concesionarios_list.append({
                "id": row[0],
                "nombre_concesionario": row[1],
                "ciudad": row[2],
                "marcas": list(row[3]) if isinstance(row[3], list) else []  # ✅ Convertir ARRAY de PostgreSQL a lista de Python
            })
        except IndexError:
            print(f"⚠️ Error en la fila: {row}")  # Depuración si hay problemas con alguna fila

    return jsonify(concesionarios_list), 200


# Ruta para agregar concesionario
@app.route('/add-concesionario', methods=['POST'])
def add_concesionario():
    try:
        data = request.json
        nombre = data['nombre_concesionario']
        ciudad = data['ciudad']
        marcas = data['marcas']

        cur = conn.cursor()
        marcas_array = '{' + ','.join(marcas) + '}'

        cur.execute(
            "INSERT INTO concesionarios (nombre_concesionario, ciudad, marcas) VALUES (%s, %s, %s)",
            (nombre, ciudad, marcas_array)
        )
        conn.commit()
        cur.close()

        return jsonify({"message": "Concesionario agregado exitosamente"}), 200

    except Exception as e:
        print(f"Error al agregar concesionario: {e}")
        return jsonify({"error": str(e)}), 500

# Ruta para actualizar concesionario
@app.route('/update-concesionario', methods=['POST'])
def update_concesionario():
    data = request.json
    cur = conn.cursor()
    cur.execute(
        "UPDATE concesionarios SET nombre_concesionario = %s, ciudad = %s, marcas = %s WHERE id = %s",
        (data['nombre_concesionario'], data['ciudad'], '{' + ','.join(data['marcas']) + '}', data['id'])
    )
    conn.commit()
    cur.close()
    return jsonify({"message": "Concesionario actualizado exitosamente"}), 200

# Ruta para eliminar un concesionario
@app.route('/delete-concesionario', methods=['POST'])
def delete_concesionario():
    try:
        data = request.json
        concesionario_id = data.get('id')

        if not concesionario_id:
            return jsonify({"error": "ID del concesionario no proporcionado"}), 400

        cur = conn.cursor()

        # Verificar si hay leads asociados a este concesionario
        cur.execute("SELECT COUNT(*) FROM leads WHERE concesionario_id = %s", (concesionario_id,))
        leads_count = cur.fetchone()[0]

        if leads_count > 0:
            print(f"🔄 Reasignando {leads_count} leads al concesionario 'Sin asignar' (ID: 9999)...")
            cur.execute("UPDATE leads SET concesionario_id = 9999 WHERE concesionario_id = %s", (concesionario_id,))
            conn.commit()

        # Verificar si hay usuarios asignados a este concesionario
        cur.execute("SELECT COUNT(*) FROM usuarios WHERE concesionario = (SELECT nombre_concesionario FROM concesionarios WHERE id = %s)", (concesionario_id,))
        usuarios_count = cur.fetchone()[0]

        if usuarios_count > 0:
            print(f"🔄 Actualizando {usuarios_count} usuarios que tenían asignado este concesionario...")
            cur.execute("UPDATE usuarios SET concesionario = NULL WHERE concesionario = (SELECT nombre_concesionario FROM concesionarios WHERE id = %s)", (concesionario_id,))
            conn.commit()

        # Eliminar el concesionario
        cur.execute("DELETE FROM concesionarios WHERE id = %s", (concesionario_id,))
        conn.commit()
        cur.close()

        return jsonify({"message": "Concesionario eliminado exitosamente"}), 200

    except Exception as e:
        conn.rollback()
        print(f"❌ Error al eliminar concesionario: {e}")
        return jsonify({"error": "Error al eliminar el concesionario", "details": str(e)}), 500


# Ruta para agregar un usuario
@app.route('/add-usuario', methods=['POST'])
def add_usuario():
    try:
        data = request.json
        usuario = data['usuario']
        password = data['password']
        concesionario = data['concesionario']
        tipo_usuario = data['tipo_usuario']
        nombres = data['nombres']
        apellidos = data['apellidos']
        celular = data.get('celular', '')  # Nuevo campo con valor por defecto
        correo = data.get('correo', '')   
        marca_asignada = data.get('marca_asignada', '')  # Nuevo campo
        # Determinar si el usuario es administrador o no basado en `tipo_usuario`
        es_administrador = tipo_usuario == 'administrador'

        cursor.execute("""
            INSERT INTO usuarios (usuario, password, concesionario, es_administrador, tipo_usuario, nombres, apellidos, celular, correo, marca_asignada)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (usuario, password, concesionario, es_administrador, tipo_usuario, nombres, apellidos, celular, correo, marca_asignada))
        
        conn.commit()
        return jsonify({"message": "Usuario agregado exitosamente"}), 200

    except Exception as e:
        print(f"Error al agregar usuario: {e}")
        return jsonify({"error": str(e)}), 500

# Ruta para actualizar un usuario
@app.route('/update-usuario', methods=['POST'])
def update_usuario():
    try:
        data = request.json
        es_administrador = data['tipo_usuario'] == 'administrador'
    
        query = """
            UPDATE usuarios
            SET usuario = %s, password = %s, concesionario = %s, 
                es_administrador = %s, tipo_usuario = %s, activo = %s,
                nombres = %s, apellidos = %s, celular = %s, correo = %s, marca_asignada = %s
            WHERE id = %s
        """
        values = (
            data['usuario'], data['password'], data['concesionario'], 
            es_administrador, data['tipo_usuario'], data['activo'], 
            data['nombres'], data['apellidos'], data.get('celular', ''), 
            data.get('correo', ''), data.get('marca_asignada', ''), data['id']
        )
        cursor.execute(query, values)
        conn.commit()
        return jsonify({"message": "Usuario actualizado exitosamente"}), 200
    except Exception as e:
        print(f"Error al actualizar usuario: {e}")
        return jsonify({"error": str(e)}), 500

# Ruta para obtener usuarios
@app.route('/get-usuarios', methods=['GET'])
def get_usuarios():
    cursor.execute("SELECT * FROM usuarios;")
    usuarios = cursor.fetchall()

    usuarios_list = []
    for user in usuarios:
        usuarios_list.append({
            "id": user[0],
            "usuario": user[1],
            "password": user[2],
            "concesionario": user[3] if len(user) > 3 else "",
            "es_administrador": user[4] if len(user) > 4 else False,
            "tipo_usuario": user[5] if len(user) > 5 else "vendedor",
            "fecha_creacion": str(user[6]) if len(user) > 6 else "",
            "activo": user[7] if len(user) > 7 else True,
            "nombres": user[8] if len(user) > 8 else "",
            "apellidos": user[9] if len(user) > 9 else "",
            "en_linea": user[10] if len(user) > 10 else False,
            "ultima_conexion": str(user[11]) if len(user) > 11 else "",
            "ultima_puesta_online": str(user[12]) if len(user) > 12 else "",
            "celular": user[13] if len(user) > 13 else "",   # Campo celular mapeado correctamente
            "correo": user[14] if len(user) > 14 else ""     # Campo correo mapeado correctamente
        })

    return jsonify(usuarios_list), 200


@app.route('/asignar-lead', methods=['POST'])
def asignar_lead():
    data = request.get_json()
    vendedor_id = data['vendedor_id']

    print(f"📌 Recibido POST en /asignar-lead con vendedor_id: {vendedor_id}")  # 👀 Log de entrada

    # 🔎 Verificar si el vendedor ya tiene un lead asignado con estado "asignado"
    cursor.execute("""
        SELECT id, nombres, apellidos, identificacion, telefono, direccion, ciudad, correo, fecha_lead, origen_lead, 
               marca_interes, modelo_interesado, estatus, asignado, asignado_a, fecha_asignacion, seguimientos
        FROM leads 
        WHERE asignado_a = %s AND asignado = true AND estatus = 'asignado'
    """, (vendedor_id,))
    lead_asignado = cursor.fetchone()

    if lead_asignado:
        print(f"✅ El vendedor {vendedor_id} ya tiene un lead asignado. No se asignará otro.")  # 👀
        return jsonify({
            "message": "Vendedor ya tiene un lead asignado.",
            "lead_asignado": {
                "id": lead_asignado[0],
                "nombres": lead_asignado[1],
                "apellidos": lead_asignado[2],
                "identificacion": lead_asignado[3],
                "telefono": lead_asignado[4],
                "direccion": lead_asignado[5],
                "ciudad": lead_asignado[6],
                "correo": lead_asignado[7],
                "fecha_lead": str(lead_asignado[8]),
                "origen_lead": lead_asignado[9],
                "marca_interes": lead_asignado[10],
                "modelo_interesado": lead_asignado[11],
                "estatus": lead_asignado[12],
                "asignado": lead_asignado[13],
                "asignado_a": lead_asignado[14],
                "fecha_asignacion": str(lead_asignado[15]) if lead_asignado[15] else None,
                "seguimientos": lead_asignado[16]
            }
        }), 200

    # 🔎 Obtener información del vendedor y su concesionario
    cursor.execute("""
        SELECT celular, correo, nombres, apellidos, concesionario 
        FROM usuarios 
        WHERE id = %s
    """, (vendedor_id,))
    resultado_vendedor = cursor.fetchone()

    if not resultado_vendedor:
        print("❌ Error: No se encontró el vendedor en la BD.")  # 👀
        return jsonify({"message": "No se encontró el vendedor."}), 404

    vendedor_celular, vendedor_correo, vendedor_nombres, vendedor_apellidos, concesionario_vendedor = resultado_vendedor
    print(f"✅ Vendedor encontrado: {vendedor_nombres} {vendedor_apellidos}, Concesionario: {concesionario_vendedor}")

    # 🔎 Obtener las marcas del concesionario del vendedor
    cursor.execute("""
        SELECT id, ciudad, marcas 
        FROM concesionarios 
        WHERE nombre_concesionario = %s
    """, (concesionario_vendedor,))
    resultado_concesionario = cursor.fetchone()

    if not resultado_concesionario:
        print("❌ Error: El concesionario del vendedor no existe.")  # 👀
        return jsonify({"message": "El concesionario del vendedor no existe."}), 404

    concesionario_id_vendedor, ciudad_vendedor, marcas_vendedor = resultado_concesionario
    print(f"✅ Concesionario encontrado: {concesionario_id_vendedor}, Ciudad: {ciudad_vendedor}, Marcas: {marcas_vendedor}")

    # 🔹 Convertimos las marcas del concesionario en una lista segura
    if isinstance(marcas_vendedor, str):
        marcas_vendedor = [m.strip() for m in marcas_vendedor.strip("{}").split(",")]
    elif marcas_vendedor is None:
        marcas_vendedor = []

    print(f"🔹 Marcas procesadas: {marcas_vendedor}")  # 👀

    lead = None

    # 🔎 Buscar un lead en el mismo concesionario del vendedor
    if concesionario_id_vendedor:
        cursor.execute("""
            SELECT id, nombres, apellidos, identificacion, telefono, direccion, ciudad, correo, fecha_lead, 
                origen_lead, marca_interes, modelo_interesado, estatus, asignado, concesionario_id
            FROM leads
            WHERE concesionario_id = %s
            AND estatus = 'nuevo'
            AND asignado = false
            LIMIT 1;
        """, (concesionario_id_vendedor,))
        lead = cursor.fetchone()

    # ✅ Optimización: Si no hay leads en concesionario, pasar **inmediatamente** a buscar sin concesionario
    if not lead:
        print("❌ No hay leads en concesionario. Buscando leads sin concesionario...")

        cursor.execute("""
            SELECT id, nombres, apellidos, identificacion, telefono, direccion, ciudad, correo, 
                fecha_lead, origen_lead, marca_interes, modelo_interesado, estatus, asignado, concesionario_id
            FROM leads
            WHERE estatus = 'nuevo'
            AND asignado = false
            AND concesionario_id IS NULL
            AND marca_interes = ANY(%s)
            LIMIT 1;
        """, (marcas_vendedor,))
        lead = cursor.fetchone()

    # 🔎 Si aún no hay leads, buscar por ciudad y marca
    if not lead and ciudad_vendedor:
        cursor.execute("""
            SELECT id, nombres, apellidos, identificacion, telefono, direccion, ciudad, correo, fecha_lead, 
                origen_lead, marca_interes, modelo_interesado, estatus, asignado, concesionario_id
            FROM leads
            WHERE ciudad = %s
            AND estatus = 'nuevo'
            AND asignado = false
            AND marca_interes = ANY(%s)
            LIMIT 1;
        """, (ciudad_vendedor, marcas_vendedor))
        lead = cursor.fetchone()

    if not lead:
        print("🚫 No hay leads disponibles para asignar.")  # 👀
        return jsonify({"message": "No hay leads disponibles para asignar."}), 200


    lead_id, nombres, apellidos, identificacion, telefono, direccion, ciudad, correo, fecha_lead, origen_lead, marca_interes, modelo_interesado, estatus, asignado, concesionario_id = lead

    # 🏆 **Asignar el lead al vendedor**
    fecha_asignacion = get_current_time_colombia()
    cursor.execute("""
        UPDATE leads
        SET asignado_a = %s, estatus = 'asignado', asignado = true, fecha_asignacion = %s
        WHERE id = %s
    """, (vendedor_id, fecha_asignacion, lead_id))
    conn.commit()
    print(f"✅ Lead {lead_id} asignado a {vendedor_nombres}")  # 👀

    # 🔔 **Enviar notificación de WhatsApp**
    if vendedor_celular:
        try:
            enviar_notificacion_whatsapp(vendedor_celular)
            
        except Exception as e:
            print(f"Error enviando mensaje de WhatsApp: {e}")

    # 📩 **Enviar notificación por correo electrónico**
    if vendedor_correo:
        try:
            enviar_correo(
                destinatario=vendedor_correo,
                asunto="Nuevo Lead Asignado",
                #mensaje=f"Hola {vendedor_nombres}, tienes un nuevo lead asignado: {nombres} {apellidos}, Tel: {telefono}."
                mensaje = f"""
                Cordial saludo {vendedor_nombres},<br><br>
                Desde el sistema LeadsMass se te ha asignado un un nuevo lead para contactarlo y gestionar un test drive.<br>
                <ul>
                    <li><b>Nombres:</b> {nombres}</li>
                    <li><b>Apellidos:</b> {apellidos}</li>
                    <li><b>Ciudad:</b> {ciudad}</li>
                    <li><b>Fecha del Lead:</b> {get_current_time_colombia().date()}</li>
                    <li><b>Origen del Lead:</b> {origen_lead}</li>
                    <li><b>Marca:</b> {marca_interes}</li>
                    
                </ul>
                Para mas información sobre este Lead, por favor ingresa a nuestro sistema.<br><br>
                Cordialmente,<br>Sistema LeadsMass
                """
            )
        except Exception as e:
            print(f"Error enviando correo electrónico: {e}")

    # 🏆 **Devolver el lead asignado**
    return jsonify({
        "message": "Lead asignado exitosamente",
        "lead_asignado": {
            "id": lead[0],
            "nombres": lead[1],
            "apellidos": lead[2],
            "identificacion": lead[3],
            "telefono": lead[4],
            "direccion": lead[5],
            "ciudad": lead[6],
            "correo": lead[7],
            "fecha_lead": str(lead[8]),
            "origen_lead": lead[9],
            "marca_interes": lead[10],
            "modelo_interesado": lead[11],
            "estatus": lead[12],
            "asignado": lead[13],
            "concesionario_id": lead[14]
        }
    }), 200




@app.route('/update-vendedor-estado', methods=['POST'])
def update_vendedor_estado():
    data = request.json
    vendedor_id = data['vendedor_id']
    estado = data['estado']  # Recibe el estado como True para 'En línea' o False para 'Fuera de línea'

    # Actualizar el estado en la base de datos
    cursor.execute("UPDATE usuarios SET en_linea = %s WHERE id = %s", (estado, vendedor_id))

    if estado:
        # Registrar la fecha de la última puesta en línea
        cursor.execute("UPDATE usuarios SET ultima_puesta_online = %s WHERE id = %s", (get_current_time_colombia(), vendedor_id))

        # Verificar si el vendedor ya tiene un lead asignado y su estatus
        cursor.execute("""
            SELECT id, nombres, apellidos, marca_interes, estatus, asignado
            FROM leads 
            WHERE asignado_a = %s AND asignado = true
        """, (vendedor_id,))
        lead_asignado = cursor.fetchone()

        conn.commit()  # Consolidar los commits en uno solo

        # Depuración para ver qué retorna la consulta
        print(f"Lead asignado al vendedor {vendedor_id}: {lead_asignado}")

        # Si el vendedor tiene un lead asignado, devolver sus detalles
        if lead_asignado:
            return jsonify({
                "message": "Vendedor en línea y ya tiene un lead asignado.",
                "lead_asignado": {
                    "id": lead_asignado[0],
                    "nombres": lead_asignado[1],
                    "apellidos": lead_asignado[2],
                    "marca_interes": lead_asignado[3],
                    "estatus": lead_asignado[4]
                }
            }), 200
        else:
            print(f"No hay leads asignados para el vendedor {vendedor_id}")
            return jsonify({
                "message": "Vendedor en línea, pero no tiene un lead asignado."
            }), 200

    else:
        # Registrar la última conexión al ponerse fuera de línea
        cursor.execute("UPDATE usuarios SET ultima_conexion = %s WHERE id = %s", (get_current_time_colombia(), vendedor_id))
        conn.commit()  # Commit aquí ya que este es un flujo alternativo

        print(f"Vendedor {vendedor_id} se ha puesto fuera de línea.")
        return jsonify({"message": "Estado del vendedor actualizado exitosamente"}), 200

@app.route('/tiempo-ultima-conexion', methods=['GET'])
def tiempo_ultima_conexion():
    vendedor_id = request.args.get('vendedor')

    cursor.execute("""
        SELECT ultima_conexion, ultima_puesta_online 
        FROM usuarios 
        WHERE id = %s
    """, (vendedor_id,))
    resultado = cursor.fetchone()

    if resultado:
        ultima_conexion, ultima_puesta_online = resultado
        
        # Formatear las fechas
        ultima_conexion_str = ultima_conexion.strftime("%Y-%m-%d %H:%M:%S") if ultima_conexion else "Sin conexión registrada"
        ultima_puesta_online_str = ultima_puesta_online.strftime("%Y-%m-%d %H:%M:%S") if ultima_puesta_online else "Sin registro"

        return jsonify({
            "fecha_ultima_conexion": ultima_conexion_str,
            "ultima_puesta_online": ultima_puesta_online_str
        }), 200
    else:
        return jsonify({"message": "No se encontró el vendedor."}), 404


@app.route('/get-vendedores', methods=['GET'])
def get_vendedores():
    cursor.execute("SELECT id, nombres, apellidos FROM usuarios WHERE tipo_usuario = 'vendedor'")
    vendedores = cursor.fetchall()

    result = [{"id": vendedor[0], "nombre": f"{vendedor[1]} {vendedor[2]}"} for vendedor in vendedores]

    return jsonify(result), 200

# Ruta para exportar el reporte en PDF o CSV
@app.route('/exportar-reporte', methods=['POST'])
def exportar_reporte():
#    data = request.get_json()
#    leads = data['leads']
#    formato = data.get('formato', 'pdf')

    data = request.get_json()
    leads = data['leads']
    formato = data.get('formato', 'pdf')
    vendedor = data.get('vendedor', None)
    filtro_estado = data.get('filtro_estado', None)
    filtroTestDrive = data.get('filtroTestDrive', None)
    vendedor_nombre_completo = None

    # Obtener el nombre completo del vendedor si se especifica el ID
    if vendedor:  # Asegurarse de que vendedor está definido
        cursor.execute("SELECT nombres, apellidos FROM usuarios WHERE id = %s", (vendedor,))
        vendedor = cursor.fetchone()
        if vendedor:
            vendedor_nombre_completo = f"{vendedor[0]} {vendedor[1]}"

    if formato == 'pdf':
        # Generar y devolver PDF
        #pdf = create_pdf(leads)
        pdf = create_pdf(leads, vendedor=vendedor, filtro_estado=filtro_estado, filtroTestDrive=filtroTestDrive, vendedor_nombre_completo=vendedor_nombre_completo)
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=reporte_leads.pdf'
        return response

    elif formato == 'csv':
        # Generar y devolver CSV con punto y coma como delimitador
        csv_content = "id;nombres;apellidos;identificacion;telefono;direccion;ciudad;correo;fecha_lead;origen_lead;marca_interes;modelo_interesado;estatus;test_drive;asignado;seguimientos\n"
        for lead in leads:
            # Asegurar que 'seguimientos' está entrecomillado para manejar posibles saltos de línea
            csv_content += ";".join([
                str(lead.get('id', '')),
                lead.get('nombres', ''),
                lead.get('apellidos', ''),
                lead.get('identificacion', ''),
                lead.get('telefono', ''),
                lead.get('direccion', ''),
                lead.get('ciudad', ''),
                lead.get('correo', ''),
                str(lead.get('fecha_lead', '')).split(" ")[0],  # Solo la fecha en formato "YYYY-MM-DD"
                lead.get('origen_lead', ''),
                lead.get('marca_interes', ''),
                lead.get('modelo_interesado', ''),
                lead.get('estatus', ''),
                lead.get('test_drive', ''),
                str(lead.get('asignado', '')),
                f'"{lead.get("seguimientos", "").replace(chr(10), " ").replace(chr(13), " ")}"'  # Remover saltos de línea
            ]) + "\n"

        response = make_response(csv_content)
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = 'attachment; filename=reporte_leads.csv'
        return response

    return jsonify({"error": "Formato no soportado"}), 400


# Ruta para exportar el reporte en PDF o CSV
@app.route('/exportar-reporte-gerente', methods=['POST'])
def exportar_reporte_gerente():
    """
    Exportar reporte de leads en formato PDF o CSV.
    Permite filtros por vendedor, marca, estado, test drive y rango de fechas.
    """
    try:
        # Obtener datos del cuerpo de la solicitud
        data = request.get_json()
        leads = data.get('leads', [])
        formato = data.get('formato', 'pdf')
        vendedor_id = data.get('vendedor', None)  # Ahora usamos el ID del vendedor
        filtro_marca = data.get('filtro_marca', None)
        filtro_estado = data.get('filtro_estado', None)
        filtroTestDrive = data.get('filtroTestDrive', None)
        fechaDesde = data.get('fechaDesde', None)
        fechaHasta = data.get('fechaHasta', None)

        print("🔍 Leads recibidos en el backend:", len(leads))  # 🔥 Ver cuántos leads llegan
        print("🔍 Primer lead recibido:", leads[0] if leads else "No hay leads")


        # Convertir fechas de cadena a objeto de fecha, si están presentes
        from datetime import datetime
        fechaDesde = datetime.strptime(fechaDesde, '%Y-%m-%d').date() if fechaDesde else None
        fechaHasta = datetime.strptime(fechaHasta, '%Y-%m-%d').date() if fechaHasta else None

        # 🔍 DEPURACIÓN: Revisar IDs antes de filtrar
        print(f"🔎 Vendedor ID recibido: {vendedor_id}")
        print(f"🔎 Leads antes de filtrar por vendedor: {len(leads)}")

        # Aplicar filtros en la lista de leads antes de generar el reporte
        if vendedor_id is not None:
            vendedor_id = int(vendedor_id)  # Asegurar que sea un número
            leads = [lead for lead in leads if int(lead.get('asignado_a', 0)) == vendedor_id]  # ✅ Conversión segura
            print(f"✅ Leads después de filtrar por vendedor: {len(leads)}")  # Depuración

        if filtro_marca:
            leads = [lead for lead in leads if lead.get('marca_interes') == filtro_marca]
        if filtro_estado:
            leads = [lead for lead in leads if lead.get('estatus') == filtro_estado]
        if filtroTestDrive:
            leads = [lead for lead in leads if lead.get('test_drive') == filtroTestDrive]
        if fechaDesde or fechaHasta:
            leads = [
                lead for lead in leads
                if (
                    (not fechaDesde or datetime.strptime(lead['fecha_lead'], '%Y-%m-%d').date() >= fechaDesde) and
                    (not fechaHasta or datetime.strptime(lead['fecha_lead'], '%Y-%m-%d').date() <= fechaHasta)
                )
            ]

        # Obtener nombre del vendedor si se aplica el filtro
        vendedor_nombre_completo = None
       # ✅ Filtrar por asignado_a (ID del vendedor) en vez de vendedor_nombre
        if vendedor_id:
            # Obtener el nombre del vendedor basándonos en su ID
            cursor.execute("SELECT nombres, apellidos FROM usuarios WHERE id = %s", (vendedor_id,))
            vendedor_data = cursor.fetchone()
            if vendedor_data:
                vendedor_nombre_completo = f"{vendedor_data[0]} {vendedor_data[1]}"
                print(f"🔍 Nombre del vendedor filtrado: {vendedor_nombre_completo}")
                
                # Filtrar por nombre del vendedor en lugar de `asignado_a`
                leads = [lead for lead in leads if lead.get('vendedor_nombre') == vendedor_nombre_completo]



        # Generar PDF
        if formato == 'pdf':
            pdf = create_pdf_gerente(
                leads,
                vendedor_nombre_completo=vendedor_nombre_completo,
                filtro_estado=filtro_estado,
                filtroTestDrive=filtroTestDrive,
                filtro_marca=filtro_marca,
                fechaDesde=fechaDesde,
                fechaHasta=fechaHasta
            )
            response = make_response(pdf)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = 'attachment; filename=reporte_leads.pdf'
            return response

        # Generar CSV
        elif formato == 'csv':
            csv_content = "vendedor;nombres;apellidos;identificacion;telefono;direccion;ciudad;correo;fecha_lead;origen_lead;marca_interes;modelo_interesado;estatus;test_drive;seguimientos\n"
            for lead in leads:
                csv_content += ";".join([
                    str(lead.get('vendedor_nombre', '') or ''),
                    str(lead.get('nombres', '') or ''),
                    str(lead.get('apellidos', '') or ''),
                    str(lead.get('identificacion', '') or ''),
                    str(lead.get('telefono', '') or ''),
                    str(lead.get('direccion', '') or ''),
                    str(lead.get('ciudad', '') or ''),
                    str(lead.get('correo', '') or ''),
                    str(lead.get('fecha_lead', '') or '').split(" ")[0],  # Formato YYYY-MM-DD
                    str(lead.get('origen_lead', '') or ''),
                    str(lead.get('marca_interes', '') or ''),
                    str(lead.get('modelo_interesado', '') or ''),
                    str(lead.get('estatus', '') or ''),
                    str(lead.get('test_drive', '') or ''),
                    f'"{str(lead.get("seguimientos", "") or "").replace(chr(10), " ").replace(chr(13), " ")}"'
                ]) + "\n"

            response = make_response(csv_content)
            response.headers['Content-Type'] = 'text/csv'
            response.headers['Content-Disposition'] = 'attachment; filename=reporte_leads.csv'
            return response

        # Si el formato no es soportado, devolver un error
        return jsonify({"error": "Formato no soportado"}), 400

    except Exception as e:
        print(f"❌ Error al exportar reporte gerente: {str(e)}")
        return jsonify({"error": "Error interno al exportar reporte", "details": str(e)}), 500



# Endpoint para eliminar un lead
@app.route('/delete-lead', methods=['POST'])
def delete_lead():
    data = request.get_json()
    print("Datos recibidos para eliminación:", data)  # Depuración
    lead_id = data.get('lead_id')
    usuario_id = data.get('usuario_id')  # Usuario que realiza la acción

    if not lead_id:
        return jsonify({"error": "ID del lead no proporcionado"}), 400
    if not usuario_id:
        return jsonify({"error": "Usuario no identificado"}), 400

    try:
        # Recuperar datos del lead antes de eliminar para la auditoría
        cursor.execute("SELECT * FROM leads WHERE id = %s", (lead_id,))
        lead = cursor.fetchone()

        if not lead:
            return jsonify({"error": "Lead no encontrado"}), 404

        # Obtener los nombres de las columnas de la tabla "leads"
        columnas = [desc[0] for desc in cursor.description]

        # Crear una descripción detallada de los datos eliminados para la auditoría
        datos_eliminados = {columnas[i]: str(lead[i]) for i in range(len(columnas))}

        # Eliminar el lead
        cursor.execute("DELETE FROM leads WHERE id = %s", (lead_id,))
        conn.commit()

        # Registrar la acción en auditoría
        auditoria_query = """
            INSERT INTO auditoria (usuario_id, accion, tabla_afectada, registro_id, comentarios, campo_modificado, valor_anterior)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        auditoria_values = (
            usuario_id, 'Eliminación', 'leads', lead_id, 'Lead eliminado del sistema',
            'Datos eliminados', str(datos_eliminados)
        )
        cursor.execute(auditoria_query, auditoria_values)
        conn.commit()

        return jsonify({"message": "Lead eliminado exitosamente"}), 200

    except Exception as e:
        conn.rollback()
        print("Error al eliminar lead:", e)
        return jsonify({"error": "Error al eliminar el lead", "details": str(e)}), 500




# Ruta para contar los leads capturados por el usuario Expert en la fecha actual
@app.route('/count-leads-today', methods=['GET'])
def count_leads_today():
    user_id = request.args.get('user_id')  # Obtener el ID del usuario desde el frontend
    today = get_current_time_colombia().date()  # Fecha actual

    cursor.execute("""
        SELECT COUNT(*) FROM leads
        WHERE fecha_lead = %s AND origen_lead = 'Evento' AND capturado_por = %s
    """, (today, user_id))

    count = cursor.fetchone()[0]
    return jsonify({"count": count}), 200

# Ruta para obtener el contador de leads capturados por un Expert en la fecha actual
@app.route('/get-leads-count-expert', methods=['GET'])
def get_leads_count_expert():
    user_id = request.args.get('user_id')

    if not user_id:
        return jsonify({"error": "Falta el ID del usuario"}), 400

    fecha_actual = get_current_time_colombia().date()  # Fecha en formato `YYYY-MM-DD`

    query = """
        SELECT COUNT(*) FROM leads
        WHERE capturado_por = %s 
        AND DATE(fecha_lead) = %s::DATE
    """  # ✅ Se asegura de comparar correctamente `fecha_lead` con `fecha_actual`

    print(f"🔍 Query Ejecutada: {query} - Params: {user_id}, {fecha_actual}")

    cursor.execute(query, (user_id, fecha_actual))
    result = cursor.fetchone()

    count = result[0] if result else 0

    print(f"🛠️ Debug: Usuario {user_id} - Fecha actual: {fecha_actual} - Leads hoy: {count}")

    return jsonify({"count": count}), 200


# Envio de correso de prueba de correo gmail desde leadbridgesystem@gmail.com usando sendgrid
@app.route('/test-email', methods=['POST'])
def test_email():
    """Endpoint para enviar un correo de prueba."""
    data = request.get_json()
    destinatario = data.get('destinatario')
    asunto = data.get('asunto', "Prueba de Envío de Correo")
    mensaje = data.get('mensaje', "Este es un mensaje de prueba desde LeadBridge.")

    try:
        enviar_correo(destinatario=destinatario, asunto=asunto, mensaje=mensaje)
        return jsonify({"message": "Correo de prueba enviado exitosamente"}), 200
    except Exception as e:
        return jsonify({"error": f"Error al enviar el correo: {e}"}), 500


# Endpoint para probar el envío de notificaciones
@app.route('/test-whatsapp-notification', methods=['POST'])
def test_whatsapp_notification():
    data = request.get_json()
    telefono = data.get("telefono")

    if not telefono:
        return jsonify({"error": "Se requiere un número de teléfono"}), 400

    try:
        mensaje_sid = enviar_notificacion_whatsapp(telefono)
        return jsonify({"message": "Mensaje enviado exitosamente", "sid": mensaje_sid}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint para consultar estado de conexión  de un vendedor
@app.route('/estado-vendedores', methods=['GET'])
def estado_vendedores():
    try:
        # Consultar el estado de los vendedores en la tabla de usuarios
        cursor.execute("""
            SELECT id, nombres, apellidos, en_linea 
            FROM usuarios
            WHERE tipo_usuario = 'vendedor'
        """)
        vendedores = cursor.fetchall()

        # Formatear los datos de los vendedores
        vendedores_estado = [
            {
                "id": vendedor[0],
                "nombre": f"{vendedor[1]} {vendedor[2]}",
                "en_linea": vendedor[3]
            }
            for vendedor in vendedores
        ]

        return jsonify({"vendedores": vendedores_estado}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get-usuarios-expert', methods=['GET'])
def get_usuarios_expert():
    # Selecciona usuarios de tipo "expert"
    cursor.execute("""
        SELECT id, nombres, apellidos FROM usuarios WHERE tipo_usuario = 'expert'
    """)
    expertos = cursor.fetchall()

    # Formatea los resultados para la respuesta
    expertos_list = [{"id": experto[0], "nombre": f"{experto[1]} {experto[2]}"} for experto in expertos]

    return jsonify(expertos_list), 200

@app.route('/leads-capturados-expert', methods=['GET'])
def leads_capturados_expert():
    expert_id = request.args.get('expert_id')
    fecha = request.args.get('fecha')
    
    query = "SELECT * FROM leads WHERE capturado_por IS NOT NULL"  # Asegura que solo obtenga leads capturados por expertos
    params = []

    if expert_id:
        query += " AND capturado_por = %s"
        params.append(expert_id)

    if fecha:
        query += " AND fecha_lead = %s"
        params.append(fecha)

    cursor.execute(query, params)
    leads = cursor.fetchall()

    # Formatear los leads para enviarlos en la respuesta
    leads_list = [{
        "id": lead[0],
        "nombres": lead[1],
        "apellidos": lead[2],
        "identificacion": lead[3],
        "telefono": lead[4],
        "direccion": lead[5],
        "ciudad": lead[6],
        "correo": lead[7],
        "fecha_lead": str(lead[8]),
        "origen_lead": lead[9],
        "marca_interes": lead[10],
        "modelo_interesado": lead[11],
        "estatus": lead[12],
        "asignado": lead[13],
        "seguimientos": lead[14],
        "test_drive": lead[15],
        "capturado_por": lead[16],
        "habeas_data": lead[17]
    } for lead in leads]

    return jsonify(leads_list), 200

@app.route('/consultar-rne', methods=['POST'])
def consultar_rne():
    """
    Endpoint para consultar el RNE y registrar los resultados en la tabla log_consultas_rne.
    """
    data = request.json
    telefono = data.get('telefono')
    correo = data.get('correo')
    vendedor_id = data.get('vendedor_id')  # ID del vendedor enviado por el frontend

    if not vendedor_id:
        print("Error: vendedor_id no proporcionado en la solicitud.")
        return jsonify({"error": "El vendedor_id es obligatorio"}), 400


    url = "https://tramitescrcom.gov.co/excluidosback/consultaMasiva/validarExcluidos"
    token = os.getenv("CRC_TOKEN")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    def realizar_consulta(payload):
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error al realizar la consulta: {e}")
            return None

    results = {"telefono": None, "correo": None}

    if telefono:
        payload_tel = {"type": "TEL", "keys": [telefono]}
        data_tel = realizar_consulta(payload_tel)
        results["telefono"] = data_tel[0] if data_tel else None

    if correo:
        payload_correo = {"type": "COR", "keys": [correo]}
        data_correo = realizar_consulta(payload_correo)
        results["correo"] = data_correo[0] if data_correo else None

    # Preparar los datos para la base de datos
    consulta_data = {
        "vendedor_id": vendedor_id,
        "consulta_tel": telefono or None,
        "consulta_corr": correo or None,
        "fecha_consulta": get_current_time_colombia(),
        "tipo": results["telefono"].get("tipo", "NR") if results["telefono"] else "NR",
        "sms": "S" if results["telefono"] and results["telefono"].get("opcionesContacto", {}).get("sms") else "NR",
        "aplicacion": "S" if results["telefono"] and results["telefono"].get("opcionesContacto", {}).get("aplicacion") else "NR",
        "llamada": "S" if results["telefono"] and results["telefono"].get("opcionesContacto", {}).get("llamada") else "NR",
        "fecha_creacion_tel": results["telefono"].get("fechaCreacion", None) if results["telefono"] else None,
        "aplicacion_corr": "S" if results["correo"] and results["correo"].get("opcionesContacto", {}).get("aplicacion") else "NR",
        "correo_corr": "S" if results["correo"] and results["correo"].get("opcionesContacto", {}).get("correo_electronico") else "NR",
        "fecha_creacion_corr": results["correo"].get("fechaCreacion", None) if results["correo"] else None,
    }

    try:
        query = """
            INSERT INTO log_consultas_rne (
                vendedor_id, consulta_tel, fecha_consulta, tipo, sms, aplicacion, llamada,
                fecha_creacion_tel, consulta_corr, aplicacion_corr, correo_corr, fecha_creacion_corr
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            consulta_data["vendedor_id"],
            consulta_data["consulta_tel"],
            consulta_data["fecha_consulta"],
            consulta_data["tipo"],
            consulta_data["sms"],
            consulta_data["aplicacion"],
            consulta_data["llamada"],
            consulta_data["fecha_creacion_tel"],
            consulta_data["consulta_corr"],
            consulta_data["aplicacion_corr"],
            consulta_data["correo_corr"],
            consulta_data["fecha_creacion_corr"],
        )
        cursor.execute(query, values)
        conn.commit()
        print(f"Datos insertados en log_consultas_rne: {values}")
    except Exception as e:
        print(f"Error al insertar en la base de datos: {e}")
        conn.rollback()
        return jsonify({"error": "Error al insertar en la base de datos"}), 500

    return jsonify(results)


@app.route("/get-log-consultas-rne", methods=["GET"])
def get_log_consultas_rne():
    vendedor_id = request.args.get("vendedor_id")
    fecha = request.args.get("fecha")
    telefono = request.args.get("telefono")
    correo = request.args.get("correo")

    query = """
        SELECT lcr.id, u.nombres || ' ' || u.apellidos AS vendedor, lcr.consulta_tel, lcr.consulta_corr, lcr.fecha_consulta,
               lcr.tipo, lcr.sms, lcr.aplicacion, lcr.llamada, lcr.fecha_creacion_tel,
               lcr.aplicacion_corr, lcr.correo_corr, lcr.fecha_creacion_corr
        FROM log_consultas_rne lcr
        LEFT JOIN usuarios u ON lcr.vendedor_id = u.id
        WHERE 1=1
    """
    params = []

    if vendedor_id:
        query += " AND lcr.vendedor_id = %s"
        params.append(vendedor_id)

    if fecha:
        query += " AND DATE(lcr.fecha_consulta) = %s"
        params.append(fecha)

    if telefono:
        query += " AND lcr.consulta_tel ILIKE %s"
        params.append(f"%{telefono}%")

    if correo:
        query += " AND lcr.consulta_corr ILIKE %s"
        params.append(f"%{correo}%")

    query += " ORDER BY lcr.fecha_consulta DESC"

    cursor.execute(query, params)
    registros = cursor.fetchall()

    result = [
        {
            "id": r[0],
            "vendedor": r[1],
            "consulta_tel": r[2],
            "consulta_corr": r[3],
            "fecha_consulta": r[4],
            "tipo": r[5],
            "sms": r[6],
            "aplicacion": r[7],
            "llamada": r[8],
            "fecha_creacion_tel": r[9],
            "aplicacion_corr": r[10],
            "correo_corr": r[11],
            "fecha_creacion_corr": r[12],
        }
        for r in registros
    ]

    return jsonify(result)

@app.route('/exportar-log-consultas-rne', methods=['GET'])
def exportar_log_consultas_rne():
    vendedor_id = request.args.get("vendedor_id")
    fecha = request.args.get("fecha")
    telefono = request.args.get("telefono")
    correo = request.args.get("correo")

    query = """
        SELECT lcr.id, u.nombres || ' ' || u.apellidos AS vendedor, lcr.consulta_tel, lcr.consulta_corr, lcr.fecha_consulta,
               lcr.tipo, lcr.sms, lcr.aplicacion, lcr.llamada, lcr.fecha_creacion_tel,
               lcr.aplicacion_corr, lcr.correo_corr, lcr.fecha_creacion_corr
        FROM log_consultas_rne lcr
        LEFT JOIN usuarios u ON lcr.vendedor_id = u.id
        WHERE 1=1
    """
    params = []

    if vendedor_id:
        query += " AND lcr.vendedor_id = %s"
        params.append(vendedor_id)

    if fecha:
        query += " AND DATE(lcr.fecha_consulta) = %s"
        params.append(fecha)

    if telefono:
        query += " AND lcr.consulta_tel ILIKE %s"
        params.append(f"%{telefono}%")

    if correo:
        query += " AND lcr.consulta_corr ILIKE %s"
        params.append(f"%{correo}%")

    query += " ORDER BY lcr.fecha_consulta DESC"

    cursor.execute(query, params)
    registros = cursor.fetchall()

    # Encabezados del CSV
    headers = [
        "ID", "Vendedor", "Consulta Teléfono", "Consulta Correo", "Fecha Consulta",
        "Tipo", "SMS", "Aplicación", "Llamada", "Fecha Creación Tel",
        "Aplicación Correo", "Correo", "Fecha Creación Correo"
    ]

    # Crear contenido del CSV
    csv_content = ";".join(headers) + "\n"  # Encabezados separados por ";"

    for registro in registros:
        # Aseguramos que cada valor esté separado por ";"
        csv_content += ";".join([str(valor) if valor is not None else "" for valor in registro]) + "\n"

    # Retornar el archivo CSV al cliente
    response = make_response(csv_content)
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=resultados_consultas_realizadas_RNE.csv'
    return response

@app.route('/consultar-rne-expert', methods=['POST'])
def consultar_rne_expert():
    """
    Endpoint para consultar el RNE sin registrar los resultados en la base de datos.
    """
    data = request.json
    telefono = data.get('telefono')
    correo = data.get('correo')

    # Validación: Al menos uno de los campos debe estar presente
    if not telefono and not correo:
        return jsonify({"error": "Debe proporcionar un teléfono o un correo"}), 400

    # Configuración del servicio RNE
    url = "https://tramitescrcom.gov.co/excluidosback/consultaMasiva/validarExcluidos"
    token = os.getenv("CRC_TOKEN")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    def realizar_consulta(payload):
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error al realizar la consulta: {e}")
            return None

    results = {"telefono": None, "correo": None}

    # Consultar por teléfono
    if telefono:
        payload_tel = {"type": "TEL", "keys": [telefono]}
        data_tel = realizar_consulta(payload_tel)
        results["telefono"] = data_tel[0] if data_tel else None

    # Consultar por correo
    if correo:
        payload_correo = {"type": "COR", "keys": [correo]}
        data_correo = realizar_consulta(payload_correo)
        results["correo"] = data_correo[0] if data_correo else None

    # Devolver los resultados al cliente
    return jsonify(results)

# ENPOINTS para la nueva pagina de gerente

@app.route('/get-leads-concesionario', methods=['GET'])
def get_leads_concesionario():
    concesionario_id = request.args.get('concesionario_id')  # Filtro opcional por concesionario
    vendedor_id = request.args.get('vendedor_id')           # Filtro opcional por vendedor
    estado = request.args.get('estado')                    # Filtro opcional por estado
    test_drive = request.args.get('test_drive')            # Filtro opcional por test drive

    # Consulta base
    query = """
        SELECT l.id, l.nombres, l.apellidos, l.identificacion, l.telefono, l.direccion, l.ciudad, 
               l.correo, l.fecha_lead, l.origen_lead, l.marca_interes, l.modelo_interesado, 
               l.estatus, l.asignado, l.concesionario_id, l.test_drive, 
               u.nombres || ' ' || u.apellidos AS vendedor_nombre
        FROM leads l
        LEFT JOIN usuarios u ON l.asignado_a = u.id
        WHERE 1=1
    """
    params = []

    # Agregar filtro por concesionario si se proporciona
    if concesionario_id:
        query += " AND l.concesionario_id = %s"
        params.append(concesionario_id)

    # Agregar otros filtros opcionales
    if vendedor_id:
        query += " AND l.asignado_a = %s"
        params.append(vendedor_id)
    if estado:
        query += " AND l.estatus = %s"
        params.append(estado)
    if test_drive:
        query += " AND l.test_drive = %s"
        params.append(test_drive)

    try:
        # Ejecutar la consulta con los parámetros proporcionados
        cursor.execute(query, params)
        leads = cursor.fetchall()

        # Formatear los resultados
        leads_list = [
            {
                "id": lead[0],
                "nombres": lead[1],
                "apellidos": lead[2],
                "identificacion": lead[3],
                "telefono": lead[4],
                "direccion": lead[5],
                "ciudad": lead[6],
                "correo": lead[7],
                "fecha_lead": str(lead[8]),
                "origen_lead": lead[9],
                "marca_interes": lead[10],
                "modelo_interesado": lead[11],
                "estatus": lead[12],
                "asignado": lead[13],
                "concesionario_id": lead[14],
                "test_drive": lead[15],
                "vendedor_nombre": lead[16]
            }
            for lead in leads
        ]
        return jsonify(leads_list), 200
    except Exception as e:
        print(f"Error al obtener leads: {e}")
        return jsonify({"error": "Error al obtener leads"}), 500


@app.route('/get-leads-gerente', methods=['GET'])
def get_leads_gerente():
    try:
        query = """
            SELECT l.id, l.nombres, l.apellidos, l.identificacion, l.telefono, l.direccion, 
                   l.ciudad, l.correo, l.fecha_lead, l.origen_lead, l.marca_interes, 
                   l.modelo_interesado, l.estatus, l.asignado, l.concesionario_id, 
                   l.test_drive, l.seguimientos, l.asignado_a, 
                   u.nombres || ' ' || u.apellidos AS vendedor_nombre, 
                   l.precio_venta   -- ✅ incluimos el nuevo campo
            FROM leads l
            LEFT JOIN usuarios u ON l.asignado_a = u.id
            ORDER BY l.fecha_lead DESC
        """
        
        cursor.execute(query)
        leads = cursor.fetchall()

        # Formatear los resultados asegurando que "seguimientos" y "vendedor_id" no sean NULL
        leads_list = [
            {
                "id": lead[0],
                "nombres": lead[1],
                "apellidos": lead[2],
                "identificacion": lead[3],
                "telefono": lead[4],
                "direccion": lead[5],
                "ciudad": lead[6],
                "correo": lead[7],
                "fecha_lead": str(lead[8]),
                "origen_lead": lead[9],
                "marca_interes": lead[10],
                "modelo_interesado": lead[11],
                "estatus": lead[12],
                "asignado": lead[13],
                "concesionario_id": lead[14],
                "test_drive": lead[15],
                "seguimientos": lead[16] if lead[16] else "",  # Evita valores NULL
                "vendedor_id": lead[17] if lead[17] else None,  # Asegura que el vendedor se recupere correctamente
                "vendedor_nombre": lead[18],
                "precio_venta": float(lead[19]) if lead[19] is not None else 0  # ✅ nuevo campo en la respuesta
            }
            for lead in leads
        ]
        return jsonify(leads_list), 200

    except Exception as e:
        print(f"❌ Error al obtener leads para gerente: {e}")
        return jsonify({"error": "Error al obtener leads para gerente"}), 500



@app.route('/get-concesionarios-con-leads', methods=['GET'])
def get_concesionarios_con_leads():
    try:
        query = """
            SELECT DISTINCT c.id, c.nombre_concesionario, COUNT(l.id) AS total_leads
            FROM concesionarios c
            LEFT JOIN leads l ON c.id = l.concesionario_id
            GROUP BY c.id, c.nombre_concesionario
            ORDER BY c.nombre_concesionario
        """
        cursor.execute(query)
        concesionarios = cursor.fetchall()
        result = [
            {
                "id": row[0],
                "nombre_concesionario": row[1],
                "total_leads": row[2]
            }
            for row in concesionarios
        ]
        return jsonify(result), 200
    except Exception as e:
        print(f"Error al obtener concesionarios con leads: {e}")
        return jsonify({"error": "Error al obtener concesionarios"}), 500


@app.route('/auditoria', methods=['GET'])
def consultar_auditoria():
    usuario_id = request.args.get('usuario_id')  # Filtrar por usuario que realizó la acción
    tabla_afectada = request.args.get('tabla_afectada')  # Filtrar por tabla afectada
    accion = request.args.get('accion')  # Filtrar por tipo de acción
    fecha_desde = request.args.get('fecha_desde')  # Fecha de inicio del rango
    fecha_hasta = request.args.get('fecha_hasta')  # Fecha de fin del rango

    query = """
        SELECT id, fecha_hora, usuario_id, accion, tabla_afectada, registro_id, campo_modificado, 
               valor_anterior, valor_nuevo, comentarios
        FROM auditoria
        WHERE 1=1
    """
    params = []

    if usuario_id:
        query += " AND usuario_id = %s"
        params.append(usuario_id)
    if tabla_afectada:
        query += " AND tabla_afectada = %s"
        params.append(tabla_afectada)
    if accion:
        query += " AND accion = %s"
        params.append(accion)
    if fecha_desde:
        query += " AND fecha_hora >= %s"
        params.append(fecha_desde)
    if fecha_hasta:
        query += " AND fecha_hora <= %s"
        params.append(fecha_hasta)

    query += " ORDER BY fecha_hora DESC"

    cursor.execute(query, params)
    registros = cursor.fetchall()

    result = [
        {
            "id": r[0],
            "fecha_hora": r[1],
            "usuario_id": r[2],
            "accion": r[3],
            "tabla_afectada": r[4],
            "registro_id": r[5],
            "campo_modificado": r[6],
            "valor_anterior": r[7],
            "valor_nuevo": r[8],
            "comentarios": r[9],
        }
        for r in registros
    ]

    return jsonify(result), 200

@app.route('/auditoria', methods=['POST'])
def registrar_auditoria():
    data = request.get_json()

    query = """
        INSERT INTO auditoria (usuario_id, accion, tabla_afectada, registro_id, campo_modificado, valor_anterior, valor_nuevo, comentarios)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        data['usuario_id'], data['accion'], data['tabla_afectada'], data.get('registro_id'),
        data.get('campo_modificado'), data.get('valor_anterior'), data.get('valor_nuevo'),
        data.get('comentarios')
    )

    try:
        cursor.execute(query, values)
        conn.commit()
        return jsonify({"message": "Evento de auditoría registrado exitosamente"}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/get-logs', methods=['GET'])
def get_logs():
    try:
        # Configurar la zona horaria a 'America/Bogota' después de la conexión
        cursor.execute("SET timezone = 'America/Bogota';")

        cursor.execute("""
            SELECT a.id, 
                   to_char(a.fecha_hora, 'YYYY-MM-DD HH24:MI:SS') AS fecha_hora, -- Formato correcto
                   u.id AS usuario_id, 
                   u.nombres || ' ' || u.apellidos AS usuario, 
                   a.accion, 
                   a.campo_modificado, 
                   a.valor_anterior, 
                   a.valor_nuevo, 
                   a.comentarios
            FROM auditoria a
            LEFT JOIN usuarios u ON a.usuario_id = u.id
            ORDER BY a.fecha_hora DESC
        """)
        logs = cursor.fetchall()
        logs_dict = [dict(zip([desc[0] for desc in cursor.description], row)) for row in logs]

        # Obtener usuarios para los filtros
        cursor.execute("SELECT id, nombres || ' ' || apellidos AS name FROM usuarios")
        users = cursor.fetchall()

        return jsonify({
            "logs": logs_dict,
            "users": [{"id": user[0], "name": user[1]} for user in users]
        }), 200
    except Exception as e:
        print("Error al obtener los logs:", e)
        return jsonify({"error": "Error al obtener los logs"}), 500


# Ruta para agregar un lead de Test Drive
@app.route('/add-lead-test-drive', methods=['POST'])
def add_lead_test_drive():
    data = request.json
    print("🔍 Datos recibidos en el backend:", data)  # Ver los datos que llegan

    # Validación de Autorización de Datos
    if data.get('habeas_data') != 'Si':
        print("⚠️ Error: El usuario no aceptó la Autorización de Tratamiento de Datos y Habeas Data")
        return jsonify({"error": "Debe aceptar la Autorización de Tratamiento de Datos y Habeas Data"}), 400

    try:
        # Normalización de ciudad antes de insertar
        ciudad_db = "Bogota" if data.get('ciudad') == "Bogotá y Municipios Cercanos" else data.get('ciudad', None)
        print("🏙️ Ciudad normalizada para BD:", ciudad_db)

        # Obtener la fecha en UTC
        #fecha_aceptacion = datetime.utcnow()
        fecha_aceptacion = get_current_time_colombia()

        # Construcción de los valores para la base de datos
        lead_values = (
            data['nombres'],
            data['apellidos'],
            data.get('identificacion', None),
            data['telefono'],
            data.get('direccion', None),
            ciudad_db,  # Ciudad corregida
            data['correo'],
            get_current_time_colombia().date(),
            data.get('origen_lead', 'Canal digital'),
            data['marca_interes'],
            data['modelo_interesado'],
            data.get('estatus', 'nuevo'),
            data.get('asignado', False),
            data.get('test_drive', 'No'),
            data.get('precio_venta'),
            9999,  # Usuario genérico "Captura Digital" estandar
            data['habeas_data'],
            data.get('aceptacion_tratamiento_datos'),
            data.get('firma_digital', None),
            data.get('concesionario_id', None),
            fecha_aceptacion
        )

        print("📦 Valores a insertar en BD:", lead_values)  # Ver valores antes de insertar

        # Inserción en la base de datos
        lead_query = """
            INSERT INTO leads (nombres, apellidos, identificacion, telefono, direccion, ciudad, correo, fecha_lead,
                               origen_lead, marca_interes, modelo_interesado, estatus, asignado, test_drive, precio_venta,
                               capturado_por, habeas_data, aceptacion_tratamiento_datos, firma_digital, concesionario_id, fecha_aceptacion)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """
        cursor.execute(lead_query, lead_values)
        lead_id = cursor.fetchone()[0]
        print("✅ Lead insertado con ID:", lead_id)

        # Registro detallado en la auditoría
        comentarios_auditoria = (
            f"Lead Test Drive creado: nombres={data['nombres']}, apellidos={data['apellidos']}, "
            f"identificación={data.get('identificacion', 'N/A')}, celular={data['telefono']}, "
            f"ciudad={ciudad_db}, correo={data['correo']}, origen_lead={data.get('origen_lead', 'Canal digital')}, "
            f"marca_interes={data['marca_interes']}, modelo_interesado={data['modelo_interesado']}, test_drive={data.get('test_drive', 'No')}."
        )
        auditoria_query = """
            INSERT INTO auditoria (usuario_id, accion, tabla_afectada, registro_id, comentarios)
            VALUES (%s, %s, %s, %s, %s)
        """
        auditoria_values = (
            9999, 'Creación', 'leads', lead_id, comentarios_auditoria
        )
        cursor.execute(auditoria_query, auditoria_values)

        print("📜 Registro en auditoría completado.")

        # Verificar configuración para envío de correo
        cursor.execute("SELECT enviar_correo, destinatarios FROM configuracion_general")
        configuracion = cursor.fetchone()
        enviar_correo_flag, destinatarios = configuracion if configuracion else (False, None)

        if enviar_correo_flag and destinatarios:
            try:
                # Enviar correo con detalles del lead
                asunto = "Nuevo Lead de Test Drive Capturado"
                mensaje = f"""
                Cordial saludo Director equipo Retail,<br><br>
                Se ha capturado un nuevo lead a través del formulario de Test Drive. Detalles del lead almacenados en nuestra base de datos:<br>
                <ul>
                    <li><b>Nombres:</b> {data['nombres']}</li>
                    <li><b>Apellidos:</b> {data['apellidos']}</li>
                    <li><b>Identificación:</b> {data.get('identificacion', 'N/A')}</li>
                    <li><b>Celular:</b> {data['telefono']}</li>
                    <li><b>Ciudad:</b> {ciudad_db}</li>
                    <li><b>Correo:</b> {data['correo']}</li>
                    <li><b>Fecha del Lead:</b> {get_current_time_colombia().date()}</li>
                    <li><b>Origen del Lead:</b> {data.get('origen_lead', 'Canal digital')}</li>
                    <li><b>Marca:</b> {data['marca_interes']}</li>
                    <li><b>Modelo Interesado:</b> {data['modelo_interesado']}</li>
                    <li><b>Test Drive:</b> {data.get('test_drive', 'No')}</li>
                </ul>
                Este lead ha sido registrado correctamente en el sistema.<br><br>
                Cordialmente,<br>Sistema LeadsMass
                """
                enviar_correo(destinatario=destinatarios, asunto=asunto, mensaje=mensaje)

                # Registro en auditoría del correo enviado
                auditoria_query = """
                    INSERT INTO auditoria (usuario_id, accion, tabla_afectada, registro_id, comentarios)
                    VALUES (%s, %s, %s, %s, %s)
                """
                auditoria_values = (
                    9999, 'Correo Captura Lead Test Drive', 'leads', lead_id, "Correo enviado correctamente"
                )
                cursor.execute(auditoria_query, auditoria_values)
                print("📧 Correo enviado correctamente.")

            except Exception as e:
                print(f"❌ Error al enviar el correo: {e}")
                # Opcional: registrar en auditoría el fallo del correo
                auditoria_query = """
                    INSERT INTO auditoria (usuario_id, accion, tabla_afectada, registro_id, comentarios)
                    VALUES (%s, %s, %s, %s, %s)
                """
                auditoria_values = (
                    9999, 'Error Correo Lead Test Drive', 'leads', lead_id, f"Error al enviar correo: {str(e)}"
                )
                cursor.execute(auditoria_query, auditoria_values)


        # Confirmar transacción
        conn.commit()
        print("✅ Transacción confirmada en BD. Lead insertado con ID:", lead_id)

         # 🔥 Llamar al webhook después de confirmar la inserción
        enviar_webhook(data)

        return jsonify({"message": "Lead agregado exitosamente"}), 200

    except Exception as e:
        conn.rollback()
        print("❌ Error al guardar el lead:", str(e))
        return jsonify({"error": "Error al guardar el lead", "details": str(e)}), 500


# Publicar último lead en el webhook o webservice
# Publicar último lead en el webhook o webservice
@app.route('/get-last-lead', methods=['GET'])
def get_last_lead():
    """
    Obtiene el último lead capturado en la base de datos sin ciertos campos sensibles.
    """
    try:
        # Crear un cursor temporal en este scope
        with conn.cursor() as cursor:
            query = """
                SELECT nombres, apellidos, identificacion, telefono, direccion, ciudad, correo, fecha_lead, 
                       origen_lead, marca_interes, modelo_interesado, estatus, test_drive, 
                       capturado_por, habeas_data, aceptacion_tratamiento_datos, fecha_aceptacion, id
                FROM leads
                WHERE fecha_aceptacion IS NOT NULL
                ORDER BY fecha_aceptacion DESC
                LIMIT 1;
            """
            
            cursor.execute(query)
            lead = cursor.fetchone()

            if not lead:
                print("⚠️ No se encontraron leads en la base de datos.")
                return jsonify({"error": "No hay leads registrados aún."}), 404

            # Convertir el resultado en un diccionario para la respuesta JSON
            lead_dict = {
                "nombres": lead[0],
                "apellidos": lead[1],
                "identificacion": lead[2],
                "telefono": lead[3],
                "direccion": lead[4],
                "ciudad": lead[5],
                "correo": lead[6],
                "fecha_lead": str(lead[7]) if lead[7] else None,
                "origen_lead": lead[8],
                "marca_interes": lead[9],
                "modelo_interesado": lead[10],
                "estatus": lead[11],
                "test_drive": lead[12],
                "capturado_por": lead[13],
                "aceptacion_habeas_data": lead[14],
                "aceptacion_tratamiento_datos": lead[15],
                "fecha_aceptacion": str(lead[16]) if lead[16] else None,
                "id": lead[17]
            }

            return jsonify(lead_dict), 200

    except Exception as e:
        print(f"❌ Error al obtener el último lead: {str(e)}")
        return jsonify({"error": "Error al obtener el último lead", "details": str(e)}), 500



#if __name__ == '__main__':
#    port = int(os.environ.get("PORT", 5000))  # Usa el puerto de Railway o 5000 si no está definido
#    app.run(debug=True, host='0.0.0.0', port=port)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))  # Usa el puerto 8080 si no está definido
    print(f"Ejecutando en el puerto: {port}")
    app.run(debug=True, host='0.0.0.0', port=port)

