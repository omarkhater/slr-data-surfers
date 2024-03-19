import streamlit as st
import pandas as pd
from SLR_PP import get_state_data, PP_df, netCDF_2_pd
from SLR_visualization import migrationSLRMap
from datetime import datetime

def load_initial_data(year):
    """Loads or computes data necessary for initializing the app or responding to user input."""
    state_data = get_state_data(year=year)
    slr_data_path = "C:/Users/Madeline/Downloads/c3s_obs-sl_glo_phy-ssh_my_twosat-l4-duacs-0.25deg_P1D_multi-vars_101.88W-49.12W_16.12N-51.88N_2021-01-01-2023-06-07.nc"
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

st.title("Visualize US Internal Migration Patters Alongside Sea Level Rise")

start_date = st.date_input("Start Date:", datetime(2021, 1, 1), min_value=datetime(2021, 1, 1), max_value=datetime.today())
end_date = st.date_input("End Date:", datetime(2021, 12, 31), min_value=datetime(1995, 1, 1), max_value=datetime.today())
n_days = st.number_input("Number of Days (n_days):", min_value=1, max_value=365, value=30, step=1)

if st.button("Update Map"):
    year = start_date.year
    state_data, SLR_data = load_initial_data(year=year)
    updated_fig = generate_figure(state_data, SLR_data, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), n_days)
    st.plotly_chart(updated_fig)
else:
    st.plotly_chart(initial_fig)