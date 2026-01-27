# src/utils/excel_parser.py
import pandas as pd
import os

class ExcelParser:
    def __init__(self):
        # Diccionario de sinónimos para detectar columnas automáticamente
        # Clave: Nombre interno que usa nuestra DB
        # Valor: Lista de posibles nombres que usa el proveedor
        self.column_mapping = {
            'codigo': ['codigo', 'cod', 'sku', 'ref', 'referencia', 'articulo', 'art'],
            'descripcion': ['descripcion', 'detalle', 'nombre', 'producto', 'item'],
            'costo': ['costo', 'precio', 'precio_lista', 'unitario', 'valor', 'p.unit'],
            'cantidad': ['cantidad', 'cant', 'unidades', 'stock']
        }

    def leer_archivo(self, ruta_archivo):
        """
        Lee un Excel y devuelve una lista de diccionarios estandarizados.
        """
        if not os.path.exists(ruta_archivo):
            return {"error": "El archivo no existe."}

        try:
            # Leemos el Excel. 'dtype=str' fuerza a leer todo como texto para no perder ceros a la izquierda en códigos
            df = pd.read_excel(ruta_archivo, dtype=str)
            
            # Limpiamos los nombres de las columnas (todo a minúsculas y sin espacios extra)
            df.columns = [str(col).lower().strip() for col in df.columns]
            
            # Identificamos qué columna es cual
            mapa_actual = self._identificar_columnas(df.columns)
            
            if not mapa_actual['codigo'] or not mapa_actual['costo']:
                return {"error": "No pude identificar las columnas de 'Código' o 'Costo' automáticamente. Revisa el Excel."}

            datos_limpios = []
            
            # Recorremos el Excel fila por fila
            for index, row in df.iterrows():
                # Extraemos los datos usando el mapa identificado
                codigo = row[mapa_actual['codigo']] if mapa_actual['codigo'] else f"SIN-COD-{index}"
                desc = row[mapa_actual['descripcion']] if mapa_actual['descripcion'] else "Sin descripción"
                
                # Limpieza de precio (reemplazar comas por puntos, quitar signos $)
                raw_costo = str(row[mapa_actual['costo']]).replace('$', '').replace(',', '.')
                try:
                    costo = float(raw_costo)
                except ValueError:
                    costo = 0.0

                item = {
                    "codigo": str(codigo).strip(),
                    "descripcion": str(desc).strip(),
                    "costo": costo,
                    "cantidad": 0  # Por defecto 0, el usuario pondrá cuánto le llegó
                }
                
                # Filtramos filas vacías
                if item["codigo"] and item["codigo"] != "nan":
                    datos_limpios.append(item)
                    
            return {"status": "ok", "data": datos_limpios}

        except Exception as e:
            return {"error": f"Error leyendo el archivo: {str(e)}"}

    def _identificar_columnas(self, columnas_excel):
        """
        Intenta adivinar qué columna del Excel corresponde a nuestros datos
        """
        mapa = {'codigo': None, 'descripcion': None, 'costo': None, 'cantidad': None}
        
        for col_real in columnas_excel:
            for clave_interna, posibles_nombres in self.column_mapping.items():
                if any(nombre in col_real for nombre in posibles_nombres):
                    # Si aún no asignamos esa columna, la asignamos ahora
                    if mapa[clave_interna] is None:
                        mapa[clave_interna] = col_real
        
        return mapa

# --- BLOQUE DE PRUEBA  ---
if __name__ == "__main__":
   
     parser = ExcelParser()
     ruta = r"C:/Users/Nicolas/Desktop/comercio-facil/src/Book.xlsx" 
     resultado = parser.leer_archivo(ruta)
     print(resultado)