import os
import psycopg2
from dotenv import load_dotenv
import pandas as pd
from Bitcoin_scraping_Times import scrape_ft_bitcoin_articles
from bitcoin_api import fetch_crypto_data

# Load environment variables
load_dotenv()

# Database connection parameters
database_url = os.getenv('railway_url')

# Connect to the database
conn = psycopg2.connect(database_url)
cur = conn.cursor()

# Create tables if they do not exist
cur.execute('''
CREATE TABLE IF NOT EXISTS bitcoin_data (
    date DATE PRIMARY KEY,
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    volume FLOAT
)
''')
cur.execute('''
CREATE TABLE IF NOT EXISTS bitcoin_news_Patricia (
    id SERIAL PRIMARY KEY,
    date DATE,
    title TEXT,
    UNIQUE (date, title)
)
''')

conn.commit()

# Function to insert data into the bitcoin_data table
def insert_bitcoin_data(conn, data):
    try:
        cursor = conn.cursor()
        for index, row in data.iterrows():
            cursor.execute('''
                INSERT INTO bitcoin_data (date, open, high, low, close, volume)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (date) DO NOTHING
            ''', (row.name, row['1. open'], row['2. high'], row['3. low'], row['4. close'], row['5. volume']))
        conn.commit()
        cursor.close()
    except Exception as e:
        print(f'Error inserting data: {e}')
        conn.rollback()

def insert_bitcoin_news(conn, df):
    try:
        cursor = conn.cursor()
        for index, row in df.iterrows():
            cursor.execute('''
                INSERT INTO bitcoin_news_Patricia (id, date, title)
                VALUES (%s, %s, %s)
            ''', (index,  row['Date'], row['Title']))
            conn.commit()
        cursor.close()
    except Exception as e:
        print(f"Error inserting bitcoin news: {e}")
        conn.rollback()


# Main function
def main():
    # Fetch bitcoin data
    bitcoin_data = fetch_crypto_data('BTC', 'USD')

    # Scrape bitcoin news
    bitcoin_news_df = scrape_ft_bitcoin_articles()

    # Connect to the database
    conn = psycopg2.connect(database_url)

    if conn:
        # Insert data
        insert_bitcoin_data(conn, bitcoin_data)
        insert_bitcoin_news(conn, bitcoin_news_df)

        # Close the connection
        conn.close()
    else:
        print('Failed to connect to the database')

if __name__ == '__main__':
    main()