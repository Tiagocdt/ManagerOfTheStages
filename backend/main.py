from analysis import calculate_collection_times, calculate_exact_times, calculate_switch_times, filter_results_by_timing, generate_temp_combinations, get_interpolated_durations, suggest_fastest_temperature
from plot import plot_development_times
from data import add_entree, create_interpolated_dataset, load_data, prepare_data
from decision_tree import main_decision_tree
from utils import parse_available_temperatures, parse_collection_window, parse_desired_time, parse_lab_days, parse_lab_hours, parse_required_stages, parse_start_time
from User_Intrct import get_available_temperatures, get_collection_window, get_desired_time, get_lab_days, get_lab_hours, get_required_stages, get_start_datetime
file_path = 'Development_Times.json'

def main(action=None, entry_action = None, required_stages_str=None, available_temperatures_str=None, start_time_str=None, desired_time_str=None, collection_window_str=None, lab_days_str=None, lab_hours_str=None):
    if action is None:
        action = input("Do you want to 'predict Medaka stages' or 'enter data'? (predict/enter): ")
    
    if action.lower() == "enter":
        if entry_action is None:
            entry_action = input("Do you want to enter 'a single entry' or 'multiple entries'? (single/multiple): ")
        if entry_action.lower() == "single":
            temperature = input("Temperature: ")
            stage = input("Stage: ")
            duration_str = input("Enter duration in format DD:HH:MM: ")
            days, hours, minutes = map(int, duration_str.split(':'))
            duration_in_hpf = days * 24 + hours + minutes / 60
            add_entree(file_path, temperature, stage, duration_in_hpf)
        elif entry_action.lower() == "multiple":
            development_data = input("Enter multiple development data (Format: 'Temperature,Stage,Duration; Temperature,Stage,Duration; ...'): ")
            development_data_list = development_data.split(";")
            for data_entry in development_data_list:
                data = data_entry.strip().split(",")
                if len(data) == 3:
                    temperature, stage, time_str = data
                    days, hours, minutes = map(int, time_str.split(':'))
                    duration_in_hpf = days * 24 + hours + minutes / 60
                    add_entree(file_path, temperature.strip(), stage.strip(), duration_in_hpf)
                else:
                    print("Skipped invalid data entry:", data_entry)

    elif action.lower() == "predict":
        # Prepare inputs either from parameters or from user input if not provided
        required_stages = parse_required_stages(required_stages_str) if required_stages_str else get_required_stages()
        available_temperatures = parse_available_temperatures(available_temperatures_str) if available_temperatures_str else get_available_temperatures()
        start_datetime = parse_start_time(start_time_str)[2] if start_time_str else get_start_datetime()
        desired_time = parse_desired_time(desired_time_str) if desired_time_str else get_desired_time()
        collection_start = collection_end = None    
        if desired_time:
            collection_start, collection_end = parse_collection_window(collection_window_str) if collection_window_str else get_collection_window()
        lab_days = parse_lab_days(lab_days_str) if lab_days_str else get_lab_days()
        lab_start_time, lab_end_time = parse_lab_hours(lab_hours_str) if lab_hours_str else get_lab_hours()

        # Load and prepare data
        data = load_data(file_path)
        points, values = prepare_data(data)
        
        # Create interpolated dataset
        interpolated_df = create_interpolated_dataset(points, values, method='rbf')
        print("interpolated_df")
        print(interpolated_df)

        plot_development_times(interpolated_df, available_temperatures, points, values)

        # Generate all possible temperature combinations
        temp_combinations = generate_temp_combinations(available_temperatures)
        extended_df = calculate_switch_times(interpolated_df, temp_combinations, required_stages)
        print("extended_df")
        print(extended_df)

        # Calculate the collection times based on the inputs
        if desired_time:
            results_df = calculate_collection_times(extended_df, required_stages, available_temperatures, desired_time)
            print("results_df")
            print(results_df)

        # Calculate the exact times based on the inputs
        elif not desired_time and start_datetime:
            results_df = calculate_exact_times(extended_df, required_stages, available_temperatures, start_datetime)
            print("results_df")
            print(results_df)

        # If neither desired_time nor start_datetime is provided by the user calculate durations for all stages at all temperatures
        else: 
            results_df = get_interpolated_durations(extended_df, required_stages, available_temperatures)
            print("results_df")
            print(results_df)
        
        # Filter the results based on the lab days and hours
        if start_datetime or collection_start or lab_days or lab_start_time:
            filtered_results_df = filter_results_by_timing(results_df, lab_days, lab_start_time, lab_end_time, collection_start, collection_end, start_datetime)
            print("filtered_results_df")
            print(filtered_results_df)

        fastest_temp_df = suggest_fastest_temperature(filtered_results_df, required_stages)
        print("fastest_temp_df")
        print(fastest_temp_df)
        # Conduct the decision process
        #results = main_decision_tree(required_stages, available_temperatures, start_datetime, desired_time, collection_start, collection_end, lab_days, lab_start_time, lab_end_time, interpolated_df)

    else:
        print("Unknown action. Please choose 'predict' or 'enter'.")

if __name__ == "__main__":
    main('predict', None, '39,23,40,32,10,15', '18,20,26,28,32', '2024-02-22 10:00', '2024-03-04 15:00', '', 'Mon,Tue,Wed,Thu,Fri', '9-18')

#'predict', None, '10,20,30,40,32,12,15,18', '18,20,26,28,32', '2024-05-08 10:00', '2024-05-13 10:00', '9-11', 'Mon,Tue,Wed,Thu,Fri', '9-16'

#'predict', None, '10,20,30,40', '18,26,28,32', '2024-03-04 10:00', '2024-03-07 10:00', '10-11', 'Mon,Tue,Wed,Thu,Fri', '9-18'

#'predict', None, None, '10,20,30,40', '18,20,24,26,28,30,32', '2024-03-04 10:00', '2024-03-07 10:00', '10-11', 'Mon,Tue,Wed,Thu,Fri', '9-18'