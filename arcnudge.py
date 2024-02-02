from io import BytesIO
from tempfile import tempdir
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
# not needed for mpl >= 3.1
from matplotlib.backends.backend_agg import FigureCanvas
import numpy as np
import numba as nb
import pandas as pd
import holoviews as hv
from holoviews.operation import gridmatrix
import panel as pn
from datetime import datetime,date,timedelta
import finnhub
import requests
from yahoo_fin.stock_info import get_data
import seaborn as sns
from scipy.optimize import minimize
import time
pn.extension(template='fast')
pn.state.template.title = "Arcesium"
import os
import hvplot.pandas  # noqa


text = """
#  ARC Nudge

Arc Nudge performs analysis of your position holdings to get actionable insights from your portfolio:

To get actionable insights from your portfolio:

1. Upload excel of the holdings for a particular date
2. Apply the filters
3. Run the Analysis
"""
holdings_data=pd.read_excel("holdings_sample.xlsx")

stocks=holdings_data['Symbol'].tolist()
country_list=['Norway','Italy','Denmark','Romania','UK']
date_picker = pn.widgets.DatePicker(name='Date')
file_input = pn.widgets.FileInput(align='center')
stock_selector=pn.widgets.Select(name='Select individual stock', options=stocks)


days_analysed=pn.widgets.IntSlider(name='Last x days-social media analysis', value=5, start=2, end=10, step=1)

button = pn.widgets.Button(name='Run Analysis')

widgets = pn.WidgetBox(
    pn.panel(text, margin=(0, 10)),
    pn.panel('Upload an excel containing stock holdings data:', margin=(0, 10)),
    date_picker,
    file_input,
    days_analysed,
    stock_selector,
    button

)
def get_holdings():
    if file_input.value is None:
        holdings_file = 'holdings_sample.xlsx'
    else:
        holdings_file = BytesIO()
        holdings_file.write(file_input.value)
        holdings_file.seek(0)
    return pd.read_excel(holdings_file)




@pn.depends(button.param.clicks)
def get_portfolio_analysis(_):
    holdings_data=get_holdings()
    finnhub_client = finnhub.Client(api_key="cmt5p1hr01qqtangidrgcmt5p1hr01qqtangids0")
    no_days=days_analysed.value
    #growth=mentions_growth.value


    def social_media_mentions(data,no_days):
        end_date=date.today()-timedelta(1)

        start_date=end_date-timedelta(no_days-1)
        hist_end_date=start_date-timedelta(1)
        hist_start_date=hist_end_date-timedelta(no_days)

        #start_date=start_date.strftime('%Y-%m-%d')
        #end_date=end_date.strftime('%Y-%m-%d')
        for ticker in data["Symbol"].unique():
            #historical mentions
            hist_resp=finnhub_client.stock_social_sentiment(ticker,hist_start_date,hist_end_date)
            hist_reddit_df=pd.DataFrame(hist_resp["reddit"])
            hist_twitter_df=pd.DataFrame(hist_resp["twitter"])
            hist_mentions=pd.concat([hist_reddit_df,hist_twitter_df])
            tot_hist_mentions=hist_mentions["mention"].sum()

            # current time period mentions
            sent_resp=finnhub_client.stock_social_sentiment(ticker,start_date,end_date)
            if len(sent_resp["reddit"])==0:
                data.loc[data["Symbol"]==ticker,"reddit_mentions"]=0
            else:
                reddit_df=pd.DataFrame(sent_resp["reddit"])
                reddit_df["date"]=reddit_df["atTime"].apply(lambda x:str(datetime.strptime(x,'%Y-%m-%d %H:%M:%S').date()))
                reddit_mentions=reddit_df["mention"].sum()
                reddit_pos_mentions=reddit_df["positiveMention"].sum()
                reddit_neg_mentions=reddit_df["negativeMention"].sum()
                data.loc[data["Symbol"]==ticker,"reddit_mentions"]=reddit_mentions
            if len(sent_resp["twitter"])==0:
                data.loc[data["Symbol"]==ticker,"twitter_mentions"]=0
            else:
                twitter_df=pd.DataFrame(sent_resp["twitter"])
                twitter_df["date"]=twitter_df["atTime"].apply(lambda x:str(datetime.strptime(x,'%Y-%m-%d %H:%M:%S').date()))
                twitter_mentions=twitter_df["mention"].sum()
                twitter_pos_mentions=twitter_df["positiveMention"].sum()
                twitter_neg_mentions=twitter_df["negativeMention"].sum()
                data.loc[data["Symbol"]==ticker,"twitter_mentions"]=twitter_mentions
            total_mentions=reddit_mentions+twitter_mentions

            pos_mentions=reddit_pos_mentions+twitter_pos_mentions
            neg_mentions=reddit_neg_mentions+twitter_neg_mentions
            data.loc[data["Symbol"]==ticker,"positve_mentions"]=pos_mentions
            data.loc[data["Symbol"]==ticker,"negative_mentions"]=neg_mentions
            data.loc[data["Symbol"]==ticker,"Increase in total mentions(%)"]=((total_mentions-tot_hist_mentions)*100/tot_hist_mentions)


            ##price and volume data
            volume_start_date=start_date.strftime('%m-%d-%Y')
            volume_end_date=date.today().strftime('%m-%d-%Y')
            volume_price_data=get_data(ticker, start_date=volume_start_date, end_date=volume_end_date, index_as_date = True, interval="1d")

            volume_sum=volume_price_data["volume"].sum()
            price=volume_price_data.tail(1)["close"].values[0]
            data.loc[data["Symbol"]==ticker,"Volume"]=volume_sum
            data.loc[data["Symbol"]==ticker,"Current Market Price"]=price

        return data





    def highlight_rows(s):

        if (s["Increase in total mentions(%)"] in top_two_values.values) & (s["Increase in total mentions(%)"]>0):
             return ['background-color: #FF0000'] * len(s)
        else:
            return ['background-color: '] * len(s)

    def individual_stock_mentions(ticker):
        end_date=date.today()-timedelta(1)

        start_date=end_date-timedelta(no_days-1)
        #print(f"in indvidual stocks start_date:{start_date},end_date:{end_date}")
        sent_resp_ticker=finnhub_client.stock_social_sentiment(ticker,start_date,end_date)
        reddit_df_ticker=pd.DataFrame(sent_resp_ticker["reddit"])
        twitter_df_ticker=pd.DataFrame(sent_resp_ticker["twitter"])
        mentions_ticker=pd.concat([reddit_df_ticker,twitter_df_ticker])
        mentions_ticker["date"]=mentions_ticker["atTime"].apply(lambda x:str(datetime.strptime(x,'%Y-%m-%d %H:%M:%S').date()))
        mentions_grouped=mentions_ticker.groupby("date").agg({'mention':np.sum,'positiveMention':np.sum,'negativeMention':np.sum,'score':np.mean}).reset_index()


        ##price and volume data
        volume_start_date=start_date.strftime('%m-%d-%Y')
        volume_end_date=date.today().strftime('%m-%d-%Y')
        volume_price_data=get_data(ticker, start_date=volume_start_date, end_date=volume_end_date, index_as_date = False, interval="1d")


        return mentions_grouped,volume_price_data



    final_data=social_media_mentions(holdings_data,no_days)
    final_data["Exposure"]=final_data["Net Position"]*final_data["Current Market Price"]
    final_data=final_data.round({"Exposure":3})
    final_data.drop(['Sr. No.'],axis=1,inplace=True)
    ## Fetch volume and price data
    #volume_price_data(final_data)



    top_two_values=final_data["Increase in total mentions(%)"].nlargest(2)
    df_widget = pn.widgets.Tabulator(final_data,frozen_columns=['Index','Holdings'],theme='midnight', width=800)
    df_widget.style.apply(highlight_rows,axis=1)

    mentions_grouped,volume_price_data=individual_stock_mentions(stock_selector.value)
    volume_price_data["date"]=volume_price_data["date"].dt.strftime('%Y-%m-%d')
    mentions_volume_price=pd.merge(mentions_grouped,volume_price_data,on='date',how='left')
    mentions_volume_price=mentions_volume_price[["date","mention","positiveMention","negativeMention","close","volume"]]
    mentions_dashboard = hv.NdOverlay({col: hv.Curve(mentions_volume_price, 'date', col).redim(**{col: '# mentions'}) for col in ["mention","positiveMention","negativeMention"]}).opts(
        title_format='Date', min_height=300, responsive=True, show_grid=True, legend_position='top_left')
    volume_dashboard=hv.NdOverlay({col: hv.Curve(mentions_volume_price, 'date', col).redim(**{col: 'Volume'}) for col in ["volume"]}).opts(
        title_format='Date', min_height=300, responsive=True, show_grid=True, legend_position='top_left')
    price_dashboard=hv.NdOverlay({col: hv.Curve(mentions_volume_price, 'date', col).redim(**{col: 'Closing Price ($)'}) for col in ["close"]}).opts(
        title_format='Date', min_height=300, responsive=True, show_grid=True, legend_position='top_left')



    return pn.Tabs(
        ('Portfolio volume and Social media analysis',pn.Column(pn.Row(df_widget,sizing_mode='stretch_width'),sizing_mode='stretch_width')),
        ('Dashboard',pn.Column(pn.Row(mentions_dashboard,sizing_mode='stretch_width'),pn.Row(volume_dashboard,sizing_mode='stretch_width'),pn.Row(price_dashboard,sizing_mode='stretch_width'),sizing_mode='stretch_width')
        )
        #('Oil volume prediction', pn.Row(menu_button,pn.Column(image_raw,analyze_button),pn.Row(image_interim,image_final),pn.Row(oil_levels[country]), height=300))
        #('Mentions Dashboard',pn.Column(mentions_dashboard))

    )



pn.Row(pn.Column(widgets), pn.layout.Spacer(width=20),get_portfolio_analysis).servable()
