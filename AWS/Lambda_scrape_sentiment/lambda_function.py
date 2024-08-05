import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import os
import boto3

# Hugging Face API Details (using environment variable)
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis"
HUGGINGFACE_API_TOKEN = os.environ.get("sentiment_token")  # Retrieve token from environment variable

# AWS Lambda Client
lambda_client = boto3.client('lambda', region_name='eu-north-1')

def get_sentiment(text):
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"}
    data = {"inputs": text}
    try:
        response = requests.post(HUGGINGFACE_API_URL, headers=headers, json=data)
        response.raise_for_status()
        response_json = response.json()

        # Log the full response for debugging
        print(f"Response JSON for '{text}': {response_json}")

        # Assuming Hugging Face returns a nested list structure
        if isinstance(response_json, list) and len(response_json) > 0 and isinstance(response_json[0], list):
            return response_json[0]

        return response_json
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred for {text}: {http_err} - {response.text}")
    except Exception as e:
        print(f"Error during sentiment analysis for {text}: {e}")
    return None  # Handle potential exceptions during API call

def scrape_ft_bitcoin_articles(event, context):
    try:
        articles = []
        # Calculate date range
        for i in range(90):
            date = datetime.now() - timedelta(days=i)
            formatted_date = date.strftime('%Y-%m-%d')

            # Construct URL with initial page number
            url = f'https://www.ft.com/search?q=Bitcoin&dateFrom={formatted_date}&dateTo={formatted_date}&page=1'

            page_number = 1  # Initialize page number

            while True:
                # Fetch webpage
                result = requests.get(url)
                soup = BeautifulSoup(result.content, 'html.parser')
                titles = soup.find_all('a', class_='js-teaser-heading-link')

                for title in titles:
                    # Sentiment Analysis Integration
                    sentiment = get_sentiment(title.text.strip())
                    if sentiment is not None:
                        article = {"date": formatted_date, "title": title.text.strip()}
                        # Process the sentiment data
                        for entry in sentiment:
                            if isinstance(entry, dict):
                                label = entry.get('label', '').lower()
                                score = entry.get('score', 0.0)
                                if label:
                                    article[f"{label}_score"] = score
                                else:
                                    print(f"Unexpected entry format: {entry}")
                        articles.append(article)
                    else:
                        print(f"Skipping article due to failed sentiment analysis: {title.text.strip()}")

                # Check for "Next Page" link
                next_page_link = soup.find('a', class_='next-page')

                if not next_page_link:
                    break  # No more pages, exit the loop

                page_number += 1  # Increment page number for next iteration
                url = f'https://www.ft.com/search?q=Bitcoin&dateFrom={formatted_date}&dateTo={formatted_date}&page={page_number}'

        # Convert articles list to JSON string
        articles_json = json.dumps(articles)

        # Invoke the second Lambda function to save the data
        response = lambda_client.invoke(
            FunctionName='arn:aws:lambda:eu-north-1:381492122205:function:Save_with_Sentiment',  # Correct function name
            InvocationType='Event',
            Payload=json.dumps({"responsePayload": {"body": articles_json}})
        )

        print("Invoked Save_with_Sentiment Lambda function with response:", response)

        # Return response
        return {
            'statusCode': 200,
            'body': articles_json
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
