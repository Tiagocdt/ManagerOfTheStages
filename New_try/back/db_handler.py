# db_handler.py

import sqlite3
import numpy as np
import pandas as pd
from scipy.interpolate import Rbf

# Connect to the SQLite database
def get_db_connection():
    conn = sqlite3.connect('medaka_development.db')
    conn.row_factory = sqlite3.Row
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
    rows = cursor.fetchall()
    conn.close()
    data = [dict(row) for row in rows]
    return data

def prepare_data(data):
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
    data_df = pd.DataFrame(data_list)
    points = data_df[['Temperature', 'Stage']].values
    values = data_df['Development_Time'].values
    return points, values

def create_interpolated_dataset(points, values, method='rbf', available_temperatures=None, max_stage=None):
    # Include available temperatures in the grid
    if available_temperatures is not None and len(available_temperatures) > 0:
        temperatures = np.array(sorted(set(available_temperatures)))
    else:
        temperatures = np.unique(points[:, 0])

    # Include all stages up to max_stage
    if max_stage is not None:
        stages = np.arange(0, max_stage + 1)
    else:
        stages = np.unique(points[:, 1])

    # Prepare meshgrid
    temp_mesh, stage_mesh = np.meshgrid(temperatures, stages, indexing='ij')

    # Flatten the meshgrid for interpolation
    temps_flat = temp_mesh.ravel()
    stages_flat = stage_mesh.ravel()

    # Use RBF interpolation
    rbf_interpolator = Rbf(points[:, 0], points[:, 1], values, function='thin_plate', smooth=0.2)

    # Interpolate values
    interpolated_values = rbf_interpolator(temps_flat, stages_flat)

    # Set negative interpolated values to zero
    interpolated_values = np.where(interpolated_values < 0, 0, interpolated_values)

    # Create DataFrame
    df = pd.DataFrame({
        'Temperature': temps_flat,
        'Stage': stages_flat,
        'Development_Time': interpolated_values
    })

    return df
