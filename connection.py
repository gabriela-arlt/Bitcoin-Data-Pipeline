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
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("<h1 style='color: #00008b;'>Gabi's Bitcoin Dashboard</h1>", unsafe_allow_html=True)

# Fetch the bitcoin data and news
bitcoin_prices_df = fetch_bitcoin_data(conn)
bitcoin_news_df = fetch_bitcoin_news(conn)


# Convert date column to datetime format
bitcoin_prices_df['date'] = pd.to_datetime(bitcoin_prices_df['date'])

# Extract month and year from date
bitcoin_prices_df['year_month'] = bitcoin_prices_df['date'].dt.to_period('M')

# Group by year_month and calculate mean of low, high, and close
monthly_data = bitcoin_prices_df.groupby('year_month').agg({'low': 'mean', 'high': 'mean', 'close': 'mean'}).reset_index()

# Convert year_month to datetime for plotting
monthly_data['year_month'] = monthly_data['year_month'].dt.to_timestamp()

#Dropdown for the dataframe
with st.expander("Data Preview"):
     st.dataframe(bitcoin_prices_df)

# Create a line chart with Plotly Express
fig = px.line(monthly_data, x='year_month', y=['low', 'high', 'close'], labels={
    'value': 'Price',
    'year_month': 'Date'
}, title='Monthly Low, High, and Close Prices for Bitcoin')

# Customize the layout to change the background color
fig.update_layout(
    xaxis_title='Date',
    yaxis_title='Price',
    legend_title='Price Type',
    plot_bgcolor='#add8e6',  # Bright blue background for the plot area
    paper_bgcolor='#add8e6',  # Bright blue background for the entire figure
)

# Customize the line colors
fig.update_traces(line=dict(color='#00008b'))  # Dark blue color for the lines

# Update the line colors individually
fig.for_each_trace(lambda trace: trace.update(line=dict(color={
    'low': '#ff6347',  # Tomato
    'high': '#4682b4',  # SteelBlue
    'close': '#32cd32'  # LimeGreen
}[trace.name])))

# Display the Plotly chart
st.plotly_chart(fig)






