# src/main.py
import sys
import os

# Ajustamos el path para que Python encuentre nuestros módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import inicializar_db

def main():
    print("Iniciando Comercio Fácil...")
    # 1. Chequeo de base de datos
    inicializar_db()
    
    print("Sistema listo. Esperando interfaz gráfica...")

if __name__ == "__main__":
    main()