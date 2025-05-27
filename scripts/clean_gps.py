import pandas as pd
import os

def clean_taxi_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia el DataFrame de GPS:
    - Convierte timestamp a datetime
    - Elimina registros con timestamps inválidos
    - Filtra coordenadas fuera de Beijing
    - Ordena por taxi y tiempo
    - Guarda un checkpoint en CSV para evitar reprocesar
    """
    output_file = "data/processed/gps_clean.csv"

    # Si ya existe el archivo limpio, lo cargamos
    if os.path.exists(output_file):
        print(f"Archivo de limpieza ya existe: {output_file}")
        return pd.read_csv(output_file, parse_dates=['timestamp'])

    print("Iniciando limpieza de datos...")

    # Convertir timestamps
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df = df.dropna(subset=['timestamp'])

    # Filtrar coordenadas fuera de rango (Beijing aprox.)
    lat_bounds = (39.5, 40.5)
    lon_bounds = (115.5, 117.5)

    before_filter = len(df)
    df = df[
        (df['latitude'].between(*lat_bounds)) &
        (df['longitude'].between(*lon_bounds))
    ]
    print(f"Registros eliminados por coordenadas fuera de Beijing: {before_filter - len(df)}")

    # Ordenar por id y timestamp
    df = df.sort_values(by=['id', 'timestamp']).reset_index(drop=True)

    print(f"Registros después de limpieza: {len(df)}")

    # Guardar CSV limpio
    os.makedirs("data/processed", exist_ok=True)
    df.to_csv(output_file, index=False)
    print(f"Datos limpios guardados en {output_file}")

    return df
