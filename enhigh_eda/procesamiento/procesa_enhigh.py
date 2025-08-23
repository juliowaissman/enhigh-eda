import logging
import argparse
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from datetime import datetime
import zipfile
import os
import json
import hashlib

base_data_dir = Path("data")
raw_dir = base_data_dir / "raw" / "enigh"
processed_dir = base_data_dir / "processed" / "enigh"

def extraer_datos(zip_path):
    """Extrae los datos del archivo zip"""
    extract_dir = zip_path.parent / "extracted"
    extract_dir.mkdir(exist_ok=True)
    
    logger.info(f"Extrayendo datos a: {extract_dir}...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        archivos = zip_ref.namelist()
        zip_ref.extractall(extract_dir)
    logger.info(f"Extracción completa: {extract_dir}")
    
    return extract_dir, archivos

def procesar_datos(self, extract_dir, año):
    """Procesa y convierte los datos a Parquet"""
    
    # Encontrar archivos CSV
    archivos_csv = list(extract_dir.rglob("*.csv"))
        
    datos_procesados = {}
    for archivo in archivos_csv:
        nombre = archivo.stem.lower()
        try:
            # Leer datos
            df = pd.read_csv(archivo, encoding='latin-1', low_memory=False)
                
            # Limpiar nombres de columnas
            df.columns = (
                df.columns
                .str.lower()
                .str.replace(' ', '_')
                .str.replace('[^a-z0-9_]', '', regex=True)
            )
            df = df.replace({' ': None, '': None, 'NA': None, 'N/A': None})
                
            # Agregar metadatos
            df['_año_encuesta'] = año
            df['_fecha_procesamiento'] = datetime.now()
                
            datos_procesados[nombre] = df
                
        except Exception as e:
            logger.warning(f"Error procesando {archivo}: {e}")
        
        return datos_procesados

def guardar_parquet(datos, año):
    """Guarda los datos en formato Parquet"""
    output_dir = self.processed_dir / f"año_{año}"
    output_dir.mkdir(exist_ok=True)
        
    for nombre, df in datos.items():
        output_path = output_dir / f"{nombre}.parquet"
        pq.write_table(
            pa.Table.from_pandas(df),
            output_path,
            compression='snappy'
        )
        return output_dir
