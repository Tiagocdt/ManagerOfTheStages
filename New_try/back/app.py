from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
from user_handler import handle_and_validate_user_input
from db_handler import get_db_connection, fetch_all_data, add_record, prepare_data, create_interpolated_dataset
from analysis import (
    calculate_collection_times, calculate_exact_times, calculate_switch_times, 
    filter_results_by_timing, generate_temp_combinations, get_interpolated_durations, 
    suggest_fastest_temperature, convert_df_to_serializable
)


app = Flask(__name__)
CORS(app)  # Allow CORS so that the frontend can make requests to this API

# Route for predicting stages based on input data
@app.route('/predict', methods=['POST'])
def predict_stages():
    # Get the input data from the request
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

        # Fetch all the data from the database
        data = fetch_all_data()

        # Filter the data by the required species
        if required_species:
            filtered_data = [entry for entry in data if entry['species'] == required_species]
        else:
            return jsonify({"error": "No species provided or species not found"}), 400

        # Process the data as required
        points, values = prepare_data(data)
        interpolated_df = create_interpolated_dataset(points, values, method='rbf')

        # Generate all possible temperature combinations for Switch_Times
        temp_combinations = generate_temp_combinations(available_temperatures)
        extended_df = calculate_switch_times(interpolated_df, temp_combinations, required_stages)

        # Calculate the collection times or exact times based on input
        if desired_time:
            results_df = calculate_collection_times(extended_df, required_stages, available_temperatures, desired_time)
        elif not desired_time and start_datetime:
            results_df = calculate_exact_times(extended_df, required_stages, available_temperatures, start_datetime)
        # If neither desired_time nor start_datetime is provided by the user calculate durations for all stages at all temperatures
        else:
            results_df = get_interpolated_durations(extended_df, required_stages, available_temperatures)

        # Filter results based on lab days and hours
        if start_datetime or collection_start or lab_days or lab_start_time:
            filtered_results_df = filter_results_by_timing(
                results_df, lab_days, lab_start_time, lab_end_time, collection_start, collection_end, start_datetime, desired_time
            )
        else:
            filtered_results_df = results_df

        # Suggest the fastest temperature for incubation
        fastest_temp_df = suggest_fastest_temperature(filtered_results_df, required_stages)

        # Convert DataFrame to JSON-serializable format (handle Timedelta fields)
        serializable_df = convert_df_to_serializable(fastest_temp_df)

        # Return the results as JSON
        return jsonify(serializable_df.to_dict(orient='records')), 200
    
    except ValueError as e:
        # Return an error message if the validation fails
        return jsonify({"error": str(e)}), 400


# Route for entering new data
@app.route('/enter-data', methods=['POST'])
def enter_data():
    # Get the input data from the request
    input_data = request.get_json()
    species = input_data.get('species')
    temperature = input_data.get('temperature')
    stage = input_data.get('stage')
    duration = input_data.get('duration')

    # Add the new data into the SQLite database
    add_record(species, temperature, stage, duration)

    # Return a success message
    return jsonify({'message': 'Data added successfully'})



if __name__ == '__main__':
    app.run(debug=True)
