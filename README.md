# Project: ﻿Bitcoin-Data-Pipeline
## Premise of the project: the focus of the project is creating a data pipeline which would involve scraping Financial news and getting API data about Bitcoin from alphavantage, saving the data in railway, automating the process using AWS Lambda function and Eventrbridge and last but not least visualizing the data in Streamlit.

## Data:
+ Bitcoin API data from alphavantage
+ Scraped data from Financial Times
## Libraries used: 
+ Data Extraction:
Web Scraping: Using requests and BeautifulSoup to collect data from web sources.
API Requests: Fetching data from web APIs with requests.
+ Data Management:
Data Handling: Manipulating and analyzing data with pandas.
Database Interaction: Storing and retrieving data from PostgreSQL using psycopg2 and sqlalchemy.
+ Data Visualization:
Interactive Visuals: Creating interactive charts and dashboards with plotly and streamlit.
+ Configuration Management:
Environment Variables: Managing configuration and sensitive information using dotenv.
+ Date and Time Handling:
Time-Series Analysis: Utilizing datetime for time-based data analysis.


## Step 1 (files: API_Scrape_Railway)
+ I have first created functions for getting API data and scraping the news (files: bitcoin_api.py and Bitcoin_ Scraping_Times.py) further I have activated both functions and saved the data into Railway (files: railway_connection.py). I have used here SQL integrated into Python in order to create the databse and specify the columns and keys
## Step 2 (files: AWS folder)
+ automating the process  via creating a AWS Lamnda function for getting the API data, sceduling it daily via EventBridge in AWS (folders: Lambda_functions_fetch_API and Lambda_function_save_api)
+ automating the process via creating a AWS Lambda functions for scraping Financial Times daily, again sceduling the event daily  (folders: Lambda_functions_scrape_news and Lambda_function_save_news)
+ automating seinding the titles to hugging face for sentiment analysis and saving the results in railway (folder: lambda_scrape_sentiment, lamda_save_sentiment)
+ for all first three steps the folders consist of the libraries which AWS need for the lambda function file to work. I believe this was one of the most challenging steps in the process, getting the libraries to work
## Step 3 (file: connection.py)
+ I connect the Railway database to Streamlit
+ currently only the API data is visualized due to lack of time for the project. Just building the pipeline took most of the times. (you can take a look at other streamlit projects in case you need to know how I would deal with streamlit)
+ link to the app: https://bitcoin-data-pipeline-wzl7ckt2sf7crdty9ndu6a.streamlit.app/

