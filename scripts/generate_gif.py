import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from PIL import Image
import imageio

def capture_maps_to_images(html_folder: str, image_folder: str, driver_path: str, wait_time=2):
    """
    Abre cada mapa HTML en Chrome y guarda una captura como imagen PNG.
    """
    os.makedirs(image_folder, exist_ok=True)

    html_files = sorted([f for f in os.listdir(html_folder) if f.endswith('.html')])

    # Configurar opciones de Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Ejecutar sin interfaz gráfica
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Inicializar el driver con la nueva API
    if driver_path:
        service = Service(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
    else:
        driver = webdriver.Chrome(options=chrome_options)

    for file in html_files:
        path = os.path.abspath(os.path.join(html_folder, file))
        driver.get(f"file:///{path}")
        time.sleep(wait_time)  # esperar a que cargue todo

        img_name = file.replace('.html', '.png')
        img_path = os.path.join(image_folder, img_name)
        driver.save_screenshot(img_path)
        print(f"Captura guardada: {img_path}")

    driver.quit()

def generate_gif_from_images(image_folder: str, output_gif: str, duration=0.5):
    """
    Une todas las imágenes PNG del folder en un solo GIF animado.
    """
    images = []
    files = sorted([f for f in os.listdir(image_folder) if f.endswith('.png')])
    for file in files:
        img_path = os.path.join(image_folder, file)
        images.append(imageio.imread(img_path))

    imageio.mimsave(output_gif, images, duration=duration)
    print(f"GIF generado: {output_gif}")

def generate_slider_from_images(image_folder: str, output_html: str):
    """
    Genera un HTML con slider para explorar imágenes PNG (como un visualizador interactivo).
    """
    files = sorted([f for f in os.listdir(image_folder) if f.endswith('.png')])
    if not files:
        print("No se encontraron imágenes en la carpeta.")
        return

    slider_steps = len(files)
    image_paths = [f"images/{file}" for file in files]


    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Visualización de Tráfico - Slider</title>
    <style>
        body {{
            background-color: #111;
            color: white;
            text-align: center;
            font-family: sans-serif;
        }}
        img {{
            max-width: 100%;
            height: auto;
            border: 4px solid #444;
            border-radius: 8px;
        }}
        #slider {{
            width: 80%;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <h1>Visualización de Tráfico - Slider</h1>
    <img id="trafficImage" src="{image_paths[0]}" alt="Tráfico por hora">
    <br>
    <input type="range" min="0" max="{slider_steps - 1}" value="0" id="slider" oninput="updateImage(this.value)">
    <p id="label">Imagen 1 de {slider_steps}</p>

    <script>
        const imagePaths = {image_paths};
        const imgElement = document.getElementById('trafficImage');
        const label = document.getElementById('label');

        function updateImage(index) {{
            imgElement.src = imagePaths[index];
            label.textContent = "Imagen " + (parseInt(index) + 1) + " de {slider_steps}";
        }}
    </script>
</body>
</html>
    """

    # Guardar HTML
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"Visualizador HTML con slider generado: {output_html}")