import sqlite3
import numpy as np
import pandas as pd
from scipy.interpolate import Rbf

# Connect to the SQLite database (you can reuse this connection in different functions)
def get_db_connection():
    conn = sqlite3.connect('medaka_development.db')
    conn.row_factory = sqlite3.Row  # Makes rows behave like dictionaries (optional)
    return conn

# Add a new record to the database
def add_record(species, temperature, stage, development_time_hpf):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO development_times (species, temperature, stage, development_time_hpf)
        VALUES (?, ?, ?, ?)
    ''', (species, temperature, stage, development_time_hpf))
    conn.commit()
    conn.close()

# Fetch all data from the database
def fetch_all_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM development_times')
    data = cursor.fetchall()  # Returns a list of rows
    conn.close()
    return data

# Fetch specific data by species and temperature
def fetch_by_species_and_temp(species, temperature):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM development_times WHERE species = ? AND temperature = ?', (species, temperature))
    data = cursor.fetchall()
    conn.close()
    return data

def prepare_data(data):
    # This will store each entry as a dictionary in a list
    data_list = []

    for entry in data:
        temperature = float(entry['temperature'])
        stage = float(entry['stage'])
        development_time = float(entry['development_time_hpf'])
        data_list.append({
            'Temperature': temperature,
            'Stage': stage,
            'Development_Time': development_time
        })
    
    # Convert the list of dictionaries to a DataFrame
    data_df = pd.DataFrame(data_list)
    
    points = data_df[['Temperature', 'Stage']].values
    values = data_df['Development_Time'].values
    
    return points, values

# Create an interpolated dataset   
def create_interpolated_dataset(points, values, method='linear'):
    # Define the range of temperatures and stages you need
    temperatures = np.linspace(18, 32, 15)  # From 18 to 32 degrees, 15 points
    stages = np.linspace(0, 40, 41)         # From stage 0 to 40, 41 points
    
    # Prepare mesh for temperatures and stages
    temp_mesh, stage_mesh = np.meshgrid(temperatures, stages, indexing='ij')

    # Use Radial Basis Function for interpolation
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
