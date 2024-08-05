import requests
import datetime as dt
import pandas as pd
from dotenv import load_dotenv
import requests
import os

load_dotenv()
api_key=os.getenv('alpha_api_key')

def fetch_crypto_data(symbol, market):
   url= f'https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol={symbol}&market={market}&apikey=api_key'
   response= requests.get(url)
   data=response.json()
   if 'Time Series (Digital Currency Daily)' in data:
      time_series=data['Time Series (Digital Currency Daily)']
      df= pd.DataFrame.from_dict(time_series, orient='index')
      df=df.astype(float)
      df.index=pd.to_datetime(df.index)
      df=df.sort_index()

      return df
   else:
      print(f'Error fetching data from {symbol}:{data}')
      return pd.DataFrame()
   
#fetsch now
bitcoin_data=fetch_crypto_data('BTC', 'USD')
print(bitcoin_data)
      