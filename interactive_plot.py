import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
from SLR_PP import get_state_data, PP_df, netCDF_2_pd
from SLR_visualization import migrationSLRMap
from datetime import date
import plotly.graph_objects as go 
app = dash.Dash(__name__)

def load_initial_data(year):
    """Loads or computes data necessary for initializing the app or responding to user input."""
    state_data = get_state_data(year=year)
    slr_data_path = "C:/Users/Omar.khater/Desktop/SLR/data/c3s_obs-sl_glo_phy-ssh_my_twosat-l4-duacs-0.25deg_P1D_multi-vars_101.88W-49.12W_16.12N-51.88N_2021-01-01-2023-06-07.nc"
    SLR_data = netCDF_2_pd(slr_data_path)
    return state_data, SLR_data

def generate_figure(state_data, SLR_data, year, n_days, size_scaling_factor):
    """Generates the figure based on the provided data and parameters."""
    SLR_data_pp = PP_df(SLR_data, 
                        start_day=f'{year}-01-01', 
                        end_day=f'{year}-01-15', 
                        n_days=n_days)
    fig = migrationSLRMap(state_data, 
                          SLR_data_pp, 
                          size_scaling_factor=size_scaling_factor)
    return fig

# Load initial data
initial_year = 2021
state_data_initial, SLR_data_initial = load_initial_data(initial_year)
initial_fig = generate_figure(state_data_initial, SLR_data_initial, initial_year, 1, 10)

app.layout = html.Div([
    html.Div([
        html.Label('Start Date:'),
        dcc.DatePickerSingle(
            id='start-date-picker',
            min_date_allowed=date(2021, 1, 1),
            max_date_allowed=date.today(),
            initial_visible_month=date.today(),
            date=date(2021, 1, 1)  # Example default date
        ),
    ], style={'padding': 10}),
    
    html.Div([
        html.Label('End Date:'),
        dcc.DatePickerSingle(
            id='end-date-picker',
            min_date_allowed=date(1995, 1, 1),
            max_date_allowed=date.today(),
            initial_visible_month=date.today(),
            date=date(2021, 12, 31)  # Example default date
        ),
    ], style={'padding': 10}),
    
    html.Div([
        html.Label('Number of Days (n_days):'),
        dcc.Input(
            id='n-days-input',
            type='number',
            value=30,  # Default value
            min=1, max=365, step=1
        ),
    ], style={'padding': 10}),
    
    html.Button('Update Map', id='update-button', n_clicks=0),
    
    dcc.Graph(id='migration-slr-map')
])

from dateutil import parser

@app.callback(
    Output('migration-slr-map', 'figure'),
    [Input('update-button', 'n_clicks')],
    [State('start-date-picker', 'date'), 
     State('end-date-picker', 'date'),
     State('n-days-input', 'value')]
)
def update_figure(n_clicks, start_date, end_date, n_days):
    if n_clicks > 0:  # Only update the figure if the update button has been clicked
        # Convert start and end dates to tz-naive datetime objects
        start_date = parser.parse(start_date).replace(tzinfo=None)
        end_date = parser.parse(end_date).replace(tzinfo=None)

        # Ensure start_date and end_date are in 'YYYY-MM-DD' format
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')

        # Load data for the selected year
        year = start_date.year
        state_data, SLR_data = load_initial_data(year=year)

        # Generate and return the updated figure
        return generate_figure(state_data, SLR_data, start_date_str, end_date_str, n_days)
    else:
        # Return an empty figure or a default figure before any update action
        return initial_fig


if __name__ == '__main__':
    app.run_server(debug=True)