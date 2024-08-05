import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, Date, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Hugging Face setup
API_URL = "https://api-inference.huggingface.co/models/mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis"
HEADERS = {"Authorization": f"Bearer {os.getenv('sentiment_token')}"}

def query_sentiment(payload):
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    return response.json()

# Database setup
DATABASE_URL = os.getenv('railway_url')
engine = create_engine(DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

# Define the Article model matching the existing table
class Article(Base):
    __tablename__ = 'news_with_sentiment'
    id = Column(Integer, primary_key=True)
    date = Column(Date)
    title = Column(String)
    neutral_score = Column(Float)
    positive_score = Column(Float)
    negative_score = Column(Float)

Base.metadata.create_all(engine)

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

        if not dates or not titles:
            break

        for date, title in zip(dates, titles):
            article_dates.append(date.get('datetime'))
            article_titles.append(title.get_text(strip=True))

        next_page_link = soup.find('a', class_='o-buttons-icon--arrow-right')
        if not next_page_link or 'is-disabled' in next_page_link.get('class', []):
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

def analyze_and_save_articles(df):
    for index, row in df.iterrows():
        sentiment_result = query_sentiment({"inputs": row['Title']})
        neutral_score = positive_score = negative_score = 0.0
        for result in sentiment_result:
            if result['label'] == 'LABEL_0':
                negative_score = result['score']
            elif result['label'] == 'LABEL_1':
                neutral_score = result['score']
            elif result['label'] == 'LABEL_2':
                positive_score = result['score']

        article = Article(
            date=row['Date'],
            title=row['Title'],
            neutral_score=neutral_score,
            positive_score=positive_score,
            negative_score=negative_score
        )
        session.add(article)
    session.commit()

bitcoin_articles_df = scrape_ft_bitcoin_articles()
analyze_and_save_articles(bitcoin_articles_df)
