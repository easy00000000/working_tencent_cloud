# -*- coding: utf-8 -*-
"""
Created on Wed Jun 19 13:33:56 2019

@author: w
"""
import pandas as pd
import requests
from pandas.compat import StringIO

def get_historical_data(symbol="AAPL.US", api_token="5cebe613e02010.08022109", session=None):
    if session is None:
        session = requests.Session()        
        url = "https://eodhistoricaldata.com/api/eod/%s" % symbol        
        params = {        
            "api_token": api_token        
        }
        r = session.get(url, params=params)
        if r.status_code == requests.codes.ok:
            df = pd.read_csv(StringIO(r.text), skipfooter=1, parse_dates=[0], index_col=0, engine="python")
        return df
    else:
        raise Exception(r.status_code, r.reason, url)
        
def save_eod(tickers):
    for e in tickers:
        print(e)
        symbol = e
        df = get_historical_data(symbol)
        df = df.rename({'Adjusted_close':'Adj Close'}, axis=1)
        csv_filename = e + '.csv'
        df.to_csv(csv_filename, encoding='utf-8')
        
tickers = ['SPY.US', '2833.HK']

#save to csv
save_eod(tickers)

# get data to pandas
symbol = tickers[0]
df = get_historical_data(symbol)
