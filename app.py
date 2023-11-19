# app.py

from flask import Flask, render_template, request, redirect, url_for
from db import create_tables, insert_player_history, insert_dealer_history, get_all_cards
import os, pickle
import sqlite3

app = Flask(__name__)

# Crear tablas si no existen
create_tables()

# Cargar el modelo entrenado al inicio de la aplicación
with open('modelo_entrenado.pkl', 'rb') as file:
    modelo = pickle.load(file)

# Definir una ruta para la página principal
@app.route('/')
def index():
    # Conectar a la base de datos
    conn = sqlite3.connect('historial.db')
    cursor = conn.cursor()

    # Obtener historial del player
    cursor.execute('SELECT * FROM historial_player')
    historial_player = cursor.fetchall()

    # Obtener historial del dealer
    cursor.execute('SELECT * FROM historial_dealer')
    historial_dealer = cursor.fetchall()

    # Obtener cartas
    cartas = get_all_cards()

    # Cerrar la conexión a la base de datos
    conn.close()

    return render_template('index.html', historial_player=historial_player, historial_dealer=historial_dealer, cartas=cartas)

# Definir una función que haga una predicción
def hacer_predicción(datos):
    # Hacer una predicción utilizando el modelo KNN
    prediccion = modelo.predict(datos)
    return prediccion

# Definir una ruta para la predicción
@app.route('/predict', methods=['POST'])
def predict():
    # Obtener los datos de la solicitud
    first_player_card = request.form['firstplayercard']
    second_player_card = request.form['secondplayercard']
    dealer_card = request.form['dealer_card']

    # Registrar el historial del jugador en la base de datos
    insert_player_history(first_player_card, second_player_card)

    # Registrar el historial del dealer en la base de datos
    insert_dealer_history(dealer_card)

    # Redirigir de vuelta al index
    return redirect(url_for('index'))

# Ejecutar la aplicación Flask
if __name__ == '__main__':
    app.run(debug=True)
