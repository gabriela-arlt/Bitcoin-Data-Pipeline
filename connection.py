import streamlit as st
from sqlalchemy import create_engine
import pandas as pd
import plotly.express as px
import altair as alt
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

# Main function to run the Streamlit app
def main():
    st.title("Bitcoin Data Visualization")

    # Custom CSS to change background color
    st.markdown(
        """
        <style>
        .main {
            background-color: #f5f5f5;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

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
            fig.update_traces(mode='lines+markers', hovertemplate='<b>Date</b>: %{x}<br><b>Price</b>: %{y}<br><b>News</b>: %{customdata[0]}')
            fig.update_traces(customdata=filtered_df[['news_title']].values)
            st.plotly_chart(fig)

            # Volume Bar Chart using Altair
            st.subheader('Daily Trading Volume')
            volume_chart = alt.Chart(filtered_df).mark_bar().encode(
                x='date:T',
                y='volume:Q',
                tooltip=['date:T', 'volume:Q']
            ).properties(
                width=800,
                height=400
            )
            st.altair_chart(volume_chart, use_container_width=True)

            # News Impact on Price using Altair
            st.subheader('News Impact on Bitcoin Price')
            price_news_chart = alt.Chart(filtered_df).mark_line().encode(
                x='date:T',
                y='close:Q'
            ).properties(
                width=800,
                height=400
            ) + alt.Chart(filtered_df).mark_text(
                align='left',
                baseline='middle',
                dx=7
            ).encode(
                x='date:T',
                y='close:Q',
                text='news_title:N'
            )
            st.altair_chart(price_news_chart, use_container_width=True)

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
