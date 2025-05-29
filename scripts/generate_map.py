import pandas as pd
import geopandas as gpd
import folium
import os

def aggregate_speed_by_edge_and_hour(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrupa por calle y hora, y calcula velocidad promedio + cantidad de puntos.
    """
    print("Calculando velocidad promedio por calle y hora...")

    df['hour'] = df['timestamp'].dt.floor('h')
    grouped = df.groupby(['edge_u', 'edge_v', 'hour']).agg(
        avg_speed_kmh=('speed_kmh', 'mean'),
        count=('speed_kmh', 'count')
    ).reset_index()

    # Filtrar para evitar los "gusanitos"
    grouped = grouped[grouped['count'] >= 1]

    print(f"Total de filas agregadas (tras filtrado): {len(grouped)}")
    return grouped


def get_color(speed, max_speed):
    """
    Devuelve un color degradado de rojo (tráfico pesado) a amarillo (fluido).
    """
    if pd.isna(speed):
        return "#00000000"  # transparente

    norm = min(speed / max_speed, 1.0)
    r = 255
    g = int(255 * norm)
    b = 0
    return f"#{r:02x}{g:02x}{b:02x}"


def generate_folium_map(speed_by_edge: pd.DataFrame, edges_gpkg: str, output_folder="output/maps"):
    """
    Genera mapas de calor por hora usando folium.
    Reduce opacidad para calles cortas y filtra segmentos poco representativos.
    """
    print("Generando mapas de calor por hora...")

    edges = gpd.read_file(edges_gpkg)
    edges['length'] = edges.geometry.length  # longitud en grados
    os.makedirs(output_folder, exist_ok=True)

    speed_by_edge['hour_str'] = speed_by_edge['hour'].dt.strftime('%Y-%m-%d %H:%M:%S')
    max_speed = speed_by_edge['avg_speed_kmh'].max()

    for hour, group in speed_by_edge.groupby('hour'):
        print(f"🕒 Procesando {hour}")
        m = folium.Map(location=[39.9, 116.4], zoom_start=11, tiles="CartoDB dark_matter")

        merged = edges.merge(group, how='inner', left_on=['u', 'v'], right_on=['edge_u', 'edge_v'])

        for _, row in merged.iterrows():
            color = get_color(row['avg_speed_kmh'], max_speed)
            opacity = 1 if row['length'] >= 0.01 else 0.6  # menos opacidad si es corto
            folium.PolyLine(
                locations=[(pt[1], pt[0]) for pt in row['geometry'].coords],
                color=color,
                weight=3,
                opacity=opacity
            ).add_to(m)

        hour_str = hour.strftime("%Y-%m-%d_%H")
        map_path = os.path.join(output_folder, f"map_{hour_str}.html")
        m.save(map_path)
        print(f"🗺️  Mapa guardado: {map_path}")
