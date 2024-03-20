import streamlit as st
import pandas as pd
from SLR_PP import load_initial_data
from SLR_visualization import generate_figure
from datetime import datetime

# Load initial data
initial_year = 2021
# slr_data_path= "../data/slr_eastcost_21_23.pkl"
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