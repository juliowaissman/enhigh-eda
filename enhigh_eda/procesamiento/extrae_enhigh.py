import logging
import argparse
from pathlib import Path
import zipfile


## LOGGER
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


base_data_dir = Path("data")
interm_dir = base_data_dir / "interm" / "enigh"

def extraer_datos(año):
    """Extrae los datos del archivo zip"""
    raw_dir = base_data_dir / "raw" / "enigh" / f"año_{año}"
    zip_path = raw_dir / f"enigh_{año}_raw.zip"
    extract_dir = interm_dir / f"año_{año}" / "extracted"
    extract_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Extrayendo datos a: {extract_dir}...")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            archivos = zip_ref.namelist()
            zip_ref.extractall(extract_dir)
    except Exception as e:
        logger.error(f"Error extrayendo datos: {e}")
    logger.info(f"Extracción completa: {extract_dir}")
    
    return extract_dir, archivos


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Procesar datos ENHIGH')
    parser.add_argument('--año', type=int, required=True, help='Año de la encuesta')
    args = parser.parse_args()
    
    # Extraer datos
    extract_dir, archivos = extraer_datos(args.año)
    logger.info(f"Directorio de extracción: {extract_dir}")
    logger.info(f"Archivos extraídos: {archivos}")
