import streamlit as st
from sqlalchemy import create_engine
import pandas as pd
import plotly.express as px
import os
from dotenv import load_dotenv
import plotly.graph_objects as go
from plotly.colors import sample_colorscale

# Set Streamlit layout to wide
st.set_page_config(layout="wide")

load_dotenv()

# Function to connect to the Database
def get_connection():
    try:
        DATABASE_URL = st.secrets["railway_url"]
        engine = create_engine(DATABASE_URL)
        return engine
    except Exception as e:
        st.error(f"Error connecting to the database: {e}")
        return None

# Function to fetch bitcoin prices from Database
def fetch_bitcoin_data(engine):
    try:
        query = "SELECT * FROM gabi_api ORDER BY date"
        df = pd.read_sql_query(query, engine)
        return df
    except Exception as e:
        st.error(f"Error fetching bitcoin data: {e}")
        return pd.DataFrame()

# Function to fetch bitcoin news from Database
def fetch_bitcoin_news(engine):
    try:
        query = "SELECT * FROM gabi_news ORDER BY date"
        df = pd.read_sql_query(query, engine)
        return df
    except Exception as e:
        st.error(f"Error fetching bitcoin news: {e}")
        return pd.DataFrame()

# Get the database connection
conn = get_connection()

# Custom CSS to change background color to very light blue and set header colors
st.markdown(
    """
    <style>
    .main {
        background-color: #e0f7fa;
    }
    .centered-title {
        text-align: center;
        color: #00008b;
    }
    h1 {
        color: orange;
    }
    h2 {
        color: darkblue;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("<h1 class='centered-title'>Gabi's Bitcoin Dashboard</h1>", unsafe_allow_html=True)

# Fetch the bitcoin data and news
bitcoin_prices_df = fetch_bitcoin_data(conn)
bitcoin_news_df = fetch_bitcoin_news(conn)

# Convert date column to datetime format
bitcoin_prices_df['date'] = pd.to_datetime(bitcoin_prices_df['date'])

# Extract month and year from date
bitcoin_prices_df['month'] = bitcoin_prices_df['date'].dt.month
bitcoin_prices_df['year'] = bitcoin_prices_df['date'].dt.year

# Group by month and calculate mean of low, high, close, and open
monthly_data = bitcoin_prices_df.groupby('month').agg({'low': 'mean', 'high': 'mean', 'close': 'mean', 'open':'mean'}).reset_index()

# Create a mapping from month numbers to month names
month_map = {
    1: 'January', 2: 'February', 3: 'March', 4: 'April',
    5: 'May', 6: 'June', 7: 'July', 8: 'August',
    9: 'September', 10: 'October', 11: 'November', 12: 'December'
}

# Apply the mapping to the 'month' column in monthly_data
monthly_data['month'] = monthly_data['month'].map(month_map)

# Dropdown for the dataframe
with st.expander("Data Preview"):
    st.dataframe(bitcoin_prices_df)

# Create start and end date options
col1, col2 = st.columns((2))
bitcoin_prices_df["date"] = pd.to_datetime(bitcoin_prices_df["date"])

# Getting the min and max date
startDate = pd.to_datetime(bitcoin_prices_df["date"]).min()
endDate = pd.to_datetime(bitcoin_prices_df["date"]).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

bitcoin_prices_df = bitcoin_prices_df[(bitcoin_prices_df["date"] >= date1) & (bitcoin_prices_df["date"] <= date2)].copy()

# Create a monthly filter
st.sidebar.header("Choose your filter: ")
month = st.sidebar.multiselect("Pick your Month", bitcoin_prices_df["month"].unique())

filtered_df = bitcoin_prices_df[bitcoin_prices_df["month"].isin(month)] if month else bitcoin_prices_df.copy()
filtered_monthly_data = monthly_data[monthly_data["month"].isin(month_map[m] for m in month)] if month else monthly_data.copy()

# Create a row to display all plots together
row1, row2 = st.columns((2))

# Daily Prices Line Chart
with row1:
    st.subheader('Daily Bitcoin Prices')
    fig1 = px.line(bitcoin_prices_df, x='date', y=['low', 'high', 'close', 'open'], labels={
        'value': 'Price',
        'date': 'Date'
    }, title='Daily Prices')
    fig1.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        title_font=dict(color='orange', size=24)
    )
    st.plotly_chart(fig1, use_container_width=True)

# Monthly Prices Bar Chart
with row2:
    st.subheader('Monthly Average Prices')
    fig2 = px.bar(filtered_monthly_data, x='month', y=['low', 'high', 'close', 'open'], barmode='group')
    fig2.update_layout(
        xaxis_title='Month',
        yaxis_title='Average Price',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        title_font=dict(color='orange', size=24)
    )
    st.plotly_chart(fig2, use_container_width=True)

# Generate a discrete color sequence by sampling the 'Sunset' color scale
sunset_colors = sample_colorscale(px.colors.sequential.Sunset, [i/11 for i in range(12)])

# Pie Chart
with col2:
    st.subheader('Volume wise Bitcoin')
    fig3 = px.pie(filtered_df, values="volume", names="month", hole=0.5, color_discrete_sequence=sunset_colors)
    fig3.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        title_font=dict(color='orange', size=24)
    )
    fig3.update_traces(text=filtered_df["month"], textposition="outside")  # Update text after creating fig3
    st.plotly_chart(fig3, use_container_width=True)
