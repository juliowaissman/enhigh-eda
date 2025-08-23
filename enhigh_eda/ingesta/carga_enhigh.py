import logging
import requests
import argparse
import datetime

from pathlib import Path
import yaml
import subprocess

## LOGGER
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

## INFORMACIÓN GLOBAL
base_data_dir = Path("data")
raw_dir = base_data_dir / "raw" / "enigh"
encuestas_urls = {
    2024: "https://www.inegi.org.mx/contenidos/programas/enigh/nc/2024/datosabiertos/conjunto_de_datos_enigh2024_ns_csv.zip",
    2022: "https://www.inegi.org.mx/contenidos/programas/enigh/nc/2022/datosabiertos/conjunto_de_datos_enigh_ns_2022_csv.zip",
    2020: "https://www.inegi.org.mx/contenidos/programas/enigh/nc/2020/datosabiertos/conjunto_de_datos_enigh_ns_2020_csv.zip",
    2018: "https://www.inegi.org.mx/contenidos/programas/enigh/nc/2018/datosabiertos/conjunto_de_datos_enigh_2018_ns_csv.zip",
    2016: "https://www.inegi.org.mx/contenidos/programas/enigh/nc/2016/datosabiertos/conjunto_de_datos_enigh2016_nueva_serie_csv.zip"
}

def descargar_datos(año=2024):
    """Descarga los datos de la ENHIGH"""
    url = encuestas_urls.get(año)
    if not url:
        raise ValueError(f"No hay datos disponibles para el año {año}")
    logger.info(f"Iniciando descarga de datos ENHIGH {año}...")
        
    año_dir = raw_dir / f"año_{año}"
    año_dir.mkdir(exist_ok=True)
        
    # Descargar archivo
    zip_path = año_dir / f"enigh_{año}_raw.zip"        
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(zip_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    logger.info(f"Descarga completa: {zip_path}")
    return zip_path



if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Descargar datos ENHIGH')
    parser.add_argument('--año', type=int, required=True, help='Año de la encuesta')
    args = parser.parse_args()
       
    # Crear directorio si no existe
    raw_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Directorio creado: {raw_dir}")
        
    # Inicializar DVC si no está inicializado
    dvc_config = base_data_dir / ".dvc" / "config"
    if not dvc_config.exists():
        try:
            subprocess.run(["dvc", "init", "--subdir"], cwd=base_data_dir, check=True)
            logger.info("DVC inicializado correctamente")
        except:
            raise ValueError("DVC no está instalado. Instala con: pip install dvc")
        
    # Descargar datos
    zip_path = descargar_datos(año=args.año)
    
    # Commit en dvc a los datos agregados
    try:
        resultado = subprocess.run(
            ["dvc", "add", str(zip_path.relative_to(base_data_dir))], 
            cwd=base_data_dir, 
            capture_output=True, 
            text=True, 
            check=True
        )
        subprocess.run(
            ["git", "add", 
             f"{zip_path.relative_to(base_data_dir)}.dvc", 
             ".gitignore"], 
            cwd=base_data_dir, 
            check=True
        )
        commit_msg = f"Actualización datos ENHIGH - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        subprocess.run(
            ["git", "commit", "-m", commit_msg], 
            cwd=base_data_dir, 
            capture_output=True, 
            text=True, 
            check=True
        )
        subprocess.run(
            ["git", "push", "-u", 'origin', 'main'], 
            cwd=base_data_dir, 
            capture_output=True, 
            text=True, 
            check=True
        )
        logger.info("Commit en DVC y en GIT realizado")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error ejecutando DVC o GIT: {e}")
        