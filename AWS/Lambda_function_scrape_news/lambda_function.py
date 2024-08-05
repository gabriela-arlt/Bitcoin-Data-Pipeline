import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json

def scrape_ft_bitcoin_articles(event, context):
    try:
        articles = []
        # Calculate date range
        for i in range(90):
            date = datetime.now() - timedelta(days=i)
            formatted_date = date.strftime('%Y-%m-%d') 

            # Construct URL
            url = f'https://www.ft.com/search?q=Bitcoin&dateFrom={formatted_date}&dateTo={formatted_date}&page=1'

            # Fetch webpage
            result = requests.get(url)
            soup = BeautifulSoup(result.content, 'html.parser')
            dates = soup.select('time.o-date')
            titles = soup.find_all('a', class_='js-teaser-heading-link')

            for title in titles:
                articles.append({"date":formatted_date, "title": title.text.strip()})

        # Convert articles list to JSON string
        articles_json = json.dumps(articles)

        # Return response
        return {
            'statusCode': 200,
            'body': articles_json
        }
    except Exception as e:
        # Return error response
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
