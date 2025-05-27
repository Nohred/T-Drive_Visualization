import pandas as pd
import geopandas as gpd
import folium
import os

def aggregate_speed_by_edge_and_hour(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrupa por calle y hora, y calcula velocidad promedio.
    """
    print("Calculando velocidad promedio por calle y hora...")
    
    df['hour'] = df['timestamp'].dt.floor('h')

    grouped = df.groupby(['edge_u', 'edge_v', 'hour'])['speed_kmh'].mean().reset_index()
    grouped = grouped.rename(columns={'speed_kmh': 'avg_speed_kmh'})

    print(f"Total de filas agregadas: {len(grouped)}")
    return grouped

def generate_folium_map(speed_by_edge: pd.DataFrame, edges_gpkg: str, output_folder="output/maps"):
    """
    Genera mapas de calor por hora usando folium.
    """
    print("Generando mapas de calor por hora...")

    edges = gpd.read_file(edges_gpkg)
    os.makedirs(output_folder, exist_ok=True)

    speed_by_edge['hour_str'] = speed_by_edge['hour'].dt.strftime('%Y-%m-%d %H:%M:%S')

    max_speed = speed_by_edge['avg_speed_kmh'].max()

    for hour, group in speed_by_edge.groupby('hour'):
        m = folium.Map(location=[39.9, 116.4], zoom_start=11, tiles='cartodbpositron')

        merged = edges.merge(group, how='left', left_on=['u', 'v'], right_on=['edge_u', 'edge_v'])
        merged = merged.dropna(subset=['avg_speed_kmh'])

        
        for _, row in merged.iterrows():
            color = get_color(row['avg_speed_kmh'], max_speed)
            folium.PolyLine(
                locations=[(pt[1], pt[0]) for pt in row['geometry'].coords],
                color=color,
                weight=3,
                opacity=0.8
            ).add_to(m)

        hour_str = hour.strftime("%Y-%m-%d_%H")
        map_path = os.path.join(output_folder, f"map_{hour_str}.html")
        m.save(map_path)
        print(f"Mapa guardado: {map_path}")

import folium
import geopandas as gpd
import pandas as pd
import json
import os
from folium.plugins import TimeSliderChoropleth

def generate_timeslider_map(speed_by_edge: pd.DataFrame, edges_gpkg: str, output_file="output/traffic_slider_map.html"):
    """
    Genera un mapa interactivo con barra de tiempo usando TimeSliderChoropleth de folium.
    """
    print("Generando mapa con barra de tiempo...")

    # Leer red vial
    edges = gpd.read_file(edges_gpkg)

    # Convertir hora a string (para el slider)
    speed_by_edge['hour_str'] = speed_by_edge['hour'].dt.strftime('%Y-%m-%dT%H:%M:%S')

    # Encontrar velocidad máxima para escala
    max_speed = speed_by_edge['avg_speed_kmh'].max()

    # Unir datos de velocidad con edges
    merged = edges.merge(speed_by_edge, how='left', left_on=['u', 'v'], right_on=['edge_u', 'edge_v'])
    merged = merged.dropna(subset=['avg_speed_kmh'])

    # Agrupar por edge y recolectar velocidades por timestamp
    features = []
    for (u, v), group in merged.groupby(['u', 'v']):
        geometry = group.iloc[0]['geometry']  # mismo geometry para ese edge
        times = group['hour_str'].tolist()
        speeds = group['avg_speed_kmh'].tolist()
        coordinates = list(geometry.coords)

        style_dict = {}
        for t, s in zip(times, speeds):
            style_dict[t] = {
                'color': get_color(s, max_speed),
                'opacity': 0.8
            }

        features.append({
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": coordinates
            },
            "properties": {
                "style": style_dict
            }
        })

    geojson_data = {
        "type": "FeatureCollection",
        "features": features
    }

    # Crear mapa base
    m = folium.Map(location=[39.9, 116.4], zoom_start=11, tiles="cartodbpositron")

    # Añadir capa con barra de tiempo
    TimeSliderChoropleth(
        data=json.dumps(geojson_data),
        styledict={str(i): f["properties"]["style"] for i, f in enumerate(features)}
    ).add_to(m)

    # Guardar mapa
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    m.save(output_file)
    print(f"Mapa con slider guardado en {output_file}")



def get_color(speed, max_speed):
    """
    Retorna un color en formato HEX que representa la intensidad del tráfico.
    Baja velocidad = rojo oscuro, Alta velocidad = rojo claro.
    """
    if pd.isna(speed):
        return "#000000"

    # Normalizar velocidad entre 0 y 1
    norm = min(speed / max_speed, 1.0)

    # Rojo: fijo en 255
    r = 255
    # Verde y azul van de 0 (oscuro) a 204 (claro)
    g = int(204 * norm)
    b = int(204 * norm)

    return f"#{r:02x}{g:02x}{b:02x}"

