import sqlite3
import os

def create_tables():
    db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'historial.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Verificar si las tablas ya existen antes de intentar crearlas
    cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="historial_player"')
    player_table_exists = cursor.fetchone()

    cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="historial_dealer"')
    dealer_table_exists = cursor.fetchone()

    cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="cartas"')
    cartas_table_exists = cursor.fetchone()

    if not player_table_exists:
        cursor.execute('''
            CREATE TABLE historial_player (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                carta1 TEXT NOT NULL,
                carta2 TEXT NOT NULL
            )
        ''')

    if not dealer_table_exists:
        cursor.execute('''
            CREATE TABLE historial_dealer (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                carta1 TEXT NOT NULL
            )
        ''')

    if not cartas_table_exists:
        cursor.execute('''
            CREATE TABLE cartas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL
            )
        ''')

        # Insertar las cartas si no existen
        cartas = [
            "As (1 u 11)", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"
        ]

        for carta in cartas:
            cursor.execute('INSERT OR IGNORE INTO cartas (nombre) VALUES (?)', (carta,))

    conn.commit()
    conn.close()

def insert_player_history(carta1, carta2):
    db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'historial.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Insertar historial del jugador si no existe
    cursor.execute('INSERT OR IGNORE INTO historial_player (carta1, carta2) VALUES (?, ?)', (carta1, carta2))
    conn.commit()

    conn.close()

def insert_dealer_history(carta1):
    db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'historial.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Insertar historial del dealer si no existe
    cursor.execute('INSERT OR IGNORE INTO historial_dealer (carta1) VALUES (?)', (carta1,))
    conn.commit()

    conn.close()

def get_all_cards():
    db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'historial.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM cartas')
    cartas = cursor.fetchall()

    conn.close()

    return cartas
