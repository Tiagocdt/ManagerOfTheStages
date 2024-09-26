# user_handler.py

from datetime import datetime, time

def handle_and_validate_user_input(input_data):
    # Helper functions for validation and parsing

    def validate_species(species):
        if isinstance(species, str) and species.strip():
            return species.strip()
        raise ValueError("Invalid species value.")

    def validate_stages(stages):
        if isinstance(stages, list) and all(isinstance(stage, int) for stage in stages):
            return stages
        raise ValueError("Stages should be a list of integers.")

    def validate_temperatures(temperatures):
        if isinstance(temperatures, list) and all(isinstance(temp, (int, float)) for temp in temperatures):
            return temperatures
        raise ValueError("Temperatures should be a list of numbers.")

    def validate_datetime(datetime_str):
        try:
            return datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
        except (ValueError, TypeError):
            return None  # Return None if datetime_str is None or invalid

    def validate_lab_days(lab_days):
        if isinstance(lab_days, list) and all(isinstance(day, int) and 0 <= day <= 6 for day in lab_days):
            return lab_days
        return []  # Return empty list if lab_days is invalid

    # Function to validate lab start and end times
    def validate_time_string(time_str):
        try:
            if time_str:
                return datetime.strptime(time_str, '%H:%M').strftime('%H:%M')
            return None
        except ValueError:
            return None  # Return None if time_str is invalid

    # Validating and Sanitizing User Input

    required_species = validate_species(input_data.get('required_species'))
    required_stages = validate_stages(input_data.get('required_stages', []))
    available_temperatures = validate_temperatures(input_data.get('available_temperatures', []))

    start_datetime_str = input_data.get('start_datetime')
    start_datetime = validate_datetime(start_datetime_str)

    desired_time_str = input_data.get('desired_time')
    desired_time = validate_datetime(desired_time_str)

    collection_start = validate_time_string(input_data.get('collection_start'))
    collection_end = validate_time_string(input_data.get('collection_end'))

    lab_days = validate_lab_days(input_data.get('lab_days', []))

    lab_start_time = validate_time_string(input_data.get('lab_start_time'))
    lab_end_time = validate_time_string(input_data.get('lab_end_time'))

    return {
        'required_species': required_species,
        'required_stages': required_stages,
        'available_temperatures': available_temperatures,
        'start_datetime': start_datetime,
        'desired_time': desired_time,
        'collection_start': collection_start,
        'collection_end': collection_end,
        'lab_days': lab_days,
        'lab_start_time': lab_start_time,
        'lab_end_time': lab_end_time
    }
