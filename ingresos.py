# Python 3.11.2
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
import schedule
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# API configuration for Google Sheets
SCOPES = [os.getenv("SCOPES")]
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
RANGE_NAME = os.getenv("RANGE_NAME")
CREDENTIALS_FILE = os.getenv("CREDENTIALS_FILE")

# Global list to store the students inside
estudiantes_dentro = []

# Agregar la lista de tutores
tutores = ["Ignacio Soto", "Bruno Reyes"]

# Function to get the data from the Google Sheet
def obtener_datos_hoja():
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    service = build("sheets", "v4", credentials=creds)
    sheet = service.spreadsheets()
    result = (
        sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    )
    values = result.get("values", [])

    # Dictionary to store the latest state of each student
    estados_estudiantes = {}
    for fila in values: # These rows are specific to the Google Sheet used in this case - Modify as needed
        if len(fila) >= 4:  # Make sure the row has at least 4 columns
            timestamp_str = fila[0].strip()  # Timestamp in column A
            nombre = fila[1].strip()  # Full name in column B
            accion = fila[3].strip().lower()  # Action in column D

            # Transform the timestamp string to a datetime object
            timestamp = datetime.datetime.strptime(timestamp_str, "%d/%m/%Y %H:%M:%S")

            # Update the student's state if the current action is more recent
            if (
                nombre not in estados_estudiantes
                or estados_estudiantes[nombre]["timestamp"] < timestamp
            ):
                estados_estudiantes[nombre] = {"timestamp": timestamp, "accion": accion}

    # Update the global list of students inside
    global estudiantes_dentro
    nuevos_estudiantes_dentro = set()

    for nombre, info in estados_estudiantes.items():
        if info["accion"] == "entrada":
            nuevos_estudiantes_dentro.add(nombre) # Add the student to the set
        elif info["accion"] == "salida":
            nuevos_estudiantes_dentro.discard(nombre) # Remove the student from the set

    estudiantes_dentro = list(nuevos_estudiantes_dentro)
    print(f"Estudiantes dentro actualizados: {estudiantes_dentro}") # Print the updated list of students inside to the console for debugging purposes


# Function to update the list of students inside every 10 seconds
def actualizar_estudiantes():
    while True:
        obtener_datos_hoja()
        time.sleep(10)

# Function to generate a QR code to display on the web page
def generar_codigo_qr(qr_url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10, # Change the box size to adjust the size of the QR code as needed
        border=4,
    )
    qr.add_data(qr_url)
    qr.make(fit=True)

    img = qr.make_image(fill="black", back_color="white") # Change the fill and back_color to adjust the colors of the QR code as needed

    # Save the image to a BytesIO buffer
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    buffered.seek(0)

    # Convert to base64
    img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return img_base64

# Function to log out all students at 20:00 every day - NOT WORKING YET!
def logout_all_students():
    """Automatically log out all students at 20:00 every day."""
    global estudiantes_dentro

    # Mark all students as "Salida" (logout) in the Google Sheet
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    service = build("sheets", "v4", credentials=creds)
    sheet = service.spreadsheets()

    now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    for nombre in estudiantes_dentro:
        # Create the new row data for "Salida"
        new_row = [[now, nombre, "", "Salida"]]

        # Append the new row to the Google Sheet
        sheet.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME,
            valueInputOption="USER_ENTERED",
            body={"values": new_row},
        ).execute()

    # Clear the list to log out all students locally
    estudiantes_dentro.clear()
    print("Todos los estudiantes han sido desconectados automáticamente a las 20:00.")

# Function to schedule the daily logout task
def schedule_tasks():
    """Schedule the daily logout task."""
    schedule.every().day.at("20:00").do(logout_all_students)

    while True:
        schedule.run_pending()
        time.sleep(1)


# Principal route to display the list of students inside and the QR code
@app.route("/")
def index():
    global estudiantes_dentro

    qr_url = "https://socuai.pythonanywhere.com/"
    qr_code = generar_codigo_qr(qr_url)

    return render_template(
        "index.html",
        estudiantes=estudiantes_dentro,
        qr_code=qr_code,
        tutores=tutores  # Pasar la lista de tutores al template
    )


@app.route("/estudiantes")
def estudiantes():
    global estudiantes_dentro
    return jsonify(estudiantes=estudiantes_dentro)


if __name__ == "__main__":
    # Initialize the threads to update the list of students inside and schedule the daily logout task
    threading.Thread(target=actualizar_estudiantes, daemon=True).start()
    threading.Thread(target=schedule_tasks, daemon=True).start()
    app.run(host="0.0.0.0", port=5001, debug=False) # Change the port as needed
