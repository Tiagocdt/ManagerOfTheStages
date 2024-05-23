import numpy as np
from datetime import timedelta
import pandas as pd

# Function to get the interpolated durations for the required stages and temperatures
def get_interpolated_durations(extended_df, required_stages, available_temperatures):
    if not available_temperatures:
        available_temperatures = [26]  # Default to 26°C if no temperatures are specified

    # Filter the DataFrame for the required stages and at least one matching temperature
    conditions = (
        (extended_df['Temp1'].isin(available_temperatures) | extended_df['Temp2'].isin(available_temperatures)) &
        extended_df['Stage'].isin(required_stages)
    )
    
    durations_df = extended_df[conditions]

    # Check if the DataFrame after filtering is empty
    if durations_df.empty:
        print("No interpolated data available for the specified stages and temperatures.")
        return None
    
    return durations_df

# Function to calculate the collection times for each stage at each available temperature
def calculate_collection_times(extended_df, required_stages, available_temperatures, desired_time):
    
    # Get the interpolated durations for the required stages and temperatures
    filtered_collection_df = get_interpolated_durations(extended_df, required_stages, available_temperatures)
    
    # Check if the DataFrame after filtering is empty
    if filtered_collection_df is None or filtered_collection_df.empty:
        print("No duration data available to calculate collection times.")
        return None
    
    # Calculate collection times by subtracting durations from the desired time
    filtered_collection_df = filtered_collection_df.copy()
    filtered_collection_df.loc[:, 'Collection_Time'] = filtered_collection_df.apply(
    lambda row: desired_time - timedelta(hours=row['Development_Time']), axis=1
    )

    if 'Switch_Times' in filtered_collection_df.columns:
        # Calculate switch time as a timedelta in hours from start_datetime
        filtered_collection_df['Switch_Times'] = filtered_collection_df['Switch_Times'].apply(lambda h: timedelta(hours=h))
        filtered_collection_df['Exact_Switch_Time'] = filtered_collection_df.apply(
            lambda row: row['Collection_Time'] + row['Switch_Times'], axis=1
        )

    return filtered_collection_df

# Function to calculate the exact times for reaching the specified stages at each available temperature
def calculate_exact_times(extended_df, required_stages, available_temperatures, start_datetime):

    # Get the interpolated durations for the required stages and temperatures
    filtered_exacttime_df = get_interpolated_durations(extended_df, required_stages, available_temperatures)
    
    # Check if the DataFrame after filtering is empty
    if filtered_exacttime_df is None or filtered_exacttime_df.empty:
        print("No duration data available to calculate exact times.")
        return None
    
    # Calculate exact times by adding durations to the start datetime
    filtered_exacttime_df = filtered_exacttime_df.copy()
    filtered_exacttime_df['Exact_Time'] = filtered_exacttime_df.apply(
        lambda row: start_datetime + timedelta(hours=row['Development_Time']), axis=1
    )

    # Check if Switch_Times column exists in the DataFrame and if so, calculate exact switch times
    if 'Switch_Times' in filtered_exacttime_df.columns:
        # Calculate switch time as a timedelta in hours from start_datetime
        filtered_exacttime_df['Switch_Times'] = filtered_exacttime_df['Switch_Times'].apply(lambda h: timedelta(hours=h))
        filtered_exacttime_df['Exact_Switch_Time'] = filtered_exacttime_df.apply(
            lambda row: start_datetime + row['Switch_Times'], axis=1
        )
        # Discard the Switch_Times and Switch_Time columns now that they have been used
        #filtered_exacttime_df.drop(columns=['Switch_Times', 'Switch_Time'], inplace=True)

    # Calculate exact times by adding durations to the start datetime
    filtered_exacttime_df['Exact_Time'] = filtered_exacttime_df.apply(
        lambda row: start_datetime + timedelta(hours=row['Development_Time']), axis=1
    )

    return filtered_exacttime_df

def generate_temp_combinations(temps, max_diff=5):
    """
    Generate all pairs of temperatures where the difference is <= max_diff degrees.
    """
    combinations = []
    for t1 in temps:
        for t2 in temps:
            if abs(t1 - t2) <= max_diff and t1 != t2:
                combinations.append((t1, t2))
    return combinations

def calculate_switch_times(df, temps_combinations, required_stages):
    """
    Calculate development times with switching between temperatures at each required stage.
    """
    new_rows = []
    for (t1, t2) in temps_combinations:
        for stage in required_stages:
            for switch_stage in range(0, stage):  # Switch at every stage up to the current required stage
                # Get development time up to the switch stage at t1
                time_at_t1_df = df[(df['Temperature'] == t1) & (df['Stage'] == switch_stage)]
                if not time_at_t1_df.empty:
                    time_at_t1 = time_at_t1_df['Development_Time'].iloc[0]
                else:
                    print(f"No data available for Temperature {t1} at Stage {switch_stage}. Skipping this combination.")
                    continue

                # Get development time for the required stage at t2
                required_stage_t2_df = df[(df['Temperature'] == t2) & (df['Stage'] == stage)]
                if not required_stage_t2_df.empty:
                    required_time_t2 = required_stage_t2_df['Development_Time'].iloc[0]
                else:
                    print(f"No data available for Temperature {t2} at Stage {stage}. Skipping this combination.")
                    continue

                # Get development time for the switch stage at t2
                switch_stage_t2_df = df[(df['Temperature'] == t2) & (df['Stage'] == switch_stage)]
                if not switch_stage_t2_df.empty:
                    switch_time_t2 = switch_stage_t2_df['Development_Time'].iloc[0]
                else:
                    print(f"No data available for Temperature {t2} at Switch Stage {switch_stage}. Using time from t1 instead.")
                    switch_time_t2 = time_at_t1  # Fallback to t1 time if t2 data is missing at switch stage

                # Calculate time after switching
                time_at_t2 = required_time_t2 - switch_time_t2

                new_rows.append({
                    'Stage': stage,
                    'Temp1': t1,
                    'Temp2': t2,
                    'Development_Time': time_at_t1 + time_at_t2,
                    'Switch_Stage': switch_stage,
                    'Switch_Times': time_at_t1, 
                    'Second_Times': time_at_t2
                })

    # Append new rows to the original DataFrame
    new_df = pd.DataFrame(new_rows)
    return pd.concat([df, new_df], ignore_index=True)

def clean_and_filter_df(df):
    # Create the 'Temperature' column based on whether a switch occurs
    # If 'Switch_Stage' is 0, keep only the initial temperature, otherwise show both
    df['Temperature'] = df.apply(
        lambda row: str(row['temp2']) if row['Switch_Stage'] == 0 else f"{row['temp1']} to {row['temp2']}",
        axis=1
    )
    
    # Remove duplicates by considering switched temperatures as equivalent (e.g., 28 to 32 is the same as 32 to 28)
    # Create a sorted string of temperatures for consistent comparison regardless of switch direction
    df['Sorted_Temps'] = df.apply(
        lambda row: ' to '.join(sorted([str(row['temp1']), str(row['temp2'])])),
        axis=1
    )
    
    # Drop duplicates based on 'Sorted_Temps', 'Stage', and 'Development_Time'
    df = df.drop_duplicates(subset=['Sorted_Temps', 'Stage', 'Development_Time'], keep='last')
    
    # Drop the columns used for internal calculations and sorting
    df.drop(columns=['temp1', 'temp2', 'Sorted_Temps'], inplace=True)

    return df


# Function to filter the results DataFrame based on the specified lab days, lab hours, and collection window
def filter_results_by_timing(results_df, lab_days, lab_start_time, lab_end_time, collection_start, collection_end, start_datetime):

   # Put exact_time or collection_time in a variable
    datetime_conversion = results_df[results_df.columns[-2]]

    # create new columns for weekday and time out of the datetime column
    try:
        results_df['weekday_exact'] = datetime_conversion.dt.weekday
        results_df['time_exact'] = datetime_conversion.dt.time
    except AttributeError:
        print("Die Spalte enthält keine datumsähnlichen Werte.")

    # create new columns for weekday and time out of the Switch_Times
    try:
        results_df['weekday_switch'] = results_df['Exact_Switch_Time'].dt.weekday
        results_df['time_switch'] = results_df['Exact_Switch_Time'].dt.time
    except AttributeError:
        print("Die Spalte enthält keine datumsähnlichen Werte.")

    # Use boolean masking directly rather than append to list and pop
    # Initialize the mask with True for all entries, which means all are initially included
    mask = pd.Series(True, index=results_df.index)

    # Apply filter for lab days if provided
    if lab_days:
        mask &= results_df['weekday_exact'].isin(lab_days)
        mask &= results_df['weekday_switch'].isin(lab_days)

    # Apply filter for lab hours if both start and end times are provided
    if lab_start_time and lab_end_time:
        mask &= (results_df['time_exact'] >= lab_start_time) & (results_df['time_exact'] <= lab_end_time)
        mask &= (results_df['time_switch'] >= lab_start_time) & (results_df['time_switch'] <= lab_end_time)

    # Apply filter for collection time window if both start and end times are provided
    if collection_start and collection_end:
        mask &= (results_df['time_exact'] >= collection_start) & (results_df['time_exact'] <= collection_end)

    # Apply filter to ensure the finishing times or collection times are after the start datetime if provided
    if start_datetime:
        if 'Collection_Time' in results_df.columns:
            mask &= (results_df['Collection_Time'] >= start_datetime) 
        if 'Exact_Time' in results_df.columns:
            mask &= (results_df['Exact_Time'] >= start_datetime)
        else:
            print("No exact time or collection time data available to filter by start datetime.")

    # Use the mask to create a filtered DataFrame
    filtered_df = results_df[mask].copy()

    # Clean up DataFrame by dropping temporary columns
    filtered_df.drop(columns=['time_switch', 'time_exact', 'weekday_switch', 'weekday_exact'], inplace=True, errors='ignore')
    
    if filtered_df.empty:
        print("No available times match the specified criteria.")
        return None

    return filtered_df.sort_values(by=['Stage', 'Temperature'], ascending=[True, False])

# Function to suggest the fastest temperature for each stage based on the minimum development time
def suggest_fastest_temperature(df, required_stages):
    if df.empty:
        print("No data available to analyze.")
        return None

    # Group by 'Stage' and find the entry with the minimum 'Development_Time' for each stage
    grouped = df.groupby('Stage')
    fastest_temperatures = grouped.apply(lambda x: x[x['Development_Time'] == x['Development_Time'].min()])

    # Drop duplicate stages if any
    fastest_temperatures = fastest_temperatures.drop_duplicates(subset=['Stage'], keep='first')

    
    # Convert required_stages to set for set operations
    required_stages_set = set(required_stages)
    available_stages = set(fastest_temperatures['Stage'])
    
    # Check if there are any stages missing from the results
    missing_stages = required_stages_set - available_stages
    
    if missing_stages:
        for stage in missing_stages:
            print(f"No available temperature for stage {stage}.")

    return fastest_temperatures.reset_index(drop=True)



    