from flask import Flask, render_template, jsonify
import qrcode
from io import BytesIO
import io
from PIL import Image
import base64
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import datetime
import threading
import time

app = Flask(__name__)

# Configuración de la API de Google Sheets
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
SPREADSHEET_ID = "1ehbF7VtwdYyA57CSRqbRQUzYQrtQ6tckkX0-P0vGzHE"
RANGE_NAME = "A2:D"  # Ajusta esto según la estructura de tu hoja de cálculo

# Ruta del archivo de credenciales
CREDENTIALS_FILE = "control-acceso-security-lab-1137638840bd.json"

# Lista global de estudiantes dentro
estudiantes_dentro = []


def obtener_datos_hoja():
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    service = build("sheets", "v4", credentials=creds)
    sheet = service.spreadsheets()
    result = (
        sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    )
    values = result.get("values", [])

    # Diccionario para almacenar la última acción de cada estudiante
    estados_estudiantes = {}
    for fila in values:
        if len(fila) >= 4:  # Asegurarse de que hay al menos 4 columnas
            timestamp_str = fila[0].strip()  # Marca de tiempo en la columna A
            nombre = fila[1].strip()  # Nombre completo en la columna B
            accion = fila[3].strip().lower()  # Acción en la columna D

            # Convertir la marca de tiempo a un objeto datetime para comparación
            timestamp = datetime.datetime.strptime(timestamp_str, "%d/%m/%Y %H:%M:%S")

            # Actualizar el estado del estudiante solo si es el último registro
            if (
                nombre not in estados_estudiantes
                or estados_estudiantes[nombre]["timestamp"] < timestamp
            ):
                estados_estudiantes[nombre] = {"timestamp": timestamp, "accion": accion}

    # Actualizar la lista global de estudiantes dentro
    global estudiantes_dentro
    nuevos_estudiantes_dentro = set()

    for nombre, info in estados_estudiantes.items():
        # print(f"{nombre}: {info['accion']}")
        if info["accion"] == "entrada":
            nuevos_estudiantes_dentro.add(nombre)
            # print(f"Estudiante {nombre} entró")
        elif info["accion"] == "salida":
            nuevos_estudiantes_dentro.discard(nombre)
            # print(f"Estudiante {nombre} salió")

    # print(f"Estudiantes dentro: {nuevos_estudiantes_dentro}")
    estudiantes_dentro = list(nuevos_estudiantes_dentro)
    print(f"Estudiantes dentro actualizados: {estudiantes_dentro}")  # Agregar registro


def actualizar_estudiantes():
    while True:
        obtener_datos_hoja()
        time.sleep(10)


def generar_codigo_qr(qr_url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_url)
    qr.make(fit=True)

    img = qr.make_image(fill="black", back_color="white")

    # Save the image to a BytesIO buffer
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    buffered.seek(0)

    # Convert to base64
    img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return img_base64


@app.route("/")
def index():
    global estudiantes_dentro

    qr_url = "https://sebadinator.pythonanywhere.com/"
    qr_code = generar_codigo_qr(qr_url)

    return render_template(
        "index.html", estudiantes=estudiantes_dentro, qr_code=qr_code
    )


@app.route("/estudiantes")
def estudiantes():
    global estudiantes_dentro
    return jsonify(estudiantes=estudiantes_dentro)


if __name__ == "__main__":
    # Iniciar el hilo de actualización
    threading.Thread(target=actualizar_estudiantes, daemon=True).start()
    app.run(host="0.0.0.0", port=5001, debug=False)
