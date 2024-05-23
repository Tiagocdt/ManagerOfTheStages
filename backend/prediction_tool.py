# Main function for the prediction tool
from analysis import calculate_stages, show_duration_for_stages, calculate_backward_from_desired_date
from utils import parse_lab_hours, parse_required_stages, parse_weekday, parse_lab_days, parse_collection_window, parse_start_time, parse_available_temperatures, parse_desired_time, parse_desired_time_window
from data import load_data, prepare_data, create_interpolated_dataset
from config import file_path, stage_times_26C
from plot import plot_development_times 

def prediction_tool():

    # Logic based on the given inputs
    if desired_time_str and start_datetime:
        # Desired time for reaching all stages simultaneously is specified
        print("Desired time specified. Calculating collection times to reach all stages simultaneously.")
        calculate_backward_from_desired_date(required_stages, stage_times_26C, desired_time_str, start_datetime)
    elif start_datetime:
        # Start time is specified but no desired time
        print("Start time specified. Calculating exact times to reach stages at 26°C.")
        calculate_stages(required_stages, stage_times_26C, start_datetime)
    else:
        # Only stages are specified
        print("Only stages specified. Displaying time duration to reach stages at 26°C.")
        show_duration_for_stages(required_stages, file_path, available_temperatures)

    # Logic for calculating the best times to reach the stages
    # This function is yet to be implemented
    # ...

    # Output the converted data
    print("Lab days:", lab_days)
    print("Collection day:", collection_day) 
    if start_datetime:  # Check if a start date is specified
        print(f"Collection day: {start_datetime.strftime('%Y-%m-%d')}, collection time: {collection_time}")
    else:
        print("No collection date specified.")
    print("Lab hours:", lab_start_time, lab_end_time)
    print("Required stages:", required_stages)
