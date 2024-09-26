from flask import Flask, jsonify, request
from flask_cors import CORS
from analysis import calculate_collection_times, calculate_exact_times, calculate_switch_times, filter_results_by_timing, generate_temp_combinations, get_interpolated_durations, suggest_fastest_temperature
from data import add_entree, load_data, prepare_data, create_interpolated_dataset
from plot import plot_development_times

app = Flask(__name__)
CORS(app) # Allow CORS so that the frontend can make requests to this API

# Load the data
file_path = 'Development_Times.json'
data = load_data(file_path)
points, values = prepare_data(data)
interpolated_df = create_interpolated_dataset(points, values, method='rbf')

@app.route('/predict', methods=['POST'])
def predict_stages():
    # Get the input data from the request
    input_data = request.get_json()
    required_stages = input_data.get('required_stages')
    available_temperatures = input_data.get('available_temperatures')
    start_datetime = input_data.get('start_datetime')
    desired_time = input_data.get('desired_time')
    collection_start = input_data.get('collection_start')
    collection_end = input_data.get('collection_end')
    lab_days = input_data.get('lab_days')
    lab_start_time = input_data.get('lab_start_time')
    lab_end_time = input_data.get('lab_end_time')
    # ... (get other input parameters)

    # Call the appropriate functions from your analysis module
    # Generate all possible temperature combinations for Switch_Times
    temp_combinations = generate_temp_combinations(available_temperatures)
    extended_df = calculate_switch_times(interpolated_df, temp_combinations, required_stages)


    # Calculate the collection times based on the inputs
    if desired_time:
        results_df = calculate_collection_times(extended_df, required_stages, available_temperatures, desired_time)
        

    # Calculate the exact times based on the inputs
    elif not desired_time and start_datetime:
        results_df = calculate_exact_times(extended_df, required_stages, available_temperatures, start_datetime)
        

    # If neither desired_time nor start_datetime is provided by the user calculate durations for all stages at all temperatures
    else: 
        results_df = get_interpolated_durations(extended_df, required_stages, available_temperatures)
        
    
    # Filter the results based on the lab days and hours
    if start_datetime or collection_start or lab_days or lab_start_time:
        filtered_results_df = filter_results_by_timing(results_df, lab_days, lab_start_time, lab_end_time, collection_start, collection_end, start_datetime)
        

    fastest_temp_df = suggest_fastest_temperature(filtered_results_df, required_stages)
    # Conduct the decision process
    #results = main_decision_tree(required_stages, available_temperatures, start_datetime, desired_time, collection_start, collection_end, lab_days, lab_start_time, lab_end_time, interpolated_df)

    # Return the results as JSON
    return jsonify(results_df.to_dict(orient='records'))

@app.route('/enter-data', methods=['POST'])
def enter_data():
    # Get the input data from the request
    input_data = request.get_json()
    temperature = input_data.get('temperature')
    stage = input_data.get('stage')
    duration = input_data.get('duration')

    # Call the add_entree function from your data module
    add_entree(file_path, temperature, stage, duration)

    # Return a success message
    return jsonify({'message': 'Data added successfully'})

if __name__ == '__main__':
    app.run(debug=True)