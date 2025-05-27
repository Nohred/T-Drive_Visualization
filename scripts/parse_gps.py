import pandas as pd
import os
import glob

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
