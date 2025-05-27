from parse_gps import parse_taxi_logs
from clean_gps import clean_taxi_data
from compute_speeds import compute_speeds
from map_matching import map_match_gps
from generate_map import generate_folium_map
from generate_map import aggregate_speed_by_edge_and_hour
from generate_map import generate_timeslider_map
from generate_gif import generate_slider_from_images
if __name__ == "__main__":
    # Lee los registros de GPS de taxis
    # raw_df = parse_taxi_logs()
    # # Limpia los datos de GPS, filtra y ordena
    # clean_df = clean_taxi_data(raw_df)
    # # Calcula velocidades y elimina secuencias con más de 10 minutos parados
    # speed_df = compute_speeds(clean_df)
    # # Realiza el map matching de los puntos GPS a las calles
    # matched_df = map_match_gps(speed_df)
    # # Agrupa por arista y hora
    # speed_by_edge = aggregate_speed_by_edge_and_hour(matched_df)

    # # Genera un mapa de folium con la velocidad promedio por arista
    # generate_folium_map(speed_by_edge,  edges_gpkg="data/network/beijing_edges.gpkg")

    # generate_timeslider_map(speed_by_edge, edges_gpkg="data/network/beijing_edges.gpkg")


    # from generate_gif import capture_maps_to_images, generate_gif_from_images

    # # Parámetros de rutas
    # html_folder = "output/maps"
    # image_folder = "output/images"
    # gif_path = "output/traffic.gif"
    # chromedriver_path = chromedriver_path = r"C:\CodeTools\ChromeDriver\chromedriver.exe"# ruta de chromedriver

    # # Generar imágenes desde HTML
    # capture_maps_to_images(html_folder, image_folder, driver_path=chromedriver_path)

    # # Crear el GIF
    # generate_gif_from_images(image_folder, gif_path, duration=0.75)

    generate_slider_from_images(
    image_folder="output/images",
    output_html="output/traffic_slider.html"
)

