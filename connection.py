import streamlit as st
from sqlalchemy import create_engine
import pandas as pd
import plotly.express as px
import os
from dotenv import load_dotenv

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

# Custom CSS to change background color to very light blue and font color to dark blue
st.markdown(
    """
    <style>
    .main {
        background-color: #e0f7fa;
    }
    .stApp {
        color: #00008b;
    }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        color: #00008b;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Gabi's Bitcoin Dashboard")

# Fetch the bitcoin data and news
bitcoin_prices_df = fetch_bitcoin_data(conn)
bitcoin_news_df = fetch_bitcoin_news(conn)

st.write(bitcoin_prices_df[['date', 'open', 'high', 'low', 'close', 'volume']])

# Merge prices and news dataframes on the date column
# merged_df = pd.merge(bitcoin_prices_df, bitcoin_news_df, on='date', how='left')

# Convert the date column to datetime format
# merged_df['date'] = pd.to_datetime(merged_df['date'])

# Convert pandas Timestamps to datetime.date
# min_date = merged_df['date'].min().date()
# max_date = merged_df['date'].max().date()

# Sidebar for date selection
# st.sidebar.title("Controls")
# date_range = st.sidebar.slider("Select Date Range", min_date, max_date, (min_date, max_date))

# Filter the dataframe based on the selected date range
# filtered_df = merged_df[(merged_df['date'] >= pd.to_datetime(date_range[0])) & (merged_df['date'] <= pd.to_datetime(date_range[1]))]

# Main Dashboard
