import sqlite3

# Funci�n para crear las tablas si no existen
def create_tables():
    conn = sqlite3.connect('historial.db')
    cursor = conn.cursor()

    # Crear tabla para el historial del jugador
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historial_player (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            carta1 INTEGER,
            carta2 INTEGER,
            total INTEGER,
            resultado TEXT
        )
    ''')

    # Crear tabla para el historial del dealer
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historial_dealer (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            carta_dealer INTEGER,
            total_dealer INTEGER,
            resultado_dealer TEXT
        )
    ''')

    conn.commit()
    conn.close()

# Funci�n para insertar el historial del jugador
def insert_player_history(carta1, carta2, total, resultado):
    conn = sqlite3.connect('historial.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO historial_player (carta1, carta2, total, resultado)
        VALUES (?, ?, ?, ?)
    ''', (carta1, carta2, total, resultado))

    conn.commit()
    conn.close()

# Funci�n para insertar el historial del dealer
def insert_dealer_history(carta_dealer, total_dealer, resultado_dealer):
    conn = sqlite3.connect('historial.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO historial_dealer (carta_dealer, total_dealer, resultado_dealer)
        VALUES (?, ?, ?)
    ''', (carta_dealer, total_dealer, resultado_dealer))

    conn.commit()
    conn.close()

# Funci�n para obtener todas las cartas disponibles
def get_all_cards():
    return [
        (1, 'A'), (2, '2'), (3, '3'), (4, '4'), (5, '5'), (6, '6'), (7, '7'), (8, '8'), (9, '9'), (10, '10'),
        (10, 'J'), (10, 'Q'), (10, 'K')
    ]
