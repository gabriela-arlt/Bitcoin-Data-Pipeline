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

import streamlit as st

# Custom CSS to change background color to very light blue and font color to dark blue
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


# Group by year_month and calculate mean of low, high, and close
monthly_data = bitcoin_prices_df.groupby('month').agg({'low': 'mean', 'high': 'mean', 'close': 'mean', 'open':'mean'}).reset_index()



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




#create a monthly filter
st.sidebar.header("Choose your filter: ")
month = st.sidebar.multiselect("Pick your Month", bitcoin_prices_df["month"].unique())

filtered_df = bitcoin_prices_df[bitcoin_prices_df["month"].isin(month)] if month else bitcoin_prices_df.copy()


# Filer the data based on the month


# Create a row to display all plots together
row1, row2 = st.columns((2))

# Daily Prices Line Chart
with row1:
    st.subheader('Daily Bitcoin Prices')
    fig1 = px.line(bitcoin_prices_df, x='date', y=['low', 'high', 'close','open'], labels={
        'value': 'Price',
        'date': 'Date'
    }, title='Daily')
    # Monthly Prices Bar Chart
with row2:
    st.subheader('Monthly Average Prices')
    fig2 = px.bar(monthly_data, x='month', y=['low', 'high', 'close', 'open'], barmode='group')
    fig2.update_layout(xaxis_title='Month', yaxis_title='Average Price')
    st.plotly_chart(fig2, use_container_width=True)
# Filter data based on selected month(s)
filtered_df = bitcoin_prices_df[bitcoin_prices_df["month"].isin(month)] if month else bitcoin_prices_df.copy()


# Pie Chart
with col2:
    st.subheader('Volume wise Bitcoin')
    fig3 = px.pie(filtered_df, values="volume", names="month", hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel)
    fig3.update_traces(text=filtered_df["month"], textposition="outside")  # Update text after creating fig3
    st.plotly_chart(fig3, use_container_width=True)

