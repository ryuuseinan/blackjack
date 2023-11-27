# app.py

from flask import Flask, render_template, request, redirect, url_for
from db import create_tables, insert_player_history, insert_dealer_history, get_all_cards
import os, pickle
import sqlite3
import random 

app = Flask(__name__)
# Función para calcular la puntuación de una mano de cartas
def calcular_puntuacion(cartas):
    puntuacion = 0
    ases = 0  # Contador de ases para manejar el valor 1 u 11

    for carta in cartas:
        if carta.isdigit() or carta == '10':
            puntuacion += int(carta)
        elif carta != 'A':
            puntuacion += 10
        else:
            ases += 1

    # Manejar los ases
    for _ in range(ases):
        if puntuacion + 11 <= 21:
            puntuacion += 11
        else:
            puntuacion += 1

    return puntuacion

# Función para determinar el ganador del juego
def determinar_ganador(puntuacion_player, puntuacion_dealer):
    if puntuacion_player > 21:
        return "Dealer"
    elif puntuacion_dealer > 21:
        return "Player"
    elif puntuacion_player > puntuacion_dealer:
        return "Player"
    elif puntuacion_dealer > puntuacion_player:
        return "Dealer"
    else:
        return "Empate"

# Función para adivinar la siguiente carta del mazo
def adivinar_carta_siguiente():
    mazo = get_all_cards()
    return random.choice(mazo)

# Crear tablas si no existen
create_tables()

# Cargar el modelo entrenado al inicio de la aplicación
with open('modelo_entrenado.pkl', 'rb') as file:
    modelo = pickle.load(file)

def predecir_probabilidad(cartas_player, cartas_dealer, carta_siguiente):
    # Extraer solo los nombres de las cartas (segundo elemento de cada tupla)
    features_player = [carta[1] for carta in cartas_player]
    features_dealer = [carta[1] for carta in cartas_dealer]

    # Combinar las características del jugador, del dealer y la siguiente carta
    features = [(0, carta) for carta in features_player + features_dealer] + [(0, carta_siguiente)]

    # Hacer una predicción utilizando el modelo
    probabilidad = modelo.predict_proba([features])[0]
    return probabilidad

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

    # Crear listas de cartas para el jugador y el dealer
    cartas_player = [first_player_card, second_player_card]
    cartas_dealer = [dealer_card]

    # Calcular puntuaciones
    puntuacion_player = calcular_puntuacion(cartas_player)
    puntuacion_dealer = calcular_puntuacion(cartas_dealer)

    # Adivinar la siguiente carta del mazo
    carta_siguiente = adivinar_carta_siguiente()

    # Determinar el ganador
    ganador = determinar_ganador(puntuacion_player, puntuacion_dealer)

    # Registrar el historial del jugador en la base de datos
    insert_player_history(first_player_card, second_player_card, puntuacion_player, ganador)

    # Registrar el historial del dealer en la base de datos
    insert_dealer_history(dealer_card, puntuacion_dealer, ganador)

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

    # Redirigir de vuelta al index con información adicional
    return render_template('index.html', historial_player=historial_player, historial_dealer=historial_dealer, cartas=cartas,
                           puntuacion_player=puntuacion_player, puntuacion_dealer=puntuacion_dealer,
                           carta_siguiente=carta_siguiente, ganador=ganador)

@app.route('/suggestions', methods=['POST'])
def suggestions():
    # ... (otro código)

    first_player_card = request.form['firstplayercard']
    second_player_card = request.form['secondplayercard']
    dealer_card = request.form['dealer_card']

    cartas_player = [first_player_card, second_player_card]

    # Agregar impresiones para verificar el contenido
    print("cartas_player:", cartas_player)

    cartas_dealer = [dealer_card]

    carta_siguiente = adivinar_carta_siguiente()

    # Agregar impresiones para verificar el contenido
    print("cartas_dealer:", cartas_dealer)
    print("carta_siguiente:", carta_siguiente)

    probabilidad = predecir_probabilidad(cartas_player, cartas_dealer, carta_siguiente)

    sugerencias = {
        'plantarse': probabilidad[0],
        'pedir_otra_carta': probabilidad[1],
        'duplicar': probabilidad[2]
    }
    
    puntuacion_player = calcular_puntuacion(cartas_player)
    puntuacion_dealer = calcular_puntuacion(cartas_dealer)

    return render_template('suggestions.html', sugerencias=sugerencias,
                           puntuacion_player=puntuacion_player, puntuacion_dealer=puntuacion_dealer)

# Ejecutar la aplicación Flask
if __name__ == '__main__':
    app.run(debug=True)
