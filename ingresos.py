from flask import Flask, request, render_template, redirect, url_for, flash
import datetime
import json
import os

app = Flask(__name__)
app.secret_key = "PASSWORD"  # Needed for flashing messages

# Nombres predefinidos
nombres = ["Sebastián", "Bruno"]

# Archivo para guardar los registros
archivo_registros = "registros.json"

# Leer registros desde el archivo si existe
if os.path.exists(archivo_registros):
    with open(archivo_registros, "r") as archivo:
        registros = json.load(archivo)
else:
    registros = []

# Contraseña predefinida
password = str("PASSWORD")


def registrar_entrada_salida(nombre, accion):
    tiempo_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    registro = {"nombre": nombre, "accion": accion, "tiempo": tiempo_actual}
    registros.append(registro)
    with open(archivo_registros, "w") as archivo:
        json.dump(registros, archivo, indent=4)
    flash(f"{nombre} ha {accion} el laboratorio a las {tiempo_actual}")


@app.route("/")
def index():
    return render_template("home.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        nombre = request.form["nombre"]
        accion = request.form["accion"]
        input_password = str(request.form["password"])

        if input_password == password:
            registrar_entrada_salida(nombre, accion)
            return redirect(url_for("index"))
        else:
            flash("Contraseña incorrecta. Intente nuevamente.")
            return redirect(url_for("login"))
    return render_template("login.html", nombres=nombres)


@app.route("/records", methods=["GET", "POST"])
def records():
    if request.method == "POST":
        input_password = request.form["password"]

        if input_password == password:
            return render_template("records.html", registros=registros)
        else:
            flash("Contraseña incorrecta. Intente nuevamente.")
            return redirect(url_for("records"))
    return render_template("records_login.html")


if __name__ == "__main__":
    app.run(host="HOST_IP", port=5000, debug=True)
