import numpy as np
from datetime import timedelta, time
import pandas as pd

# Function to get the interpolated durations for the required stages and temperatures
def get_interpolated_durations(extended_df, required_stages, available_temperatures):
    """
    Filters the DataFrame for the required stages and temperatures.
    Assumes valid input from the frontend.
    """
    # Filter the DataFrame for the required stages and temperatures
    conditions = (
        (extended_df['Temp1'].isin(available_temperatures) | extended_df['Temp2'].isin(available_temperatures)) &
        extended_df['Stage'].isin(required_stages)
    )
    durations_df = extended_df[conditions]

    if durations_df.empty:
        print("No interpolated data available for the specified stages and temperatures.")
        return None
    
    return durations_df


# Function to calculate the collection times for each stage at each available temperature
def calculate_collection_times(extended_df, required_stages, available_temperatures, desired_time):
    """
    Calculates collection times based on the desired time and available temperatures.
    """
    filtered_collection_df = get_interpolated_durations(extended_df, required_stages, available_temperatures)
    
    if filtered_collection_df is None:
        return None
    
    # Calculate collection times by subtracting durations from the desired time
    filtered_collection_df = filtered_collection_df.copy()
    filtered_collection_df['Collection_Time'] = filtered_collection_df.apply(
        lambda row: desired_time - timedelta(hours=row['Development_Time']), axis=1
    )

    if 'Switch_Times' in filtered_collection_df.columns:
        filtered_collection_df['Switch_Times'] = filtered_collection_df['Switch_Times'].apply(lambda h: timedelta(hours=h))
        filtered_collection_df['Exact_Switch_Time'] = filtered_collection_df.apply(
            lambda row: row['Collection_Time'] + row['Switch_Times'], axis=1
        )

    return filtered_collection_df


# Function to calculate the exact times for reaching the specified stages
def calculate_exact_times(extended_df, required_stages, available_temperatures, start_datetime):
    """
    Calculates exact times based on start date/time and available temperatures.
    """
    filtered_exacttime_df = get_interpolated_durations(extended_df, required_stages, available_temperatures)

    if filtered_exacttime_df is None:
        return None
    
    filtered_exacttime_df = filtered_exacttime_df.copy()
    filtered_exacttime_df['Exact_Time'] = filtered_exacttime_df.apply(
        lambda row: start_datetime + timedelta(hours=row['Development_Time']), axis=1
    )

    if 'Switch_Times' in filtered_exacttime_df.columns:
        filtered_exacttime_df['Switch_Times'] = filtered_exacttime_df['Switch_Times'].apply(lambda h: timedelta(hours=h))
        filtered_exacttime_df['Exact_Switch_Time'] = filtered_exacttime_df.apply(
            lambda row: start_datetime + row['Switch_Times'], axis=1
        )

    return filtered_exacttime_df


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
    """
    Calculate development times for switching between temperatures at different stages.
    """
    new_rows = []
    for (t1, t2) in temps_combinations:
        for stage in required_stages:
            for switch_stage in range(0, stage):
                # Get development time for switch stage at t1
                time_at_t1_df = df[(df['Temperature'] == t1) & (df['Stage'] == switch_stage)]
                if time_at_t1_df.empty:
                    continue
                time_at_t1 = time_at_t1_df['Development_Time'].iloc[0]

                # Get development time for the required stage at t2
                required_stage_t2_df = df[(df['Temperature'] == t2) & (df['Stage'] == stage)]
                if required_stage_t2_df.empty:
                    continue
                required_time_t2 = required_stage_t2_df['Development_Time'].iloc[0]

                # Get development time for the switch stage at t2
                switch_stage_t2_df = df[(df['Temperature'] == t2) & (df['Stage'] == switch_stage)]
                switch_time_t2 = switch_stage_t2_df['Development_Time'].iloc[0] if not switch_stage_t2_df.empty else time_at_t1

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

    return pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)


# Function to filter the results based on lab days, lab hours, and collection window
def filter_results_by_timing(results_df, lab_days, lab_start_time, lab_end_time, collection_start, collection_end, start_datetime, desired_time):
    """
    Filter the results DataFrame based on user availability.
    """
    datetime_conversion = results_df[results_df.columns[-2]]  # Assuming this column holds date-related info
    
    # Extract weekday and time from the datetime column
    results_df['weekday_exact'] = datetime_conversion.dt.weekday
    results_df['time_exact'] = datetime_conversion.dt.time

    if 'Exact_Switch_Time' in results_df.columns:
        results_df['weekday_switch'] = results_df['Exact_Switch_Time'].dt.weekday
        results_df['time_switch'] = results_df['Exact_Switch_Time'].dt.time

    # Initialize mask
    mask = pd.Series(True, index=results_df.index)

    if lab_days:
        mask &= results_df['weekday_exact'].isin(lab_days)
        mask &= results_df.get('weekday_switch', results_df['weekday_exact']).isin(lab_days)

    if lab_start_time and lab_end_time:
        mask &= (results_df['time_exact'] >= lab_start_time) & (results_df['time_exact'] <= lab_end_time)
        mask &= (results_df.get('time_switch', results_df['time_exact']) >= lab_start_time) & (results_df.get('time_switch', results_df['time_exact']) <= lab_end_time)

    if collection_start and collection_end:
        mask &= (results_df['time_exact'] >= collection_start) & (results_df['time_exact'] <= collection_end)

    if start_datetime and not desired_time:
        mask &= (results_df.get('Collection_Time') >= start_datetime)

    
    filtered_df = results_df[mask]

    if filtered_df.empty:
        print("No available times match the specified criteria.")
        return None

    return filtered_df.sort_values(by=['Stage', 'Temperature'], ascending=[True, False])


# Function to suggest the fastest temperature for each stage based on the minimum development time
def suggest_fastest_temperature(df, required_stages):
    """
    Suggest the fastest temperature for each stage based on development time.
    """
    if df.empty:
        print("No data available to analyze.")
        return None

    # Group by 'Stage' and find the entry with the minimum 'Development_Time' for each stage
    fastest_temperatures = df.loc[df.groupby('Stage')['Development_Time'].idxmin()].reset_index(drop=True)

    return fastest_temperatures

# Helper function to convert Timedelta to a string format
def timedelta_to_str(tdelta):
    if tdelta:
        return str(tdelta)  # Convert the Timedelta object to string (e.g., '2:00:00')
    return None

# Convert DataFrame with Timedelta to a serializable format
def convert_df_to_serializable(df):
    """
    Convert a DataFrame to a JSON-serializable format.
    Converts timedelta and time fields into string format.
    """
    df_copy = df.copy()

    # Iterate through each column in the DataFrame
    for col in df_copy.columns:
        if isinstance(df_copy[col].dtype, pd.api.types.DatetimeTZDtype) or pd.api.types.is_datetime64_any_dtype(df_copy[col]):
            df_copy[col] = df_copy[col].dt.strftime('%Y-%m-%d %H:%M:%S')  # Convert datetime fields to string
        elif pd.api.types.is_timedelta64_dtype(df_copy[col]):
            df_copy[col] = df_copy[col].apply(lambda x: str(x))  # Convert timedelta fields to string
        elif df_copy[col].apply(lambda x: isinstance(x, time)).any():
            df_copy[col] = df_copy[col].apply(lambda x: x.strftime('%H:%M:%S') if isinstance(x, time) else x)  # Convert time fields to string

    return df_copy