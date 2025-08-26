
def procesa_datos_vivienda(año):
    """Procesa los datos de vivienda para un año específico"""
    raw_vivienda_dir = base_data_dir / f"interm/enigh/año_{año}/extracted"
    extract_dir = base_data_dir / f"plata/vivienda/año_{año}"
    
    archivos = list(extract_dir.glob("*.csv"))
    datos = procesar_datos(extract_dir, archivos, año)
    return datos


def guardar_parquet(datos, año):
    """Guarda los datos en formato Parquet"""
    output_dir = processed_dir / f"año_{año}"
    output_dir.mkdir(parents=True, exist_ok=True)

    for nombre, df in datos.items():
        output_path = output_dir / f"{nombre}.parquet"
        pq.write_table(
            pa.Table.from_pandas(df),
            output_path,
            compression='snappy'
        )
        logger.info(f"Datos guardados en Parquet: {output_path}")
        try:
            subprocess.run(
                ["dvc", "add", str(output_path.relative_to(base_data_dir))],
                cwd=base_data_dir,
                capture_output=True,
                text=True,
                check=True
            )
            logger.info(f"Datos agregados en DVC de {output_path}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Error ejecutando DVC, mucho cuidado: {e}")
    return output_dir

def procesar_datos(extract_dir, archivos, año):
    """Procesa y convierte los datos a Parquet"""
    
    # Encontrar archivos CSV
        
    datos_procesados = {}
    for archivo in (a for a in archivos if a.lower().endswith('.csv')):
        path_archivo = extract_dir / archivo.stem.lower()
        try:
            df = pd.read_csv(path_archivo, encoding='UTF-8', low_memory=False)
                
            # Limpiar nombres de columnas
            df.columns = (
                df.columns
                .str.lower()
                .str.replace(' ', '_')
                .str.replace('[^a-z0-9_]', '', regex=True)
            )         
            # Reemplazar valores perdidos
            df = df.replace({' ': pd.NA, '': pd.NA, 'NA': pd.NA, 'N/A': pd.NA})
            # Agregar metadatos
            df['_año_encuesta'] = año
            df['_fecha_procesamiento'] = datetime.now()     
            datos_procesados[archivo] = df
                
        except Exception as e:
            logger.warning(f"Error procesando {archivo}: {e}")
        
        return datos_procesados

