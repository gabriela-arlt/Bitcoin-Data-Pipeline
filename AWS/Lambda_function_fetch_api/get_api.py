import os
import json
import requests
from datetime import datetime, timedelta


def fetch_bitcoin_data(event, context):
    """
    Fetches Bitcoin daily data for the past 180 days using Alpha Vantage API.

    Args:
        event (dict): The event object containing potential parameters.
        context (object): Lambda context object.

    Returns:
        dict: Dictionary containing status code and response body.

    Raises:
        ValueError: If API key is missing or data fetching fails.
    """

    # Get the API key from environment variable
    api_key = os.getenv('alpha_api_key')
    if not api_key:
        raise ValueError("API key not found in environment variables")

    # Handle missing parameters with defaults
    symbol = event.get("symbol", "BTC")
    market = event.get("market", "USD")

    # Set timeframe for past 180 days
    today = datetime.now()
    past_180_days = today - timedelta(days=90)

    # Construct the URL with 'outputsize=compact' for better performance
    url = f'https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol={symbol}&market={market}&apikey={api_key}&outputsize=compact&startDate={past_180_days.strftime("%Y-%m-%d")}'

    # Make the API request and get the JSON response
    response = requests.get(url).json()

    if 'Time Series (Digital Currency Daily)' in response:
        # Extract the daily time series data
        time_series = response['Time Series (Digital Currency Daily)']

        # You can add data transformation logic here (e.g., convert index, rename columns)

        return {
            "statusCode": 200,
            "body": json.dumps(time_series)
        }
    else:
        return {
            "statusCode": 500,
            "body": json.dumps(f"Error fetching data for {symbol}:{response}")
        }