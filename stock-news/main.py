from twilio.rest import Client
import requests
from newsapi import NewsApiClient
from datetime import date
import pandas as pd
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

load_dotenv()
STOCK = "AMD"
COMPANY_NAME = "AMD"
STOCK_API = os.getenv("STOCK_API")
NEWS_API = os.getenv("NEWS_API")
TWILIO = os.getenv("TWILIO")
SMS_API = os.getenv("SMS_API")
FROM_NUMBER = os.getenv("FROM_NUMBER")
TO_NUMBER = os.getenv("TO_NUMBER")
websites = ['tomshardware.com', 'arstechnica.com', 'techcrunch.com', 'reuters.com', 'bloomberg.com', 'apnews.com', 'cnet.com']

## STEP 1: Use https://www.alphavantage.co
# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").


offset = pd.tseries.offsets.BusinessDay(n=1)
yesterday = (date.today() - offset).date()
ototoi = (yesterday - offset).date()

stock_params = {
	'function': 'TIME_SERIES_DAILY',
	'symbol' : STOCK,
	'outputsize': 'compact',
	'apikey': STOCK_API,
	}

resp = requests.get('https://www.alphavantage.co/query', params=stock_params)
data = resp.json()['Time Series (Daily)']

close_day_minus_1 = data[str(yesterday)]['4. close']
close_day_minus_2 = data[str(ototoi)]['4. close']
price_delta = round((float(close_day_minus_1) - float(close_day_minus_2)) / float(close_day_minus_2) * 100, 1)
emoji = '🔺' if price_delta >= 0 else '🔻'

## STEP 2: Use https://newsapi.org
# Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME. 

newsapi = NewsApiClient(api_key=NEWS_API)

data = newsapi.get_everything(
	q=COMPANY_NAME, 
	qintitle='title',
	domains=','.join(websites), 
	language='en', 
	sort_by='relevancy'
	)

articles = data['articles'][:3]

## STEP 3: Use https://www.twilio.com
# Send a seperate message with the percentage change and each article's title and description to your phone number. 

if abs(price_delta) > 5:
	for article in articles:
		desc = BeautifulSoup(article['description'], 'html.parser')
		client = Client(TWILIO, SMS_API)
		message = client.messages \
						.create(
							body=f"{STOCK}: {emoji}{abs(price_delta)}%\n\
								Headline: {article['title']}\n\
								Brief: {desc.get_text()}",
							from_=FROM_NUMBER,
							to=TO_NUMBER
						)
#Optional: Format the SMS message like this: 
"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
"""

