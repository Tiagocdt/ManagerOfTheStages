import re
import json
from datetime import datetime, time
import numpy as np
from scipy.interpolate import griddata

# Helper function to convert a weekday string to a number (Monday = 0, ..., Sunday = 6)
def parse_weekday(weekday_str):
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    return days.index(weekday_str)

# Function to parse the user's lab days
def parse_lab_days(lab_days_str):
    # Check if the string is empty and return an empty list in that case
    if not lab_days_str.strip():
        return []
    # Otherwise, execute the original logic
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    return [days.index(day.strip()) for day in lab_days_str.split(',')]

def parse_lab_hours(lab_hours_str):
    if not lab_hours_str.strip():
        return None, None
    try:
        start_hour, end_hour = map(int, re.findall(r'\d+', lab_hours_str))
        return time(start_hour), time(end_hour)
    except ValueError:
        print("The format of the lab hours is invalid. Please provide the hours in the format HH-HH.")
        return None, None
    
def parse_collection_window(collection_window_str):
    if not collection_window_str.strip():
        return None, None  # Return None if no input is provided
    try:
        start_str, end_str = collection_window_str.split("-")
        start = datetime.strptime(start_str, "%H").time()
        end = datetime.strptime(end_str, "%H").time()
        return start, end
    except ValueError:
        print("The format of the collection window is invalid. Please provide the window in the format HH-HH.")
        return None, None

# Function to parse the start time of egg laying
def parse_start_time(start_time_str):
    if not start_time_str.strip():
        return None, None, None
    try:
        start_datetime = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M")
        collection_day = start_datetime.weekday()
        collection_time = start_datetime.time()
        return collection_day, collection_time, start_datetime
    except ValueError:
        print("The format of the start time is invalid. Please use the format YYYY-MM-DD HH:MM.")
        return None, None, None

# Function to parse the required stages
def parse_required_stages(required_stages_str):
    if not required_stages_str.strip():
        return None  # Return None if the input is empty
    try:
        return list(map(int, required_stages_str.split(',')))
    except ValueError:
        return None  # Return None if the input is invalid

# Function to parse the desired time
def parse_desired_time(desired_time_str):
    try:
        # Try to convert the string into a datetime object
        return datetime.strptime(desired_time_str, "%Y-%m-%d %H:%M")
    except ValueError:
        # Print an error message and return None if the format is invalid
        print("The format of the desired time is invalid. Please use the format YYYY-MM-DD HH:MM.")
        return None

def parse_available_temperatures(available_temperatures_str):
    if not available_temperatures_str.strip():
        return []  # No temperatures provided, return an empty list
    try:
        temperatures = [float(temp) for temp in available_temperatures_str.split(',')]
        return temperatures
    except ValueError:
        print("The format of the temperature values is invalid. Please provide the temperatures in degrees Celsius, separated by commas (e.g. 24,26,28).")
        return None

