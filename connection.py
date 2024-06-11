import streamlit as st
from sqlalchemy import create_engine
import pandas as pd
import plotly.express as px
import os
from dotenv import load_dotenv
import plotly.graph_objects as go

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
monthly_data = bitcoin_prices_df.groupby('year_month').agg({'low': 'mean', 'high': 'mean', 'close': 'mean', 'open':'mean'}).reset_index()

# Convert year_month to datetime for plotting
monthly_data['year_month'] = monthly_data['year_month'].dt.to_timestamp()



#Dropdown for the dataframe
with st.expander("Data Preview"):
       st.dataframe(bitcoin_prices_df)



#created start and end date options
col1, col2 = st.columns((2))
bitcoin_prices_df["date"]=pd.to_datetime(bitcoin_prices_df["date"])

#getting the min and max date
startDate=pd.to_datetime(bitcoin_prices_df["date"]).min()
endDate=pd.to_datetime(bitcoin_prices_df["date"]).max()

with col1:
    date1=pd.to_datetime(st.date_input("Start Date", startDate))

with col2:
    date2=pd.to_datetime(st.date_input("End Date", endDate))

bitcoin_prices_df=bitcoin_prices_df[(bitcoin_prices_df["date"]>=date1) & (bitcoin_prices_df["date"]<=date2)].copy()


# Create a line chart with Plotly Expres daily
fig = px.line(bitcoin_prices_df, x='date', y=['low', 'high', 'close','open'], labels={
       'value': 'Price',
       'date': 'Date'
      }, title='DailyPrices for Bitcoin')




# Create a line chart with Plotly Express
fig = px.line(monthly_data, x='year_month', y=['low', 'high', 'close','open'], labels={
       'value': 'Price',
       'year_month': 'Date'
      }, title='Monthly Low, High, and Close Prices for Bitcoin')

# Customize the layout to change the background color
fig.update_layout(
    xaxis_title='Date',
    yaxis_title='Price',
    legend_title='Price Type',
    plot_bgcolor='#e0f7fa',  # Bright blue background for the plot area
    paper_bgcolor='#e0f7fa',  # Bright blue background for the entire figure
    title_font={'color': '#00008b'} # Dark blue color for the title
  )


# Customize the line colors
#fig.update_traces(line=dict(color='#00008b'))  # Dark blue color for the lines

# Define colors and widths for each line
colors = {
    'low': '#ff1397',  # purple
    'high': '#c0b1ff',  # pink
    'close': '#FFFF00',  # yellow
    'open': '#a4f506' # green
  }

widths = {
    'low': 2,  # Width for low line
    'high': 8,  # Width for high line
    'close': 3,  # Width for close line
    'open' : 3
  }

# Update the line colors and widths individually
fig.for_each_trace(
    lambda trace: trace.update(
        line=dict(color=colors[trace.name], width=widths[trace.name])
    )
  )
# Display the Plotly chart
st.plotly_chart(fig, use_container_width=True)


# Create a line chart with Plotly Express
fig = px.line(, x='year_month', y=['low', 'high', 'close','open'], labels={
       'value': 'Price',
       'year_month': 'Date'
      }, title='Monthly Low, High, and Close Prices for Bitcoin')
