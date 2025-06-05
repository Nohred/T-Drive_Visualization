---
# Visualización Espaciotemporal del Tráfico en Beijing

Este proyecto consiste en el procesamiento, análisis y visualización de datos GPS provenientes de una flota de taxis en la ciudad de Beijing. Utilizando datos públicos del proyecto GeoLife de Microsoft Research, se desarrolló un pipeline que permite convertir millones de registros crudos en mapas dinámicos y representaciones gráficas del flujo vehicular urbano.

## Objetivo

El propósito principal es detectar patrones de tráfico, identificar zonas de congestión, y distinguir vías de alta velocidad a lo largo del día mediante un visor horario interactivo. Para ello, se implementaron técnicas de limpieza de datos, cálculo de velocidades, map matching con la red vial de la ciudad, y visualización geográfica con mapas generados automáticamente.

## Características del proyecto

- Limpieza y validación de millones de registros GPS.
- Cálculo de velocidades a partir de distancias geodésicas (fórmula de Haversine).
- Asignación espacial de puntos GPS a la red vial real mediante OSMnx.
- Agregación por hora y tramo para análisis espaciotemporal.
- Visualización de tráfico por hora usando mapas con escala de color (Folium).
- Exportación automática de mapas a imágenes, GIF animado y visor HTML con slider.

## Datos

Los datos provienen del proyecto [T-Drive Trajectory Dataset]([https://www.microsoft.com/en-us/research/project/geolife-building-social-networks-using-human-location-history/](https://www.kaggle.com/datasets/arashnic/tdriver)), que contiene trayectorias de taxis en Beijing durante febrero de 2008.

> **Nota:** Por motivos de tamaño, los archivos procesados y pesados han sido excluidos del repositorio mediante `.gitignore`.

## Estructura del repositorio

```

├── data/                # Datos crudos y red vial (no incluidos)
├── scripts/             # Módulos del pipeline (parser, limpieza, visualización, etc.)
├── output/              # Imágenes, mapas y animaciones generadas
├── main.py              # Ejecución principal del flujo de análisis
├── data\_exploration.ipynb # Exploración y validación inicial de los datos
└── README.md

````

## Requisitos

- Python 3.8+
- Pandas, Numpy, Matplotlib, Folium, GeoPandas, OSMnx, Selenium, ImageIO, etc.

## Uso

```bash
# Ejecuta el pipeline completo desde main.py
python main.py
````
