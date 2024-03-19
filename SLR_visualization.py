import plotly.graph_objects as go
import plotly.express as pex
import requests
import pandas as pd
import numpy as np

state_geo = requests.get(
    "https://raw.githubusercontent.com/python-visualization/folium-example-data/main/us_states.json"
).json()

# def migrationSLRMap(state_data: dict, sea_df: pd.DataFrame, size_scaling_factor=10):
#     if sea_df.empty:
#         print("The sea_df DataFrame is empty. Cannot generate the map.")
#         return go.Figure()

#     start_date = sea_df['Time'].min()
#     end_date = sea_df['Time'].max()
#     if pd.isnull(start_date) or pd.isnull(end_date):
#         print("Start date or end date is NaT. Cannot generate the map.")
#         return go.Figure()

#     n_days = infer_n_days(sea_df)
#     title = f'Sea Surface Height (ADT) Rate of Change over {n_days} Days in USA: {start_date.strftime("%Y-%m-%d")} to {end_date.strftime("%Y-%m-%d")}'
#     data_migration = {"States": list(state_data.keys()), "PercentageMigration": list(state_data.values())}
#     migration_df = pd.DataFrame.from_dict(data_migration)
    
#     fig = go.Figure(go.Choropleth(
#         geojson=state_geo,
#         locations=migration_df["States"],
#         z=migration_df["PercentageMigration"],
#         colorscale="Viridis",
#         marker_line_color='white',
#         colorbar_title="Migration Change (%)"
#     ))
    
#     fig.update_geos(fitbounds="locations", visible=False)
#     fig.update_layout(title=title)
    
#     # Vectorized approach to define colors and sizes
#     colors = ['blue' if change > 0 else 'red' for change in sea_df['Rate_of_Change']]
#     sizes = np.maximum(np.abs(sea_df['Rate_of_Change']) * size_scaling_factor, 1)
    
#     # Add a single Scattergeo trace for all points
#     fig.add_trace(go.Scattergeo(
#         lon=sea_df["Longitude"],
#         lat=sea_df["Latitude"],
#         mode='markers',
#         marker=dict(
#             size=sizes,
#             color=colors,
#             line_color='black',
#             line_width=1
#         )
#     ))
    
#     return fig

def migrationSLRMap(state_data: dict, sea_df: pd.DataFrame, size_scaling_factor=10):
    state_geo = requests.get(
        "https://raw.githubusercontent.com/python-visualization/folium-example-data/main/us_states.json"
    ).json()
    if sea_df.empty:
        print("The sea_df DataFrame is empty. Cannot generate the map.")
        return go.Figure()

    start_date = sea_df['Time'].min()
    end_date = sea_df['Time'].max()
    if pd.isnull(start_date) or pd.isnull(end_date):
        print("Start date or end date is NaT. Cannot generate the map.")
        return go.Figure()

    n_days = infer_n_days(sea_df)
    title = f'Sea Surface Height (ADT) Rate of Change over {n_days} Days in USA: {start_date.strftime("%Y-%m-%d")} to {end_date.strftime("%Y-%m-%d")}'
    data_migration = {"States": list(state_data.keys()), "PercentageMigration": list(state_data.values())}
    migration_df = pd.DataFrame.from_dict(data_migration)
    
    fig = go.Figure(go.Choropleth(
        geojson=state_geo,
        locations=migration_df["States"],
        z=migration_df["PercentageMigration"],
        colorscale="Viridis",
        marker_line_color='white',
        colorbar_title="Migration Change (%)"
    ))
    
    # Adjust map layout to focus on the United States
    fig.update_geos(
        visible=False, 
        projection=dict(type="albers usa"),  # This projection is suitable for the US
        lonaxis=dict(range=[-125, -65]),  # Optional: Adjust the longitude range if needed
        lataxis=dict(range=[25, 50])  # Optional: Adjust the latitude range if needed
    )
    fig.update_layout(title=title, geo=dict(bgcolor= 'rgba(0,0,0,0)'))
    
    return fig

def infer_n_days(df):
    """
    Infer the most common difference in days between consecutive time entries
    in the DataFrame for each group of 'Latitude' and 'Longitude'.

    Parameters:
    - df: DataFrame containing the data with 'Time', 'Latitude', and 'Longitude' columns.

    Returns:
    - n_days: The most common time difference in days across the dataset, or None if not applicable.
    """
    # Ensure 'Time' is in datetime format
    df['Time'] = pd.to_datetime(df['Time'])

    # Sort the DataFrame
    df.sort_values(by=['Latitude', 'Longitude', 'Time'], inplace=True)

    # Calculate the difference in days between consecutive entries within each group
    df['Time_Diff'] = df.groupby(['Latitude', 'Longitude'])['Time'].diff().dt.days

    # Find the most common time difference
    mode_series = df['Time_Diff'].mode()
    if not mode_series.empty:
        n_days = mode_series[0]
    else:
        n_days = None  # Or set to a default value if appropriate

    return n_days
