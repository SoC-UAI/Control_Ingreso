from flask import Flask, render_template, request, redirect, url_for
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import logging

app = Flask(__name__)

# Configuración de la conexión con Google Sheets
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
creds = ServiceAccountCredentials.from_json_keyfile_name(
    "control-acceso-security-lab-1137638840bd.json", scope
)
client = gspread.authorize(creds)
sheet = client.open("Control de Acesso Security Lab UAI").sheet1


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/entrada", methods=["GET", "POST"])
def entrada():
    if request.method == "POST":
        nombre = request.form["nombre"]
        correo = request.form["correo"]
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        sheet.append_row(
            [timestamp, nombre, correo, "Entrada"], value_input_option="RAW"
        )
        return redirect(url_for("index"))
    return render_template("entrada.html")


@app.route("/salida", methods=["GET", "POST"])
def salida():
    if request.method == "POST":
        nombre = request.form["nombre"]
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        sheet.append_row([timestamp, nombre, "", "Salida"], value_input_option="RAW")
        return redirect(url_for("index"))

    registros = sheet.get_all_records()

    # Diccionario para almacenar la última acción de cada persona
    estados_personas = {}
    for registro in registros:
        if len(registro) >= 4:  # Asegurarse de que hay al menos 4 columnas
            timestamp_str = registro.get(
                "Marca temporal", ""
            ).strip()  # Marca de tiempo en la columna A
            nombre = registro.get(
                "Nombre completo", ""
            ).strip()  # Nombre completo en la columna B
            accion = (
                registro.get("Acción", "").strip().lower()
            )  # Acción en la columna D

            if not timestamp_str or not nombre or not accion:
                logging.warning(f"Registro inválido o incompleto: {registro}")
                continue

            try:
                timestamp = datetime.strptime(timestamp_str, "%d/%m/%Y %H:%M:%S")
            except ValueError as e:
                logging.error(
                    f"Formato de tiempo inválido: {timestamp_str}, error: {e}"
                )
                continue

            # Actualizar el estado de la persona solo si es el último registro
            if (
                nombre not in estados_personas
                or estados_personas[nombre]["timestamp"] < timestamp
            ):
                estados_personas[nombre] = {"timestamp": timestamp, "accion": accion}

    # Lista de personas dentro del laboratorio
    nombres_en_lab = set()

    for nombre, info in estados_personas.items():
        if info["accion"] == "entrada":
            nombres_en_lab.add(nombre)
        elif info["accion"] == "salida":
            nombres_en_lab.discard(nombre)

    return render_template("salida.html", nombres=nombres_en_lab)


if __name__ == "__main__":
    app.run(debug=True)
