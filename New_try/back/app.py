from flask import Flask, jsonify, request
from flask_cors import CORS
import numpy as np
from user_handler import handle_and_validate_user_input
from db_handler import (
    get_db_connection,
    fetch_all_data,
    add_record,
    prepare_data,
    create_interpolated_dataset,
)
from analysis import (
    calculate_collection_times,
    calculate_exact_times,
    calculate_switch_times,
    filter_results_by_timing,
    generate_temp_combinations,
    get_interpolated_durations,
    suggest_fastest_temperature,
    convert_df_to_serializable,
)
import pandas as pd

app = Flask(__name__)
CORS(app)

@app.route('/predict', methods=['POST'])
def predict_stages():
    try:
        # Get the raw input data from the request
        input_data = request.get_json()
        
        # Handle and validate the user input
        sanitized_data = handle_and_validate_user_input(input_data)
        
        # Extract sanitized data for use in prediction logic
        required_species = sanitized_data['required_species']
        required_stages = sanitized_data['required_stages']
        available_temperatures = sanitized_data['available_temperatures']
        start_datetime = sanitized_data['start_datetime']
        desired_time = sanitized_data['desired_time']
        collection_start = sanitized_data['collection_start']
        collection_end = sanitized_data['collection_end']
        lab_days = sanitized_data['lab_days']
        lab_start_time = sanitized_data['lab_start_time']
        lab_end_time = sanitized_data['lab_end_time']

        data = fetch_all_data()
        if required_species:
            filtered_data = [entry for entry in data if entry['species'] == required_species]
        else:
            return jsonify({"error": "No species provided or species not found"}), 400

        points, values = prepare_data(filtered_data)

        if not points.size or not values.size:
            return jsonify({"error": "No valid data for interpolation."}), 400
        if len(np.unique(points, axis=0)) < 3:
            return jsonify({"error": "Not enough unique data points for interpolation"}), 400

        max_stage = 40
        interpolated_df = create_interpolated_dataset(
            points,
            values,
            method='rbf',
            available_temperatures=available_temperatures,
            max_stage=max_stage
        )

        temp_combinations = generate_temp_combinations(available_temperatures)

        extended_df = calculate_switch_times(interpolated_df, temp_combinations, required_stages)

        if desired_time:
            results_df = calculate_collection_times(extended_df, required_stages, available_temperatures, desired_time)
        elif not desired_time and start_datetime:
            results_df = calculate_exact_times(extended_df, required_stages, available_temperatures, start_datetime)
        else:
            results_df = get_interpolated_durations(interpolated_df, required_stages, available_temperatures)

        results_df.to_csv('output01.csv', index=False)

        if start_datetime or collection_start or lab_days or lab_start_time:
            filtered_results_df = filter_results_by_timing(
                results_df, lab_days, lab_start_time, lab_end_time, collection_start, collection_end, start_datetime, desired_time
            )
        else:
            filtered_results_df = results_df

        if filtered_results_df is None or filtered_results_df.empty:
            return jsonify({"error": "No available times match the specified criteria."}), 400

        filtered_results_df.to_csv('output02.csv', index=False)

        fastest_temp_df = suggest_fastest_temperature(filtered_results_df, required_stages)
    
        serializable_df = convert_df_to_serializable(fastest_temp_df)
        
        # Prepare graph data and schedule data for the frontend
        graph_data = prepare_graph_data(interpolated_df, available_temperatures)

        temperature_colors = graph_data.get('temperature_colors', {})

        schedule_data = prepare_schedule_data(
            serializable_df,
            temperature_colors,
            start_datetime=start_datetime,
            desired_time=desired_time
        )

        return jsonify({
            'graphData': graph_data,
            'scheduleData': schedule_data,
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

# Route for entering new data
@app.route('/enter-data', methods=['POST'])
def enter_data():
    input_data = request.get_json()
    rows = input_data.get('rows', [])

    for row in rows:
        species = row.get('species')
        temperature = row.get('temperature')
        stage = row.get('stage')
        duration = row.get('developmentTime')

        # Add the new data into the SQLite database
        add_record(species, temperature, stage, duration)

    # Return a success message
    return jsonify({'message': 'Data added successfully'})

# Route for getting graph data for Enter Data page
@app.route('/get-graph-data', methods=['GET'])
def get_graph_data():
    data = fetch_all_data()
    # Process data to send to frontend
    graph_data = process_graph_data(data)
    return jsonify(graph_data)

@app.route('/get-species', methods=['GET'])
def get_species():
    try:
        # Query the database for all unique species
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT species FROM development_times')
        species = cursor.fetchall()
        species_list = [s['species'] for s in species]
        return jsonify(species_list), 200
    except Exception as e:
        return jsonify({"error": "Unable to fetch species"}), 500

# Helper function to process graph data for Enter Data page
def process_graph_data(data):
    # Organize data by temperature
    df = pd.DataFrame(data)
    df['temperature'] = df['temperature'].astype(float)
    df['stage'] = df['stage'].astype(float)
    df['development_time_hpf'] = df['development_time_hpf'].astype(float)

    temperatures = df['temperature'].unique()
    graph_data = []
    colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40']

    for i, temp in enumerate(temperatures):
        temp_df = df[df['temperature'] == temp]
        dataset = {
            'temperature': temp,
            'data': temp_df[['development_time_hpf', 'stage']].to_dict(orient='records'),
            'color': colors[i % len(colors)],
        }
        graph_data.append(dataset)

    return graph_data

# Helper function to prepare graph data for Predict Stages page
def prepare_graph_data(interpolated_df, available_temperatures):
    """
    Prepare graph data with all interpolated development times for the selected species 
    across available temperatures, without filtering by required stages.
    """

    # Filter the interpolated dataframe by available temperatures
    graph_df = interpolated_df[interpolated_df['Temperature'].isin(available_temperatures)]

    # Sort the dataframe by stage and development time to get cleaner plots
    graph_df = graph_df.sort_values(by=['Stage', 'Development_Time'])

    # Unique temperatures available
    temperatures = graph_df['Temperature'].unique()
    
    # Initialize graph data structure
    graph_data = {
        'datasets': [],
        'temperature_colors': {}  # to store temperature to color mapping
    }
    
    # Color palette for different temperatures
    colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40']
    
    # Loop through each temperature and prepare dataset for plotting
    for i, temp in enumerate(temperatures):
        temp_df = graph_df[graph_df['Temperature'] == temp]
        
        color = colors[i % len(colors)]
        graph_data['temperature_colors'][temp] = color  # Store the color mapping

        dataset = {
            'temperature': temp,
            'data': temp_df[['Development_Time', 'Stage']].to_dict(orient='records'),
            'color': color,
        }
        
        graph_data['datasets'].append(dataset)

    return graph_data

# Helper function to prepare schedule data for Predict Stages page
def prepare_schedule_data(df, temperature_colors, start_datetime=None, desired_time=None):
    schedule_data = []
    if df is None or df.empty:
        return schedule_data

    max_duration = df['Development_Time'].max()

    for index, row in df.iterrows():
        # Determine temperatures and colors
        temp1 = row.get('Temp1') if 'Temp1' in row and pd.notnull(row['Temp1']) else row.get('Temperature')
        temp2 = row.get('Temp2') if 'Temp2' in row and pd.notnull(row['Temp2']) else None

        color1 = temperature_colors.get(temp1)
        color2 = temperature_colors.get(temp2) if temp2 else None

        # Assign 'startTime' and 'collectionTime' based on columns
        startTime = row.get('Start_Time')
        collectionTime = row.get('Exact_Time') or row.get('Collection_Time')


        item = {
            'stage': row['Stage'],
            'startTime': startTime,
            'collectionTime': collectionTime,
            'temperature': temp1,
            'temperature2': temp2,
            'duration': row['Development_Time'],
            'durationPercentage': (row['Development_Time'] / max_duration) * 100,
            'color': color1,
            'color2': color2,
        }

        if 'Exact_Switch_Time' in row and pd.notnull(row['Exact_Switch_Time']):
            item['switchTime'] = row['Exact_Switch_Time']
            # Calculate switch duration percentages
            switch_duration = row['Switch_Times']
            item['switchDurationPercentage'] = (switch_duration / row['Development_Time']) * 100
            item['afterSwitchDurationPercentage'] = 100 - item['switchDurationPercentage']
        else:
            item['switchTime'] = None
            item['switchDurationPercentage'] = None
            item['afterSwitchDurationPercentage'] = None

        schedule_data.append(item)
    return schedule_data

if __name__ == '__main__':
    app.run(debug=True)
