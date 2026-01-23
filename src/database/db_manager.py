# src/database/db_manager.py
import sqlite3
import os
from datetime import datetime

DB_NAME = 'negocio.db'

def conectar():
    return sqlite3.connect(DB_NAME)

def inicializar_db():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_barras TEXT UNIQUE,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            categoria TEXT,
            ruta_imagen TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_producto INTEGER,
            cantidad REAL DEFAULT 0,
            costo_unitario REAL DEFAULT 0,
            precio_venta REAL DEFAULT 0,
            margen_aplicado REAL DEFAULT 140.0,
            ultima_actualizacion DATETIME,
            FOREIGN KEY (id_producto) REFERENCES productos (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Base de datos '{DB_NAME}' verificada/inicializada.")