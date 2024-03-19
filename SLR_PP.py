import netCDF4
import pandas as pd
import numpy as np

def netCDF_2_pd(path):
    f = netCDF4.Dataset(path)
    latitude = f.variables['latitude'][:]
    longitude = f.variables['longitude'][:]
    time = f.variables['time'][:]  # This is likely in a numeric format representing dates

    # Convert numeric time to datetime
    # This depends on the 'units' and 'calendar' attributes of the time variable
    time_units = f.variables['time'].units
    time_calendar = f.variables['time'].calendar if hasattr(f.variables['time'], 'calendar') else 'standard'
    time_datetimes = netCDF4.num2date(time, units=time_units, calendar=time_calendar)
    time_units = f.variables['time'].units
    try:
        calendar = f.variables['time'].calendar
    except AttributeError:  # In case the 'calendar' attribute is missing
        calendar = 'gregorian'  # or 'standard', choose a default


    # Convert your numeric time values to numpy.datetime64 objects
    converted_times = convert_numeric_time_to_datetime64(time, time_units, calendar)

    # Since your dataset likely represents a 2D grid of points over multiple times, 
    # we'll need to repeat the time array to match the number of latitude and longitude points
    time_repeated = np.repeat(converted_times, latitude.size * longitude.size)

    # Create a meshgrid for latitude and longitude, then flatten them for the DataFrame
    lon, lat = np.meshgrid(longitude, latitude)
    lon_flat = lon.flatten()
    lat_flat = lat.flatten()

    # Repeat latitude and longitude coordinates for each time step
    lat_repeated = np.tile(lat_flat, len(time_datetimes))
    lon_repeated = np.tile(lon_flat, len(time_datetimes))

    adt = f.variables['adt'][:]
    adt_flat = adt.flatten().data  # Or another method to match DataFrame's structure

    # Now combine everything into a DataFrame
    df = pd.DataFrame({
        'Time': time_repeated,
        'Latitude': lat_repeated,
        'Longitude': lon_repeated, 
        'adt': adt_flat,
    })
    return df


def PP_df(df, start_day, end_day, n_days=1):
    """
    Process a DataFrame to select data between start and end days, calculate the rate of change in 'adt'
    values over a specified number of days, and return a row entry every n days.
    
    Parameters:
    - df: DataFrame containing the data.
    - start_day: The start day for selecting the data in YYYY-MM-DD format.
    - end_day: The end day for selecting the data in YYYY-MM-DD format.
    - n_days: The number of days over which to calculate the difference in 'adt' values. Defaults to 1.
    
    Returns:
    - A DataFrame with the rate of change calculated over the specified number of days, with an entry every n days.
    """
    start_day = pd.to_datetime(start_day)
    end_day = pd.to_datetime(end_day)
    # Filter out land data and select data between start_day and end_day
    sea_df = df[(df['adt'] > -2.147484e+07) & (df['Time'] >= start_day) & (df['Time'] <= end_day)]
    sea_df['Time'] = pd.to_datetime(sea_df['Time'])
    sea_df.sort_values(by=['Latitude', 'Longitude', 'Time'], inplace=True)
    
    # Calculate the difference in 'adt' values over n_days
    sea_df['Rate_of_Change'] = sea_df.groupby(['Latitude', 'Longitude'])['adt'].diff(periods=n_days)
    
    # Instead of dropping NaNs, filter to include every n-th day's data
    # This is achieved by resetting the index within each group and then filtering
    sea_df = sea_df.groupby(['Latitude', 'Longitude']).apply(lambda x: x.iloc[n_days-1::n_days]).reset_index(drop=True)
    sea_df.fillna(0, inplace=True)
    return sea_df

def convert_numeric_time_to_datetime64(time, units, calendar):
    # Use netCDF4.num2date to convert numeric time values to datetime objects
    cftime_objs = netCDF4.num2date(time, units=units, calendar=calendar)
    
    # Convert cftime objects to numpy.datetime64 objects
    datetime64_objs = np.array([np.datetime64(date) for date in cftime_objs])
    
    return datetime64_objs

def get_migration_data(csv_link_outflow, csv_link_inflow):
    prop_migration_by_state = {}

    outflowData = pd.read_csv(csv_link_outflow)
    inflowData = pd.read_csv(csv_link_inflow)

    outflowStates_dfs = {}
    inflowStates_dfs = {}

    for state in outflowData['y2_state'].unique():
        if state not in ['DC', 'FR']:
            #create new df for state
            outflowStates_dfs[state] = outflowData[outflowData['y2_state'] == state].copy()
            inflowStates_dfs[state] = inflowData[inflowData['y1_state'] == state].copy()

            #calculate total pop
            total_pop = 0
            matching_rows = outflowStates_dfs[state][outflowStates_dfs[state]['y2_state_name'].str.contains('Non-migrants|Migration-Same|Migration-US')]
            total_pop = matching_rows['n1'].sum() + matching_rows['n2'].sum()
            #calculate total leaving
            leaving = 0
            non_matching_rows = outflowStates_dfs[state][~outflowStates_dfs[state]['y2_state_name'].str.contains('Non-migrants|Migration-Same|Migration-US')]
            leaving = non_matching_rows['n1'].sum() + non_matching_rows['n2'].sum()
            #calculate total incoming
            incoming = 0
            non_matching_rows = inflowStates_dfs[state][~inflowStates_dfs[state]['y1_state_name'].str.contains('Non-migrants|Migration-Same|Migration-US')]
            incoming = non_matching_rows['n1'].sum() + non_matching_rows['n2'].sum()

            #calculate prop and standardize outliers
            #   (-100) im not sure why but the proportions ended up negative based on my calculations in R and outside research regarding US state migration
            #          so im multiplying by -100 instead of 100
            #          ex. California has a negative population change from 2020-2021 but without the -100 it's proportion ends up positive 0.98
            prop = ((incoming - leaving) / total_pop) * -100
            #add to dictionary
            prop_migration_by_state[state] = prop

    return prop_migration_by_state


def get_state_data(year, 
                   path_to_csv = "C:/Users/Omar.khater/Desktop/SLR/New folder/copy_migr_urls - Sheet1.csv"):
    """
    Retrieve state data for a specified year based on inflow and outflow information.
    
    Parameters:
    - year: The year for which to retrieve the data.
    - path_to_csv: Path to a CSV file containing 'start_year', 'end_year', 'inflow', and 'outflow'.
    
    Returns:
    - A dictionary with values for each state if the year is within available ranges, None otherwise.
    """
    # Read the CSV file
    df = pd.read_csv(path_to_csv)
    
    # Find the row(s) that include the specified year
    relevant_rows = df[(df['start_year'] <= year) & (df['end_year'] >= year)]
    
    if relevant_rows.empty:
        print("No data available for the specified year.")
        return None
    
    # Assuming the CSV is structured such that there will only be one matching row for each year
    row = relevant_rows.iloc[0]
    
    # Use the inflow and outflow links (file paths) to get the migration data
    state_data = get_migration_data(row['outflow'], row['inflow'])
    
    return state_data
