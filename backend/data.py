import json
import numpy as np
import pandas as pd
from scipy.interpolate import Rbf
file_path = 'Development_Times.json'

# Load data from a file
def load_data(file_path):
    try:
        with open(file_path, 'r') as file:
            if file.read().strip():
                file.seek(0)  # Setzt den Dateizeiger zurück an den Anfang der Datei
                data = json.load(file)
                # Stellen Sie sicher, dass die geladenen Daten das erwartete Format haben
                if "temperatures" in data:
                    return data
                else:
                    # Wenn "temperatures" nicht im Root-Objekt ist, initialisieren Sie die Struktur
                    return {"temperatures": []}
            else:
                # Wenn die Datei leer ist, initialisieren Sie die Struktur
                return {"temperatures": []}
    except FileNotFoundError:
        # Wenn die Datei nicht existiert, initialisieren Sie die Struktur
        return {"temperatures": []}

# Save data to a file
def save_data(file_path, data):
    print(f"Saving data: {data}")
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

# Main function to add data
def add_entree(file_path, temperature, stage, time_in_hpf):
    data = load_data(file_path)
    # Check if the temperature already exists
    temp_entry = None
    for temp in data["temperatures"]:
        if temp["temperature"] == temperature:
            temp_entry = temp
            break

    # If the temperature does not exist, add it
    if not temp_entry:
        temp_entry = {"temperature": temperature, "stages": []}
        data["temperatures"].append(temp_entry)
    
    # Check if the stage already exists
    stage_entry = None
    for st in temp_entry["stages"]:
        if st["stage"] == stage:
            stage_entry = st
            break
    
    # If the stage does not exist, add it
    if not stage_entry:
        stage_entry = {"stage": stage, "times": []}
        temp_entry["stages"].append(stage_entry)
    
    # Add the time in HPF
    stage_entry["times"].append(time_in_hpf)
    
    # Save the updated data
    save_data(file_path, data)
    print("Data successfully added.")

# Prepare data for interpolation
def prepare_data(data):
    # This will store each entry as a dictionary in a list
    data_list = []
    detailed_data_list = []  # To store detailed data including Mean_Time

    for temperature_info in data['temperatures']:
        temperature = float(temperature_info['temperature'])
        for stage_info in temperature_info['stages']:
            stage = float(stage_info['stage'])
            times = [float(time) for time in stage_info['times']]
            mean_time = np.mean(times) if times else np.nan
            data_list.append({
                'Temperature': temperature,
                'Stage': stage,
                'Mean_Time': mean_time
            })
    
    # Convert the list of dictionaries to a DataFrame
    data_df = pd.DataFrame(data_list)
    
    points = data_df[['Temperature', 'Stage']].values
    values = data_df['Mean_Time'].values
    
    return points, values

def create_interpolated_dataset(points, values, method='linear'):
    # Define the range of temperatures and stages you need
    temperatures = np.linspace(18, 32, 15)  # From 18 to 32 degrees, 15 points
    stages = np.linspace(0, 40, 41)         # From stage 0 to 40, 41 points
    
    # Prepare mesh for temperatures and stages
    temp_mesh, stage_mesh = np.meshgrid(temperatures, stages, indexing='ij')

    # Use Radial Basis Function for interpolation to consider the shape across 26 degrees
    rbf_interpolator = Rbf(points[:, 0], points[:, 1], values, function='thin_plate', smooth=0.2)
    # Interpolate values
    interpolated_values = rbf_interpolator(temp_mesh, stage_mesh)
    
    # Set negative interpolated values to zero
    interpolated_values = np.where(interpolated_values < 0, 0, interpolated_values)
    
    # Create a DataFrame from the meshgrid and interpolated values
    df = pd.DataFrame({
        'Temperature': temp_mesh.ravel(),
        'Stage': stage_mesh.ravel(),
        'Development_Time': interpolated_values.ravel()
    })

    return df