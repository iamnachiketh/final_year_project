from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pandas as pd
import matplotlib.pyplot as plt
import panel as pn

finviz_url = 'https://finviz.com/quote.ashx?t='
tickers = ['AMZN','AMD','TSLA','GOOG']

news_tables = {}
for ticker in tickers:
    url = finviz_url + ticker

    req = Request(url=url, headers={'user-agent': 'my-app'})
    response = urlopen(req)

    html = BeautifulSoup(response,features="html.parser")
    news_table = html.find(id='news-table')
    news_tables[ticker] = news_table


parsed_data = []

for ticker, news_table in news_tables.items():

    for row in news_table.findAll('tr'):

        title = row.a.text
        date_data = row.td.text.split(' ')
        arr = [value for value in date_data if value != ""]
        if len(arr) == 2:
            time = arr[1][:7]
        else:
            date = arr[1]
            time = arr[2][:7]

        parsed_data.append([ticker, date, time, title])

df = pd.DataFrame(parsed_data, columns=['ticker', 'date', 'time', 'title'])

vader = SentimentIntensityAnalyzer()

f = lambda title: vader.polarity_scores(title)['compound']
df['compound'] = df['title'].apply(f)
df = df[df['date'] != 'Today']
# Convert 'date' column to datetime
df['date'] = pd.to_datetime(df['date'], format='%b-%d-%y')
plt.figure(figsize=(10,8))
mean_df = df.groupby(['ticker', 'date'])['compound'].mean()
mean_df = mean_df.unstack().transpose()
mean_df.index = mean_df.index.strftime('%Y-%m-%d')

# Plot the DataFrame
mean_df.plot(kind='bar')
plt.xlabel('Date')
plt.ylabel('Compound Mean')
plt.title('Mean Compound Scores Over Time')
plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
plt.tight_layout()
panel_pane = pn.pane.Matplotlib(plt.gcf(),tight=True)
app = pn.Column(panel_pane)
app.show()

