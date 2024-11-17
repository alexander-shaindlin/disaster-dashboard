# app.py
import streamlit as st
import pandas as pd
import plotly.express as px

# Page config
st.set_page_config(
    page_title="Disaster Dashboard",
    layout="wide"
)

# Load data
@st.cache_data
def load_data():
    # Replace this with your actual data file path
    df = pd.read_csv("public_emdat_2024-10-29.csv")
    return df

# Load the data
df = load_data()

# Title
st.title("Global Disaster Analytics")

# Sidebar filters
st.sidebar.header("Filters")

# Year filter
years = sorted(df['Start Year'].unique())
year_range = st.sidebar.slider(
    "Select Years",
    min_value=min(years),
    max_value=max(years),
    value=(min(years), max(years))
)

# Disaster type filter
disaster_types = sorted(df['Disaster Type'].unique())
selected_disasters = st.sidebar.multiselect(
    "Select Disaster Types",
    options=disaster_types,
    default=disaster_types
)

# Filter data
filtered_df = df[
    (df['Start Year'].between(year_range[0], year_range[1])) &
    (df['Disaster Type'].isin(selected_disasters))
]

# Main charts
col1, col2 = st.columns(2)

with col1:
    # Total affected by disaster type
    fig1 = px.bar(
        filtered_df.groupby('Disaster Type')['No. Affected'].sum().reset_index(),
        x='Disaster Type',
        y='No. Affected',
        title='People Affected by Disaster Type'
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    # Deaths by disaster type
    fig2 = px.bar(
        filtered_df.groupby('Disaster Type')['Total Deaths'].sum().reset_index(),
        x='Disaster Type',
        y='Total Deaths',
        title='Deaths by Disaster Type'
    )
    st.plotly_chart(fig2, use_container_width=True)

# Data table
st.header("Detailed Data")
st.dataframe(filtered_df)