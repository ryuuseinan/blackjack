from flask import Flask, render_template, request, redirect, url_for
import os, pickle
import random

def get_all_cards():
    return [
        (1, 'A'), (2, '2'), (3, '3'), (4, '4'), (5, '5'), (6, '6'), (7, '7'), (8, '8'), (9, '9'), (10, '10'),
        (10, 'J'), (10, 'Q'), (10, 'K')
    ]

historial_player = []
historial_dealer = []
modelo = None

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
def determinar_ganador(puntuacion_player, puntuacion_dealer, carta_siguiente):
    print("carta_siguiente:", carta_siguiente)
    print("puntuacion_player:", puntuacion_player)
    print("puntuacion_dealer:", puntuacion_dealer)
    puntuacion_player = puntuacion_player + carta_siguiente[0]
    puntuacion_dealer = puntuacion_dealer + carta_siguiente[0]
    if puntuacion_player == 21:
        return "Player"
    elif puntuacion_dealer == 21:
        return "Dealer"
    else:
        return "Empate"

# Función para adivinar la siguiente carta del mazo
def adivinar_carta_siguiente():
    mazo = get_all_cards()
    return random.choice(mazo)

# Cargar el modelo entrenado al inicio de la aplicación
with open('modelo_entrenado.pkl', 'rb') as file:
    modelo = pickle.load(file)

# Function to predict probability
def predecir_probabilidad(cartas_player, cartas_dealer, carta_siguiente):
    features_player = [carta[1] for carta in cartas_player]
    features_dealer = [carta[1] for carta in cartas_dealer]
    features = [(0, carta) for carta in features_player + features_dealer] + [(0, carta_siguiente)]
    probabilidad = modelo.predict_proba([features])[0]
    return probabilidad

# Function to insert player history
# Function to insert player history
def insert_player_history(first_player_card, second_player_card, puntuacion_player, carta_siguiente, ganador):
    puntuacion_total = puntuacion_player + carta_siguiente[0]
    historial_player.append((len(historial_player) + 1, first_player_card, second_player_card, puntuacion_total, ganador))

# Function to insert dealer history
def insert_dealer_history(dealer_card, puntuacion_dealer, carta_siguiente, ganador):
    puntuacion_total = puntuacion_dealer + carta_siguiente[0]
    historial_dealer.append((len(historial_dealer) + 1, dealer_card, puntuacion_total, ganador))


# Definir una ruta para la página principal
@app.route('/')
def index():
    cartas = get_all_cards()
    modelo_str = str(modelo)

    return render_template('index.html', modelo_str=modelo_str, historial_player=historial_player, historial_dealer=historial_dealer, cartas=cartas)

# Definir una función que haga una predicción
def hacer_predicción(datos):
    # Hacer una predicción utilizando el modelo KNN
    prediccion = modelo.predict(datos)
    return prediccion

# Definir una ruta para la predicción
@app.route('/predict', methods=['POST'])
def predict():
    first_player_card = request.form['firstplayercard']
    second_player_card = request.form['secondplayercard']
    dealer_card = request.form['dealer_card']

    cartas_player = [first_player_card, second_player_card]
    cartas_dealer = [dealer_card]

    puntuacion_player = calcular_puntuacion(cartas_player)
    puntuacion_dealer = calcular_puntuacion(cartas_dealer)

    carta_siguiente = adivinar_carta_siguiente()

    ganador = determinar_ganador(puntuacion_player, puntuacion_dealer, carta_siguiente)

    insert_player_history(first_player_card, second_player_card, puntuacion_player, carta_siguiente, ganador)

    insert_dealer_history(dealer_card, puntuacion_dealer, carta_siguiente, ganador)


    cartas = get_all_cards()

    return render_template('index.html', historial_player=historial_player, historial_dealer=historial_dealer, cartas=cartas,
                           puntuacion_player=puntuacion_player, puntuacion_dealer=puntuacion_dealer,
                           carta_siguiente=carta_siguiente, ganador=ganador)

@app.route('/suggestions', methods=['POST'])
def suggestions():
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
