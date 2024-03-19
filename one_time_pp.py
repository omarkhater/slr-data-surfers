import netCDF4
import pickle as pk
import numpy as np
def netCDF_2_pickle(path):
    directory = "/".join(path.split("/")[:-1])
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

    adt = f.variables['adt'][:]
    slr_data = {'latitude': latitude, 
                'longitude': longitude, 
                'time': converted_times, 
                'adt': adt}
    with (open(f"{directory}/slr_eastcost_21_23.pkl", "wb")) as openfile:
        pk.dump(slr_data, openfile)
    return 

def convert_numeric_time_to_datetime64(time, units, calendar):
    # Use netCDF4.num2date to convert numeric time values to datetime objects
    cftime_objs = netCDF4.num2date(time, units=units, calendar=calendar)
    
    # Convert cftime objects to numpy.datetime64 objects
    datetime64_objs = np.array([np.datetime64(date) for date in cftime_objs])
    
    return datetime64_objs
netCDF_2_pickle("../data/c3s_obs-sl_glo_phy-ssh_my_twosat-l4-duacs-0.25deg_P1D_multi-vars_101.88W-49.12W_16.12N-51.88N_2021-01-01-2023-06-07.nc")
