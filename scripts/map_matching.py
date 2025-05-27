import os
import pandas as pd
import geopandas as gpd
import osmnx as ox
from shapely.geometry import Point

def map_match_gps(df: pd.DataFrame) -> pd.DataFrame:
    """
    Asocia cada punto GPS con la calle más cercana usando OSMnx.
    Devuelve un DataFrame con una nueva columna 'nearest_edge'.
    """
    output_file = "data/processed/gps_matched.csv"
    edges_file = "data/network/beijing_edges.gpkg"
    nodes_file = "data/network/beijing_nodes.gpkg"

    # Si ya existe el archivo procesado, lo cargamos
    if os.path.exists(output_file):
        print(f"Archivo con matching ya existe: {output_file}")
        return pd.read_csv(output_file, parse_dates=['timestamp'])
# Si no existe la red vial, la descargamos
    if not os.path.exists(edges_file) or not os.path.exists(nodes_file):
        print("Descargando red vial de Beijing...")
        G = ox.graph_from_place("Beijing, China", network_type='drive')
        nodes, edges = ox.graph_to_gdfs(G)
        os.makedirs("data/network", exist_ok=True)
        edges.to_file(edges_file, driver="GPKG")
        nodes.to_file(nodes_file, driver="GPKG")
    else:
        print("Cargando red vial de Beijing...")
        edges = gpd.read_file(edges_file)
        nodes = gpd.read_file(nodes_file)

    # Convertimos los puntos GPS a GeoDataFrame
    gdf_points = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df['longitude'], df['latitude']),
        crs="EPSG:4326"
    )

    print("Realizando map matching...")
    
    # Crear grafo a partir de nodos y aristas
    G = ox.graph_from_gdfs(nodes, edges)
    
    # Buscar calle más cercana para cada punto
    nearest_edge_ids = ox.nearest_edges(G, 
                                        X=gdf_points.geometry.x.values, 
                                        Y=gdf_points.geometry.y.values)

    gdf_points['edge_u'] = [e[0] for e in nearest_edge_ids]
    gdf_points['edge_v'] = [e[1] for e in nearest_edge_ids]

    print(f"Matching realizado: {len(gdf_points)} puntos asociados a calles")

    # Guardamos el resultado
    gdf_points.drop(columns='geometry').to_csv(output_file, index=False)
    print(f"Datos con matching guardados en {output_file}")

    return gdf_points.drop(columns='geometry')
