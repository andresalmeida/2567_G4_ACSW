from fastapi import FastAPI, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import pandas as pd
import numpy as np
import os
from datetime import date
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg') 
import asyncio
import psutil  # Para manejar archivos abiertos y procesos
import shutil  # Para mover archivos temporalmente antes de eliminarlos
import time  # Para usar time.sleep

app = FastAPI()

# Configuración de plantillas y archivos estáticos
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

UPLOAD_FOLDER = "static/uploads"
PLOT_FOLDER = "static"
EXPORT_FOLDER = "static/exports"
DATA_FOLDER = "data"

# Crear directorios si no existen
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(EXPORT_FOLDER, exist_ok=True)

# Leer el archivo de homologación
homologacion_path = os.path.join(DATA_FOLDER, 'Homologación.xlsx')
homologacion = pd.read_excel(homologacion_path, sheet_name='DATOS', dtype={'COD_CAPA': str})
lista_capa = homologacion[['Grupo', 'COD_CAPA', 'CAPA']].drop_duplicates()

# Definir las columnas esperadas
COLUMNAS_ESPERADAS = {'CAPA', 'SECTORIAL', 'DEVENGADO', 'CATEGORIA', 'UDAF'}

# Página principal
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "download_url": None})

# Subir y procesar archivo Excel
@app.post("/upload/")
async def upload_excel(request: Request, file: UploadFile):
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(filepath, "wb") as buffer:
        buffer.write(file.file.read())

    try:
        # Validar si la hoja 'DATOS' existe
        excel_file = pd.ExcelFile(filepath)
        if 'DATOS' not in excel_file.sheet_names:
            return templates.TemplateResponse("index.html", {
                "request": request,
                "error_message": f"ERROR: Hoja 'DATOS' no encontrada"
            })

        # Leer el archivo Excel
        df = pd.read_excel(filepath, sheet_name='DATOS', dtype={'institucion': str})
    except Exception:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error_message": "Error al leer el archivo Excel. Asegúrese de que el formato es correcto."
        })

    # Normalizar columnas
    def limpiar_columnas(columnas):
        return (columnas.str.strip()
                .str.upper()
                .str.replace('Ñ', 'N')
                .str.replace(' ', '_'))
    
    df.columns = limpiar_columnas(df.columns)
    
    # Validar que el archivo tiene las columnas esperadas
    columnas_faltantes = COLUMNAS_ESPERADAS - set(df.columns)
    if columnas_faltantes:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error_message": f"El archivo no contiene las columnas esperadas: {', '.join(columnas_faltantes)}"
        })

    # Validar columna 'DEVENGADO'
    if 'DEVENGADO' not in df.columns:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error_message": "El archivo no contiene la columna 'DEVENGADO'."
        })

    # Normalizar valores
    df['COD_CAPA'] = df['COD_CAPA'].astype(str).fillna('SIN_CAPA')
    lista_capa['COD_CAPA'] = lista_capa['COD_CAPA'].astype(str).fillna('SIN_CAPA')

    # Cruce con lista_capa
    cruce = df.merge(lista_capa[['COD_CAPA', 'Grupo']], on='COD_CAPA', how='left')
    cruce['COD_CAPA'].replace('SIN_CAPA', np.nan, inplace=True)

    # Cálculos
    total_gpa = df['DEVENGADO'].sum()

    result = cruce.groupby(['Grupo', 'CAPA']).agg({'DEVENGADO': 'sum'}).sort_values(by=['Grupo'], ascending=False)
    result['porc_gpa'] = result['DEVENGADO'] / total_gpa

    result_categoria = cruce.groupby(['Grupo', 'CAPA', 'CATEGORIA']).agg({'DEVENGADO': 'sum'})
    result_udaf = cruce.groupby(['Grupo', 'CAPA', 'UDAF']).agg(devengado_udaf=('DEVENGADO', 'sum')).reset_index()

    result_sectorial = cruce.groupby(['SECTORIAL'])['DEVENGADO'].sum().reset_index()

    # Generar y guardar gráfico
    plt.figure(figsize=(10, 6))
    plt.bar(result_sectorial['SECTORIAL'], result_sectorial['DEVENGADO'], color='#2c7d59')
    plt.title('Devengado por Sectorial')
    plt.xlabel('Sectorial')
    plt.ylabel('Devengado')
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    # Guardar gráfico en la carpeta static
    plot_path = os.path.join(PLOT_FOLDER, "plot.png")
    plt.savefig(plot_path)
    plt.close()

    # Guardar el archivo Excel generado
    export_path = os.path.join(EXPORT_FOLDER, f'bdd_{str(date.today())}.xlsx')
    with pd.ExcelWriter(export_path, engine='openpyxl') as writer:
        result.to_excel(writer, sheet_name='result', index=False)
        result_categoria.to_excel(writer, sheet_name='result_categoria', index=False)
        result_udaf.to_excel(writer, sheet_name='result_udaf', index=False)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "tables": [
            {"title": "Resultado por Grupo y CAPA", "data": result.to_html(classes="styled-table")},
            {"title": "Resultado por Categoría", "data": result_categoria.to_html(classes="styled-table")},
            {"title": "Resultado por UDAF", "data": result_udaf.to_html(classes="styled-table")}
        ],
        "plot_url": "/static/plot.png",
        "download_url": f"/static/exports/bdd_{str(date.today())}.xlsx"
    })


@app.get("/reset/")
async def reset():
    loop = asyncio.get_running_loop()
    loop.run_in_executor(None, eliminar_archivos)  # Ejecutar en segundo plano
    return RedirectResponse(url='/')


def eliminar_archivos():
    intentos = 1  # Número de reintentos
    for _ in range(intentos):
        archivos_restantes = os.listdir(UPLOAD_FOLDER)
        
        if not archivos_restantes:
            print("Todos los archivos fueron eliminados exitosamente.")
            break
        
        for file in archivos_restantes:
            file_path = os.path.join(UPLOAD_FOLDER, file)

            try:
                # Verifica si el archivo está bloqueado por algún proceso
                for proc in psutil.process_iter():
                    try:
                        if file_path in [f.path for f in proc.open_files()]:
                            proc.kill()  # Mata el proceso que usa el archivo
                            print(f"Proceso que usaba {file} fue cerrado.")
                    except Exception:
                        pass

                # Intentar mover y eliminar para desbloquear el archivo
                temp_path = file_path + ".tmp"
                if os.path.exists(file_path):
                    shutil.move(file_path, temp_path)
                    os.remove(temp_path)
                    print(f"Archivo {file} eliminado correctamente.")
            
            except Exception as e:
                print(f"Error eliminando {file}: {e}")
        
        print(f"Intentando eliminar archivos bloqueados... Archivos restantes: {os.listdir(UPLOAD_FOLDER)}")
        time.sleep(1)
    
    # Verifica si hay archivos restantes al final
    archivos_restantes = os.listdir(UPLOAD_FOLDER)
    if archivos_restantes:
        print(f"No se pudieron eliminar los archivos: {archivos_restantes}")
    else:
        print("Todos los archivos eliminados correctamente.")
    # Verifica si hay archivos restantes al final
    archivos_restantes = os.listdir(UPLOAD_FOLDER)
    if archivos_restantes:
        print(f"No se pudieron eliminar los archivos: {archivos_restantes}")
    else:
        print("Todos los archivos eliminados correctamente.")

def liberar_archivo(file_path):
    for proc in psutil.process_iter():
        try:
            for open_file in proc.open_files():
                if file_path == open_file.path:
                    proc.terminate()  # Cierra el proceso que mantiene bloqueado el archivo
                    proc.wait()
        except Exception:
            pass


