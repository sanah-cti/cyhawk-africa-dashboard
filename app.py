import pandas as pd
import streamlit as st

# Load data from CSV
df = pd.read_csv('data/incidents.csv')

# Display data
st.write(df)

