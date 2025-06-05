import pandas as pd
import numpy as np
import os
import glob
from haversine import haversine, Unit

def parse_taxi_logs():
    """
    Lee todos los archivos .txt de la carpeta de datos crudos y crea un único DataFrame
    con columnas estandarizadas.
    """
    input_folder = "data/raw_taxi_logs"
    output_file = "data/processed/gps_data.csv"

    # Si ya existe el CSV procesado, simplemente lo leemos
    if os.path.exists(output_file):
        print(f"Archivo ya procesado encontrado: {output_file}")
        df = pd.read_csv(output_file)
        print(f"Total de registros cargados: {len(df)}")
        return df
    
    all_files = sorted(glob.glob(os.path.join(input_folder, "*.txt")))

    if not all_files:
        raise FileNotFoundError(f"No se encontraron archivos .txt en {input_folder}")

    print(f"Leyendo {len(all_files)} archivos de taxi...")

    dataframes = []
    for idx, file in enumerate(all_files):
        try:
            df = pd.read_csv(file, header=None, names=['id', 'timestamp', 'longitude', 'latitude'])
            dataframes.append(df)
            if (idx + 1) % 100 == 0 or idx + 1 == len(all_files):
                print(f"Procesados {idx + 1}/{len(all_files)} archivos")
        except Exception as e:
            print(f"Error al leer {file}: {e}")

    if not dataframes:
        raise ValueError("No se pudo leer ningún archivo válido")

    # Filtrar DataFrames vacíos antes de concatenar
    dataframes = [df for df in dataframes if not df.empty]

    combined = pd.concat(dataframes, ignore_index=True)
    print(f"Total de registros combinados: {len(combined)}")

    # Guardar en archivo CSV para uso posterior
    os.makedirs("data/processed", exist_ok=True)
    combined.to_csv(output_file, index=False)
    print(f"Datos guardados en {output_file}")

    return combined

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

def compute_speeds(df: pd.DataFrame, max_speed_kmh: float = 140.0, max_idle_time_hr: float = 0.167) -> pd.DataFrame:
    """
    Calcula velocidades entre puntos consecutivos y elimina:
    - Velocidades irreales (> max_speed_kmh)
    - Periodos detenidos prolongados (idle > max_idle_time_hr)
    Si ya existe el archivo procesado, lo carga directamente.
    """
    output_file = "data/processed/gps_with_speed.csv"
    if os.path.exists(output_file):
        print(f"Archivo ya procesado encontrado: {output_file}")
        return pd.read_csv(output_file, parse_dates=['timestamp'])

    print("Calculando velocidades y limpiando...")

    df['delta_time'] = np.nan
    df['distance_km'] = np.nan
    df['speed_kmh'] = np.nan

    cleaned_records = []

    for taxi_id, group in df.groupby('id'):
        group = group.sort_values('timestamp').reset_index(drop=True)

        delta_times = [np.nan]
        distances = [np.nan]
        speeds = [np.nan]

        for i in range(1, len(group)):
            t1, t2 = group.loc[i-1, 'timestamp'], group.loc[i, 'timestamp']
            p1 = (group.loc[i-1, 'latitude'], group.loc[i-1, 'longitude'])
            p2 = (group.loc[i, 'latitude'], group.loc[i, 'longitude'])

            delta_h = (t2 - t1).total_seconds() / 3600.0
            dist_km = haversine(p1, p2)
            speed = dist_km / delta_h if delta_h > 0 else 0.0

            delta_times.append(delta_h)
            distances.append(dist_km)
            speeds.append(speed)

        group['delta_time'] = delta_times
        group['distance_km'] = distances
        group['speed_kmh'] = speeds

        group = group[(group['speed_kmh'].isna()) | (group['speed_kmh'] < max_speed_kmh)]

        group['is_idle'] = group['speed_kmh'] == 0
        group['idle_group'] = (group['is_idle'] != group['is_idle'].shift()).cumsum()

        idle_durations = group.groupby('idle_group')['delta_time'].sum()
        grupos_a_eliminar = idle_durations[idle_durations >= max_idle_time_hr].index

        group = group[~((group['idle_group'].isin(grupos_a_eliminar)) & (group['is_idle']))]

        print(f"Taxi {taxi_id}: Registros después de limpieza: {len(group)}")

        cleaned_records.append(group.drop(columns=['is_idle', 'idle_group']))

    final_df = pd.concat(cleaned_records, ignore_index=True)

    # Guardar CSV
    print(f"Guardando datos procesados en {output_file}...")
    os.makedirs("data/processed", exist_ok=True)
    final_df.to_csv(output_file, index=False)
    print(f"Datos guardados en {output_file}")
    print(f"Registros finales: {len(final_df)}")

    return final_df
