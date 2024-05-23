from analysis import get_interpolated_durations, calculate_collection_times, calculate_exact_times, filter_results_by_timing, suggest_fastest_temperature

def main_decision_tree(required_stages, available_temperatures, start_datetime, desired_time, collection_start, collection_end, lab_days, lab_start_time, lab_end_time, interpolated_df):
    if not available_temperatures:
        if not start_datetime:
            if not desired_time:
                print("Duration of each stage at 26°C")
                results_df = get_interpolated_durations(interpolated_df, required_stages, available_temperatures)
                print(results_df)
            else: # Desired time is provided
                if not collection_start:
                    if not lab_days and not lab_start_time:
                        print("Collection times for each stage at 26°C")
                        results_df = calculate_collection_times(interpolated_df, required_stages, available_temperatures, desired_time)
                        print(results_df)
                    else: # Lab days are provided
                        print("Collection times for each stage at 26°C and feasibility with user availability")
                        results_df = calculate_collection_times(interpolated_df, required_stages, available_temperatures, desired_time)
                        filtered_df = filter_results_by_timing(results_df, lab_days, lab_start_time, lab_end_time, collection_start, collection_end, start_datetime)
                        print(filtered_df)
                        fastest_temp_df = suggest_fastest_temperature(filtered_df, required_stages)
                        print(fastest_temp_df)
                else: # Collection start is provided
                    if not lab_days and not lab_start_time:
                        print("Collection times for each stage at 26°C and feasibility with specific egg laying time frame")
                        results_df = calculate_collection_times(interpolated_df, required_stages, available_temperatures, desired_time)
                        filtered_df = filter_results_by_timing(results_df, lab_days, lab_start_time, lab_end_time, collection_start, collection_end, start_datetime)
                        print(filtered_df)
                        fastest_temp_df = suggest_fastest_temperature(filtered_df, required_stages)
                        print(fastest_temp_df)
                    else: # Lab days are provided
                        print("Collection times for each stage at 26°C, feasibility with user availability and egg laying time frame")
                        results_df = calculate_collection_times(interpolated_df, required_stages, available_temperatures, desired_time)
                        filtered_df = filter_results_by_timing(results_df, lab_days, lab_start_time, lab_end_time, collection_start, collection_end, start_datetime)
                        print(filtered_df)
                        fastest_temp_df = suggest_fastest_temperature(filtered_df, required_stages)
                        print(fastest_temp_df)
        else: # Start datetime is provided
            if not desired_time:
                if not lab_days and not lab_start_time:
                    print("Exact Date of reaching stages at 26°C")
                    results_df = calculate_exact_times(interpolated_df, required_stages, available_temperatures, start_datetime)
                    print(results_df)
                else: # Lab days are provided
                    print("Exact Date of reaching stages at 26°C and feasibility with user availability")
                    results_df = calculate_exact_times(interpolated_df, required_stages, available_temperatures, start_datetime)
                    filtered_df = filter_results_by_timing(results_df, lab_days, lab_start_time, lab_end_time, collection_start, collection_end, start_datetime)
                    print(filtered_df)
                    fastest_temp_df = suggest_fastest_temperature(filtered_df, required_stages)
                    print(fastest_temp_df)
            else: # Desired time is provided
                if not collection_start:
                    if not lab_days and not lab_start_time:
                        print("Collection times for each stage at 26°C and information about feasibility in time between collection start and end")
                        results_df = calculate_collection_times(interpolated_df, required_stages, available_temperatures, desired_time)
                        filtered_df = filter_results_by_timing(results_df, lab_days, lab_start_time, lab_end_time, collection_start, collection_end, start_datetime)
                        print(filtered_df)
                        fastest_temp_df = suggest_fastest_temperature(filtered_df, required_stages)
                        print(fastest_temp_df)
                    else: # Lab days are provided
                        print("Collection times for each stage at 26°C, feasibility in time between collection start and end and user availability")
                        results_df = calculate_collection_times(interpolated_df, required_stages, available_temperatures, desired_time)
                        filtered_df = filter_results_by_timing(results_df, lab_days, lab_start_time, lab_end_time, collection_start, collection_end, start_datetime)
                        print(filtered_df)
                        fastest_temp_df = suggest_fastest_temperature(filtered_df, required_stages)
                        print(fastest_temp_df)
                else: # Collection start is provided
                    if not lab_days and not lab_start_time:
                        print("Collection times for each stage at 26°C, feasibility in time between collection start and end and egg laying time frame")
                        results_df = calculate_collection_times(interpolated_df, required_stages, available_temperatures, desired_time)
                        filtered_df = filter_results_by_timing(results_df, lab_days, lab_start_time, lab_end_time, collection_start, collection_end, start_datetime)
                        print(filtered_df)
                        fastest_temp_df = suggest_fastest_temperature(filtered_df, required_stages)
                        print(fastest_temp_df)
                    else: # Lab days are provided
                        print("Collection times for each stage at 26°C, feasibility in time between collection start and end, egg laying time frame and user availability")
                        results_df = calculate_collection_times(interpolated_df, required_stages, available_temperatures, desired_time)
                        filtered_df = filter_results_by_timing(results_df, lab_days, lab_start_time, lab_end_time, collection_start, collection_end, start_datetime)
                        print(filtered_df)
                        fastest_temp_df = suggest_fastest_temperature(filtered_df, required_stages)
                        print(fastest_temp_df)
    else:  # Available temperatures other than 26°C
        if not start_datetime:
            if not desired_time:
                print("Duration of each stage at each available temperature")
                results_df = get_interpolated_durations(interpolated_df, required_stages, available_temperatures)
                print(results_df)
            else:  # Desired time is provided
                if not collection_start:
                    if not lab_days and not lab_start_time:
                        print("Latest collection times for each stage at fastest available temperature")
                        results_df = calculate_collection_times(interpolated_df, required_stages, available_temperatures, desired_time)
                        print(results_df)
                    else: # Lab days are provided
                        print("Latest collection times for each stage at fastest available temperatures that fit with user availability if applicable")
                        results_df = calculate_collection_times(interpolated_df, required_stages, available_temperatures, desired_time)
                        filtered_df = filter_results_by_timing(results_df, lab_days, lab_start_time, lab_end_time, collection_start, collection_end, start_datetime)
                        print(filtered_df)
                        fastest_temp_df = suggest_fastest_temperature(filtered_df, required_stages)
                        print(fastest_temp_df)
                else: # Collection start is provided
                    if not lab_days and not lab_start_time:
                        print("Latest collection times for each stage at fastest available temperature also including specific time frame of egg laying")
                        results_df = calculate_collection_times(interpolated_df, required_stages, available_temperatures, desired_time)
                        filtered_df = filter_results_by_timing(results_df, lab_days, lab_start_time, lab_end_time, collection_start, collection_end, start_datetime)
                        print(filtered_df)
                        fastest_temp_df = suggest_fastest_temperature(filtered_df, required_stages)
                        print(fastest_temp_df)
                    else: # Lab days are provided
                        print("Latest collection times for each stage at fastest available temperatures that fit with egg laying time frame and user availability if applicable")
                        results_df = calculate_collection_times(interpolated_df, required_stages, available_temperatures, desired_time)
                        filtered_df = filter_results_by_timing(results_df, lab_days, lab_start_time, lab_end_time, collection_start, collection_end, start_datetime)
                        print(filtered_df)
                        fastest_temp_df = suggest_fastest_temperature(filtered_df, required_stages)
                        print(fastest_temp_df)
        else: # Start datetime is provided
            if not desired_time:
                if not lab_days and not lab_start_time:
                    print("Exact Date of reaching stages at the fastest available temperatures")
                    results_df = calculate_exact_times(interpolated_df, required_stages, available_temperatures, start_datetime)
                    print(results_df)
                    print(lab_start_time)
                else: # Lab days are provided
                    print("Exact Date of reaching stages at the fastest available temperatures which fit with user availability")
                    results_df = calculate_exact_times(interpolated_df, required_stages, available_temperatures, start_datetime)
                    filtered_df = filter_results_by_timing(results_df, lab_days, lab_start_time, lab_end_time, collection_start, collection_end, start_datetime)
                    print(filtered_df)
                    fastest_temp_df = suggest_fastest_temperature(filtered_df, required_stages)
                    print(fastest_temp_df)
            else: # Desired time is provided
                if not collection_start:
                    if not lab_days and not lab_start_time:
                        print("Collection times for each stage at fastest available temperatures and information about feasibility in time between collection start and end")
                        results_df = calculate_collection_times(interpolated_df, required_stages, available_temperatures, desired_time)
                        filtered_df = filter_results_by_timing(results_df, lab_days, lab_start_time, lab_end_time, collection_start, collection_end, start_datetime)
                        print(filtered_df)
                        fastest_temp_df = suggest_fastest_temperature(filtered_df, required_stages)
                        print(fastest_temp_df)
                    else: # Lab days are provided
                        print("Collection times for each stage at fastest available temperatures and information about feasibility in time between collection start and end that fit with user availability if applicable")
                        results_df = calculate_collection_times(interpolated_df, required_stages, available_temperatures, desired_time)
                        filtered_df = filter_results_by_timing(results_df, lab_days, lab_start_time, lab_end_time, collection_start, collection_end, start_datetime)
                        print(filtered_df)
                        fastest_temp_df = suggest_fastest_temperature(filtered_df, required_stages)
                        print(fastest_temp_df)
                else: # Collection start is provided
                    if not lab_days and not lab_start_time:
                        print("Collection times for each stage at fastest available temperatures and information about feasibility in time between collection start and end and including also time frame of egg laying time")
                        results_df = calculate_collection_times(interpolated_df, required_stages, available_temperatures, desired_time)
                        filtered_df = filter_results_by_timing(results_df, lab_days, lab_start_time, lab_end_time, collection_start, collection_end, start_datetime)
                        print(filtered_df)
                        fastest_temp_df = suggest_fastest_temperature(filtered_df, required_stages)
                        print(fastest_temp_df)
                    else: # Lab days are provided
                        print("Collection times for each stage at fastest available temperatures and information about feasibility in time between collection start and end that fit with user availability and egg laying time frame if applicable")
                        results_df = calculate_collection_times(interpolated_df, required_stages, available_temperatures, desired_time)
                        print(results_df)
                        filtered_df = filter_results_by_timing(results_df, lab_days, lab_start_time, lab_end_time, collection_start, collection_end, start_datetime)
                        print(filtered_df)
                        fastest_temp_df = suggest_fastest_temperature(filtered_df, required_stages)
                        print(fastest_temp_df)
                        


