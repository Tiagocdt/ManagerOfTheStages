import matplotlib.pyplot as plt
import numpy as np
from data import prepare_data

def plot_development_times(df, available_temperatures, points, values):
    plt.figure(figsize=(12, 8))

    # Check if available_temperatures is empty and default to 26 if it is
    if not available_temperatures:
        available_temperatures = [26]  # Temporarily use 26 as the default for plotting
        print("No available temperatures specified, defaulting to 26°C for plotting.")

    for temperature in available_temperatures:  # Loop over specified available temperatures
        subset = df[df['Temperature'] == temperature]
        if not subset.empty:
            plt.plot(subset['Development_Time'], subset['Stage'], label=f'{temperature}°C', marker='o')  # Swap x and y
        else:
            print(f"No data available for temperature {temperature}°C.")

    plt.scatter(values, points[:, 1], color='red', label='Data Points', marker='x')
    plt.xlabel('Development Time (hours)')
    plt.ylabel('Developmental Stage')
    plt.title('Development Times by Stage and Temperature')
    plt.legend(title='Temperature')
    plt.grid(True)
    plt.show()