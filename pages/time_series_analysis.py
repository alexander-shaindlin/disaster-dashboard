import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page config
st.set_page_config(
    page_title="Disaster Time Series Analysis",
    layout="wide"
)

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("public_emdat_2024-10-29.csv")
    return df

df = load_data()

# Title
st.title("Disaster Time Series Analysis")

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

# Region/Country filter
geo_level = st.sidebar.radio(
    "Select Geographic Level",
    options=["Global", "Region", "Country"]
)

if geo_level != "Global":
    geo_options = sorted(df[geo_level].unique())
    selected_geo = st.sidebar.multiselect(
        f"Select {geo_level}s",
        options=geo_options,
        default=[geo_options[0]]
    )

# Disaster type filter
disaster_types = sorted(df['Disaster Type'].unique())
selected_disasters = st.sidebar.multiselect(
    "Select Disaster Types",
    options=disaster_types,
    default=disaster_types[:3]  # Default to first 3 disaster types
)

# Filter data
filtered_df = df[
    (df['Start Year'].between(year_range[0], year_range[1])) &
    (df['Disaster Type'].isin(selected_disasters))
]

if geo_level != "Global":
    filtered_df = filtered_df[filtered_df[geo_level].isin(selected_geo)]

# Annual trends
st.header("Annual Trends")
col1, col2 = st.columns(2)

# Yearly frequency of disasters
yearly_freq = filtered_df.groupby(['Start Year', 'Disaster Type']).size().reset_index(name='Count')

with col1:
    fig1 = px.line(
        yearly_freq,
        x='Start Year',
        y='Count',
        color='Disaster Type',
        title='Disaster Frequency Over Time',
        height=400
    )
    st.plotly_chart(fig1, use_container_width=True)

# Yearly deaths
yearly_deaths = filtered_df.groupby(['Start Year', 'Disaster Type'])['Total Deaths'].sum().reset_index()

with col2:
    fig2 = px.line(
        yearly_deaths,
        x='Start Year',
        y='Total Deaths',
        color='Disaster Type',
        title='Total Deaths Over Time',
        height=400
    )
    st.plotly_chart(fig2, use_container_width=True)

# Monthly patterns
st.header("Monthly Patterns")

# Create monthly distribution
monthly_dist = filtered_df.groupby(['Start Month', 'Disaster Type']).agg({
    'DisNo.': 'count',
    'Total Deaths': 'sum'
}).reset_index()

monthly_dist.columns = ['Month', 'Disaster Type', 'Count', 'Deaths']

# Create two columns for the monthly visualizations
col1, col2 = st.columns(2)

with col1:
    # Frequency by month
    fig3a = px.line(
        monthly_dist,
        x='Month',
        y='Count',
        color='Disaster Type',
        title='Monthly Distribution of Disasters',
        height=400
    )
    fig3a.update_xaxes(
        tickmode='array', 
        ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        tickvals=list(range(1, 13))
    )
    st.plotly_chart(fig3a, use_container_width=True)

with col2:
    # Deaths by month
    fig3b = px.line(
        monthly_dist,
        x='Month',
        y='Deaths',
        color='Disaster Type',
        title='Monthly Distribution of Deaths',
        height=400
    )
    fig3b.update_xaxes(
        tickmode='array', 
        ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        tickvals=list(range(1, 13))
    )
    st.plotly_chart(fig3b, use_container_width=True)

# Add a heatmap view
st.subheader("Monthly Patterns Heatmap")
pivot_monthly = monthly_dist.pivot(
    index='Disaster Type',
    columns='Month',
    values='Count'
).fillna(0)

fig3c = px.imshow(
    pivot_monthly,
    labels=dict(x="Month", y="Disaster Type", color="Count"),
    x=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
       'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
    aspect='auto',
    title='Disaster Frequency Heatmap by Month'
)
st.plotly_chart(fig3c, use_container_width=True)

# Moving averages
st.header("Trend Analysis")

# Calculate 5-year moving averages
yearly_totals = filtered_df.groupby('Start Year').agg({
    'Total Deaths': 'sum',
    'Disaster Type': 'count'
}).reset_index()

yearly_totals['Deaths_MA'] = yearly_totals['Total Deaths'].rolling(window=5).mean()
yearly_totals['Frequency_MA'] = yearly_totals['Disaster Type'].rolling(window=5).mean()

# Create subplot with dual y-axes
fig4 = make_subplots(specs=[[{"secondary_y": True}]])

# Add traces
fig4.add_trace(
    go.Scatter(x=yearly_totals['Start Year'], y=yearly_totals['Deaths_MA'],
               name="Deaths (5-year MA)", line=dict(color='red')),
    secondary_y=True,
)

fig4.add_trace(
    go.Scatter(x=yearly_totals['Start Year'], y=yearly_totals['Frequency_MA'],
               name="Frequency (5-year MA)", line=dict(color='blue')),
    secondary_y=False,
)

# Update layout
fig4.update_layout(
    title='5-Year Moving Averages: Disaster Frequency and Deaths',
    height=500
)

fig4.update_yaxes(title_text="Number of Disasters", secondary_y=False)
fig4.update_yaxes(title_text="Number of Deaths", secondary_y=True)

st.plotly_chart(fig4, use_container_width=True)

# Summary statistics
st.header("Summary Statistics")
col3, col4 = st.columns(2)

with col3:
    st.subheader("Total Disasters by Type")
    disaster_summary = filtered_df['Disaster Type'].value_counts().reset_index()
    disaster_summary.columns = ['Disaster Type', 'Count']
    st.dataframe(disaster_summary)

with col4:
    st.subheader("Total Deaths by Type")
    death_summary = filtered_df.groupby('Disaster Type')['Total Deaths'].sum().reset_index()
    death_summary = death_summary.sort_values('Total Deaths', ascending=False)
    st.dataframe(death_summary)
