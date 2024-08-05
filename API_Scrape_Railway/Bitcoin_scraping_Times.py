#for the news 
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta

def scrape_ft_bitcoin_articles():
    base_url = 'https://www.ft.com/bitcoin'
    page_number = 1
    article_dates = []
    article_titles = []

    while True:
        url = f'{base_url}?page={page_number}'
        result = requests.get(url)
        soup = BeautifulSoup(result.text, 'html.parser')
        dates = soup.select('time.o-date')
        titles = soup.select('a.js-teaser-heading-link')

        for date, title in zip(dates, titles):
            article_dates.append(date.get('datetime'))
            article_titles.append(title.get_text(strip=True))

        next_page_link = soup.find('a', class_='o-buttons-icon--arrow-right')
        if not next_page_link:
            break

        page_number += 1

    # Convert article dates to datetime objects
    article_datetimes = [datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ').date() for date in article_dates]

    # Filter articles for the last 3 months
    today = datetime.now().date()
    three_months_ago = today - timedelta(days=90)
    df = pd.DataFrame({
        'Date': article_datetimes,
        'Title': article_titles
    })
    df = df[df['Date'] >= three_months_ago]

    return df

bitcoin_articles_df = scrape_ft_bitcoin_articles()
print(bitcoin_articles_df)