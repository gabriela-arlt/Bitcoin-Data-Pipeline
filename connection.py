import streamlit as st
from sqlalchemy import create_engine
import pandas as pd
import plotly.express as px
import os
from dotenv import load_dotenv
load_dotenv()

# Print secrets to debug
#st.write(st.secrets)

# Function to connect to the Database
def get_connection():
    try:
# DATABASE_URL = os.getenv("railway_url")
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

# Main function to run the Streamlit app
def main():
    st.title("Bitcoin Data Visualization")

    # Get the database connection
    conn = get_connection()

    if conn is not None:
        # Fetch the bitcoin data and news
        bitcoin_prices_df = fetch_bitcoin_data(conn)
        bitcoin_news_df = fetch_bitcoin_news(conn)

        if not bitcoin_prices_df.empty and not bitcoin_news_df.empty:
            # Merge prices and news dataframes on the date column
            merged_df = pd.merge(bitcoin_prices_df, bitcoin_news_df, on='date', how='left')

            # Convert the date column to datetime format
            merged_df['date'] = pd.to_datetime(merged_df['date'])

            # Convert pandas Timestamps to datetime.date
            min_date = merged_df['date'].min().date()
            max_date = merged_df['date'].max().date()

            # Adding a date slider
            date_range = st.slider("Select Date Range", min_date, max_date, (min_date, max_date))

            # Filter the dataframe based on the selected date range
            filtered_df = merged_df[(merged_df['date'] >= pd.to_datetime(date_range[0])) & (merged_df['date'] <= pd.to_datetime(date_range[1]))]

            # Creating a Plotly line chart with tooltips for news
            fig = px.line(filtered_df, x='date', y='close', title='Prices for BTC', labels={'close': 'BTC Price'})

            # Add hover data for news headlines
            fig.update_traces(mode='lines+markers', hovertemplate='<b>Date</b>: %{x}<br><b>Price</b>: %{y}<br><b>News</b>: %{customdata[0]}')
            fig.update_traces(customdata=filtered_df[['title']].values)

            # Display the Plotly chart
            st.plotly_chart(fig)

            # Displaying the dataframe with bitcoin news
            st.title("Bitcoin News")
            st.write(bitcoin_news_df)
        else:
            st.error("No data available to display.")
    else:
        st.error("Failed to connect to the database.")

# Run the app
if __name__ == "__main__":
    main()
