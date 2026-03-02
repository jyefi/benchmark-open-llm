import pandas as pd
from pathlib import Path

# --- CONFIGURACIÓN ---
# Cambia esta ruta a la carpeta donde están tus archivos
DIRECTORIO_REQUISITOS = Path("./salida_estudio")
ARCHIVO_SALIDA = DIRECTORIO_REQUISITOS / "consolidado_final_requisitos.xlsx"

def consolidar_requisitos():
    datos_finales = []
    
    # 1. Buscar todos los ficheros con extensión que contengan datos separados por ;
    # Puedes cambiar la extensión según tus archivos (*.txt, *.csv, etc.)
    ficheros = list(DIRECTORIO_REQUISITOS.glob("*.md")) + list(DIRECTORIO_REQUISITOS.glob("*.txt"))
    print(f"Encontrados {len(ficheros)} archivos para procesar.")

    for fichero in ficheros:
        # 2. Obtener modelo y proyecto del nombre del archivo
        nombre_limpio = fichero.stem.replace("output_", "")
        
        try:
            partes = nombre_limpio.split("_", 1)
            modelo = partes[0]
            proyecto = partes[1]
        except IndexError:
            modelo = "Desconocido"
            proyecto = nombre_limpio

        # 3. Leer contenido del fichero separado por ;
        with open(fichero, "r", encoding="utf-8") as f:
            lineas = f.readlines()

        for linea in lineas:
            linea = linea.strip()
            
            # Descartar líneas que no contengan ";"
            if ";" not in linea:
                continue
            
            # Ignorar la fila de cabecera
            if linea.lower().startswith("id;"):
                continue

            # 4. Procesar columnas separadas por ;
            columnas = [col.strip() for col in linea.split(";")]
            
            # Esperamos que tenga al menos 3 columnas (ID, Requisito, Texto Original)
            if len(columnas) >= 3:
                datos_finales.append({
                    "Modelo": modelo,
                    "Proyecto": proyecto,
                    "ID_requisito_elicitado": columnas[0],
                    "Texto requisito elicitado": columnas[1],
                    "Texto origen": columnas[2]
                })

    # 5. Crear DataFrame y Exportar
    df = pd.DataFrame(datos_finales)
    
    # Eliminar duplicados exactos si los hubiera por error de lectura
    df.drop_duplicates(inplace=True)

    # Guardar en Excel
    df.to_excel(ARCHIVO_SALIDA, index=False)
    print(f"✅ Proceso completado. Archivo generado en: {ARCHIVO_SALIDA}")
    print(f"Total de requisitos procesados: {len(df)}")

if __name__ == "__main__":
    consolidar_requisitos()
