import streamlit as st
import pandas as pd
import plotly.express as px

# Page config
st.set_page_config(
    page_title="Geographic Disaster Analysis",
    layout="wide"
)

# Load data (reuse the same cache function)
@st.cache_data
def load_data():
    df = pd.read_csv("public_emdat_2024-10-29.csv")
    return df

df = load_data()

# Title
st.title("Geographic Disaster Analysis")

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

# Geographic level selector
geo_level = st.sidebar.radio(
    "Select Geographic Level",
    options=["Region", "Country"]
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

# Group data by selected geographic level
geo_column = 'Region' if geo_level == 'Region' else 'Country'

# Calculate metrics by geographic area
geo_metrics = filtered_df.groupby([geo_column, 'Disaster Type']).agg({
    'Total Deaths': 'sum',
    'No. Affected': 'sum'
}).reset_index()

# Add count of disasters
disaster_counts = filtered_df.groupby([geo_column, 'Disaster Type']).size().reset_index(name='Disaster Count')
geo_metrics = geo_metrics.merge(disaster_counts, on=[geo_column, 'Disaster Type'])

# Create visualizations
col1, col2 = st.columns(2)

with col1:
    # Frequency of disasters
    fig1 = px.bar(
        geo_metrics.groupby(geo_column)['Disaster Count'].sum().reset_index(),
        x=geo_column,
        y='Disaster Count',
        title=f'Disaster Frequency by {geo_level}',
        height=500
    )
    fig1.update_xaxes(tickangle=45)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    # Deaths by geographic area
    fig2 = px.bar(
        geo_metrics.groupby(geo_column)['Total Deaths'].sum().reset_index(),
        x=geo_column,
        y='Total Deaths',
        title=f'Total Deaths by {geo_level}',
        height=500
    )
    fig2.update_xaxes(tickangle=45)
    st.plotly_chart(fig2, use_container_width=True)

# Heatmap of disaster types by geographic area
pivot_data = geo_metrics.pivot_table(
    index=geo_column,
    columns='Disaster Type',
    values='Disaster Count',
    fill_value=0
)

fig3 = px.imshow(
    pivot_data,
    title=f'Disaster Type Distribution by {geo_level}',
    aspect='auto',
    height=800
)
st.plotly_chart(fig3, use_container_width=True)

# Detailed metrics table
st.header("Detailed Metrics")
st.dataframe(
    geo_metrics.pivot_table(
        index=geo_column,
        values=['Disaster Count', 'Total Deaths', 'No. Affected'],
        aggfunc='sum'
    ).sort_values('Disaster Count', ascending=False)
) 