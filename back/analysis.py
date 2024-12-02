# analysis.py

import numpy as np
import pandas as pd
from datetime import timedelta, datetime, time

# Function to get the interpolated durations for the required stages and temperatures
def get_interpolated_durations(df, required_stages, available_temperatures):
    """
    Filters the DataFrame for the required stages and temperatures.
    Assumes valid input from the frontend.
    """
    # Filter the DataFrame for the required stages and temperatures
    conditions = (
        (df['Temperature'].isin(available_temperatures)) &
        (df['Stage'].isin(required_stages))
    )
    durations_df = df[conditions]

    if durations_df.empty:
        print("No interpolated data available for the specified stages and temperatures.")
        return None

    return durations_df


# Function to calculate the collection times for each stage at each available temperature
def calculate_start_times(extended_df, required_stages, available_temperatures, desired_time):
    """
    Calculates collection times based on the desired time and available temperatures.
    """
    filtered_start_df = get_interpolated_durations(extended_df, required_stages, available_temperatures)

    if filtered_start_df is None:
        return None

    # Calculate collection times by subtracting durations from the desired time
    filtered_start_df = filtered_start_df.copy()

    # 'Collection_Time' is the desired time provided by the user
    filtered_start_df['End_Time'] = desired_time

    filtered_start_df['Start_Time'] = filtered_start_df.apply(
        lambda row: desired_time - timedelta(hours=row['Development_Time']), axis=1
    )
    if 'Switch_Times' in filtered_start_df.columns:
        filtered_start_df['Exact_Switch_Time'] = filtered_start_df.apply(
            lambda row: row['Start_Time'] + timedelta(hours=row['Switch_Times']) if pd.notnull(row['Switch_Times']) else np.nan, axis=1
        )

    return filtered_start_df


# Function to calculate the exact times for reaching the specified stages
def calculate_end_times(extended_df, required_stages, available_temperatures, start_datetime):
    """
    Calculates exact times based on start date/time and available temperatures.
    """
    filtered_end_df = get_interpolated_durations(extended_df, required_stages, available_temperatures)

    if filtered_end_df is None:
        return None

    # Calculate exact times by adding durations to the start date/time
    filtered_end_df = filtered_end_df.copy()
    filtered_end_df['End_Time'] = filtered_end_df.apply(
        lambda row: start_datetime + timedelta(hours=row['Development_Time']), axis=1
    )

    # Set 'Start_Time' to the provided start time
    filtered_end_df['Start_Time'] = start_datetime

    # Calculate 'Exact_Switch_Time' only where 'Switch_Times' is not NaN
    if 'Switch_Times' in filtered_end_df.columns:
        filtered_end_df['Exact_Switch_Time'] = filtered_end_df.apply(
            lambda row: start_datetime + timedelta(hours=row['Switch_Times']) if pd.notnull(row['Switch_Times']) else np.nan, axis=1
        )



    return filtered_end_df


# Function to generate all pairs of temperatures where the difference is <= max_diff degrees
def generate_temp_combinations(temps, max_diff=5):
    """
    Generate all pairs of temperatures with a difference <= max_diff.
    """
    combinations = []
    for t1 in temps:
        for t2 in temps:
            if abs(t1 - t2) <= max_diff and t1 != t2:
                combinations.append((t1, t2))
    return combinations


# Function to calculate development times with switching between temperatures
def calculate_switch_times(df, temps_combinations, required_stages):
    new_rows = []
    df['Temperature'] = df['Temperature'].astype(float)
    df['Stage'] = df['Stage'].astype(int)  # Ensure stages are integers

    for (t1, t2) in temps_combinations:
        for stage in required_stages:
            for switch_stage in range(0, stage):
                # Get development time for switch stage at t1
                time_at_t1_df = df[(np.isclose(df['Temperature'], t1)) & (df['Stage'] == switch_stage)]
                if time_at_t1_df.empty:
                    continue
                time_at_t1 = time_at_t1_df['Development_Time'].iloc[0]

                # Get development time for the required stage at t2
                required_stage_t2_df = df[(np.isclose(df['Temperature'], t2)) & (df['Stage'] == stage)]
                if required_stage_t2_df.empty:
                    continue
                required_time_t2 = required_stage_t2_df['Development_Time'].iloc[0]

                # Get development time for the switch stage at t2
                switch_stage_t2_df = df[(np.isclose(df['Temperature'], t2)) & (df['Stage'] == switch_stage)]
                if switch_stage_t2_df.empty:
                    continue
                switch_time_t2 = switch_stage_t2_df['Development_Time'].iloc[0]

                # Calculate time after switching
                time_at_t2 = required_time_t2 - switch_time_t2

                new_rows.append({
                    'Switch': True,
                    'Stage': stage,
                    'Temperature': t1,
                    'Temp1': t1,
                    'Temp2': t2,
                    'Development_Time': time_at_t1 + time_at_t2,
                    'Switch_Stage': switch_stage,
                    'Switch_Times': time_at_t1,
                })

    # Create a DataFrame from the new rows
    new_df = pd.DataFrame(new_rows)

    # Combine the original DataFrame with the new DataFrame
    extended_df = pd.concat([df, new_df], ignore_index=True, sort=False)

    return extended_df

def filter_results_by_timing(results_df, lab_days, lab_start_time, lab_end_time, collection_start, collection_end, start_datetime, desired_time):
    """
    Filter the results DataFrame based on user availability.
    """
    if results_df is None or results_df.empty:
        return None

    results_df = results_df.copy()

    datetime_column = 'End_Time' if start_datetime else 'Start_Time'
    results_df[datetime_column] = pd.to_datetime(results_df[datetime_column])

    # Extract weekday and time from the datetime column
    results_df['weekday_exact'] = results_df[datetime_column].dt.weekday
    results_df['time_exact'] = results_df[datetime_column].dt.time

    # Check if 'Exact_Switch_Time' exists and is not all NaN
    if 'Exact_Switch_Time' in results_df.columns and results_df['Exact_Switch_Time'].notnull().any():
        results_df['Exact_Switch_Time'] = pd.to_datetime(results_df['Exact_Switch_Time'])
        results_df['weekday_switch'] = results_df['Exact_Switch_Time'].dt.weekday
        results_df['time_switch'] = results_df['Exact_Switch_Time'].dt.time
    else:
        # If there are no valid switch times, remove these columns to avoid confusion
        results_df = results_df.drop(columns=['Exact_Switch_Time'], errors='ignore')

    # Initialize mask
    mask = pd.Series(True, index=results_df.index)

    if lab_days:
        mask &= results_df['weekday_exact'].isin(lab_days)
        if 'weekday_switch' in results_df.columns:
            switch_mask = results_df['Exact_Switch_Time'].notnull()
            # For rows with switch times, apply the filter; else, don't alter the mask
            mask &= (~switch_mask) | (results_df['weekday_switch'].isin(lab_days))

    if lab_start_time and lab_end_time:
        lab_start_time_obj = datetime.strptime(lab_start_time, '%H:%M').time()
        lab_end_time_obj = datetime.strptime(lab_end_time, '%H:%M').time()
        mask &= results_df['time_exact'].between(lab_start_time_obj, lab_end_time_obj)
        if 'time_switch' in results_df.columns:
            switch_mask = results_df['Exact_Switch_Time'].notnull()
            mask &= (~switch_mask) | results_df['time_switch'].between(lab_start_time_obj, lab_end_time_obj)

    if collection_start and collection_end:
        collection_start_time = datetime.strptime(collection_start, '%H:%M').time()
        collection_end_time = datetime.strptime(collection_end, '%H:%M').time()
        mask &= results_df['time_exact'].between(collection_start_time, collection_end_time)

    filtered_df = results_df[mask]

    if filtered_df.empty:
        print("No available times match the specified criteria.")
        return None

    return filtered_df.sort_values(by=['Stage', 'Development_Time'], ascending=[True, True])


# Function to suggest the fastest temperature for each stage based on the minimum development time
def suggest_fastest_temperature(df, required_stages):
    """
    Suggest the fastest temperature for each stage based on development time,
    preferring schedules without temperature switches.
    """
    if df.empty:
        print("No data available to analyze.")
        return None

    fastest_entries = []  # List to collect fastest entries

    for stage in required_stages:
        stage_df = df[df['Stage'] == stage]
        if stage_df.empty:
            continue

        # Prefer non-switch schedules
        non_switch_df = stage_df[stage_df['Switch'] == False]
        if not non_switch_df.empty:
            fastest = non_switch_df.loc[non_switch_df['Development_Time'].idxmin()]
        else:
            fastest = stage_df.loc[stage_df['Development_Time'].idxmin()]

        fastest_entries.append(fastest)

    # Create a DataFrame from the list of fastest entries
    fastest_temperatures = pd.DataFrame(fastest_entries).reset_index(drop=True)

    return fastest_temperatures

# Convert DataFrame with Timedelta to a serializable format
def convert_df_to_serializable(df):
    """
    Convert a DataFrame to a JSON-serializable format.
    Converts datetime and timedelta fields into string format.
    """
    df_copy = df.copy()
    date_format = '%a %d.%m %H:%M'  # Format: weekday dd.mm HH:mm

    # Iterate through each column in the DataFrame
    for col in df_copy.columns:
        if pd.api.types.is_datetime64_any_dtype(df_copy[col]):
            df_copy[col] = df_copy[col].dt.strftime('%Y-%m-%d %H:%M:%S')
        elif pd.api.types.is_timedelta64_dtype(df_copy[col]):
            df_copy[col] = df_copy[col].apply(lambda x: str(x))
        elif df_copy[col].apply(lambda x: isinstance(x, time)).any():
            df_copy[col] = df_copy[col].apply(lambda x: x.strftime('%H:%M') if isinstance(x, time) else x)

    return df_copy
