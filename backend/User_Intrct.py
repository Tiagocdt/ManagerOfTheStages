from datetime import datetime
from utils import parse_required_stages, parse_start_time, parse_lab_days, parse_lab_hours, parse_collection_window, parse_desired_time, parse_available_temperatures

# Functions to collect user input for the prediction tool
def get_required_stages():
    while True:
        required_stages_str = input("Which stages do you need? (Numbers separated by commas, e.g. 5,10,15): ")
        required_stages = parse_required_stages(required_stages_str)
        if required_stages is not None:
            return required_stages
        print("Please provide at least one valid stage. The format is invalid or the input was empty.")

def get_available_temperatures():
    available_temperatures_str = input("Please provide the available temperatures (in degrees Celsius, separated by commas, e.g. 24,26,28) or leave it blank: ")
    return parse_available_temperatures(available_temperatures_str)

def get_start_datetime():
    while True:
        start_time_str = input("Please provide the exact date and time of egg collection (YYYY-MM-DD HH:MM) or leave it blank: ")
        if start_time_str.strip():  # Check if the input is not empty
            start_datetime = parse_start_time(start_time_str)[2]
            if start_datetime is not None:
                return start_datetime
            print("The format of the start time is invalid. Please use the format YYYY-MM-DD HH:MM.")
        else:
            return None  # Allow leaving the field blank

def get_desired_time():
    desired_time_str = input("Please provide the desired date and time when all stages should be reached simultaneously (YYYY-MM-DD HH:MM) or leave it blank: ")
    if desired_time_str.strip():  # Check if the input is not empty
        return parse_desired_time(desired_time_str)
    return None

def get_collection_window():
    collection_window_str = input("Is there a specific time window for egg collection? (e.g. 10-11) or leave it blank: ")
    return parse_collection_window(collection_window_str)

def get_lab_days():
    lab_days_str = input("On which days of the week are you in the laboratory? (e.g. Mon,Tue,Wed,Thu,Fri) or leave it blank: ")
    return parse_lab_days(lab_days_str)
        
def get_lab_hours():
    lab_hours_str = input("During which time range are you in the laboratory daily? (e.g. 9-18) or leave it blank: ")
    lab_start_time, lab_end_time = parse_lab_hours(lab_hours_str)
    return lab_start_time, lab_end_time
    
