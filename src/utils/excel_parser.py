import pandas as pd
import os
import unicodedata

class ExcelParser:
    def __init__(self):
        self.column_mapping = {
            'codigo': ['codigo', 'cod', 'sku', 'ref', 'referencia', 'articulo', 'art', 'id'],
            'descripcion': ['descripcion', 'detalle', 'nombre', 'producto', 'item', 'desc'],
            'costo': ['costo', 'precio', 'precio_lista', 'unitario', 'valor', 'p.unit', 'importe'],
            'cantidad': ['cantidad', 'cant', 'unidades', 'stock', 'existencia']
        }

    def _normalizar_texto(self, texto):
        if not isinstance(texto, str):
            texto = str(texto)
        texto = texto.lower().strip()
        return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

    def leer_archivo(self, ruta_archivo):
        if not os.path.exists(ruta_archivo):
            return {"error": "El archivo no existe."}

        try:
            # 1. BÚSQUEDA DEL ENCABEZADO
            df_preview = pd.read_excel(ruta_archivo, header=None, nrows=10, dtype=str)
            fila_encabezado = -1
            mejor_coincidencia = 0
            
            for index, row in df_preview.iterrows():
                coincidencias = 0
                fila_texto = [self._normalizar_texto(str(val)) for val in row.values]
                for keywords in self.column_mapping.values():
                    if any(key in col for col in fila_texto for key in keywords):
                        coincidencias += 1
                if coincidencias > mejor_coincidencia:
                    mejor_coincidencia = coincidencias
                    fila_encabezado = index

            if fila_encabezado == -1:
                return {"error": "No encontré fila de encabezado."}

            # 2. LECTURA REAL
            df = pd.read_excel(ruta_archivo, header=fila_encabezado, dtype=str)
            df.columns = [self._normalizar_texto(col) for col in df.columns]
            mapa = self._identificar_columnas(df.columns)
            
            print(f"--- DEBUG ---")
            print(f"Encabezado en fila: {fila_encabezado}")
            print(f"Mapeo de columnas: {mapa}")

            if not mapa['codigo'] or not mapa['costo']:
                return {"error": "Faltan columnas clave (codigo/costo)."}

            datos_limpios = []
            
            print(f"--- ANALIZANDO FILAS ---")
            for index, row in df.iterrows():
                
                if index == 0:
                    print("\n--- ¿QUÉ HAY EN LA PRIMERA FILA? ---")
                    # Esto imprimirá TODA la fila para que veamos dónde cayó el dato
                    print(row) 
                    print("------------------------------------\n")
                # Extracción
                raw_cod = row[mapa['codigo']] if mapa['codigo'] else None
                raw_desc = row[mapa['descripcion']] if mapa['descripcion'] else "Sin nombre"
                raw_costo = row[mapa['costo']] if mapa['costo'] else "0"
                
                # Limpieza
                codigo = str(raw_cod).strip()
                desc = str(raw_desc).strip()
                
                # Limpieza de costo
                str_costo = str(raw_costo).replace('$', '').replace('usd', '').strip().replace(',', '.')
                try:
                    costo = float(str_costo)
                except ValueError:
                    costo = 0.0

                item = {
                    "codigo": codigo,
                    "descripcion": desc,
                    "costo": costo,
                    "cantidad": 0
                }
                
                # DIAGNÓSTICO: Si es la primera fila, imprimimos qué ve
                if index == 0:
                    print(f"Fila 1 cruda -> Código: '{raw_cod}', Costo: '{raw_costo}'")
                    print(f"Fila 1 procesada -> Código: '{codigo}', Costo: {costo}")

                # Filtro: Aceptamos si tiene código Y (costo > 0 O precio es válido)
                # si el codigo no es 'nan' lo aceptamos, aunque el costo sea 0 (para ver si ese es el error)
                if codigo and codigo.lower() != "nan":
                    datos_limpios.append(item)
                else:
                    print(f"Fila {index} ignorada: Código inválido ('{codigo}')")

            return {"status": "ok", "data": datos_limpios}

        except Exception as e:
            return {"error": f"Error crítico: {str(e)}"}

    def _identificar_columnas(self, columnas_excel):
        mapa = {'codigo': None, 'descripcion': None, 'costo': None, 'cantidad': None}
        for col_real in columnas_excel:
            for clave_interna, posibles_nombres in self.column_mapping.items():
                if any(nombre == col_real or nombre in col_real for nombre in posibles_nombres):
                    if mapa[clave_interna] is None:
                        mapa[clave_interna] = col_real
        return mapa

# --- BLOQUE DE PRUEBA ---
if __name__ == "__main__":
    parser = ExcelParser()
    ruta = r"C:\Users\Nicolas\Desktop\comercio-facil\src\Book.xlsx"
    
    resultado = parser.leer_archivo(ruta)
    
    if "error" in resultado:
        print("❌ ERROR:", resultado['error'])
    else:
        cant = len(resultado['data'])
        print(f"✅ ÉXITO! Se leyeron {cant} productos.")
        if cant > 0:
            print("Ejemplo del primer producto:", resultado['data'][0])
        else:
            print("⚠️ La lista está vacía. Revisa los mensajes de DEBUG arriba.")