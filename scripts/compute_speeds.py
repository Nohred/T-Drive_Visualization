import pandas as pd
import numpy as np
import os
from haversine import haversine, Unit

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
