# -*- coding: utf-8 -*-
"""
Created on Wed May  8 13:03:23 2019

@author: w
"""
import os
import pandas as pd
#from eod_historical_data import get_eod_data
import datetime
import requests
from pandas.compat import StringIO

# Read data from CSV files
def read_csv(etf_tickers, end_date=''):    
    pl = None    
    p_t=['Date','Adj Close']
    for e in etf_tickers:
        # Read
        csv_path = os.getcwd() + "\\Data\\"
        csv_filename = csv_path + e + end_date + '.csv'
        df = pd.read_csv(csv_filename)
        p=df[p_t].sort_values(by='Date')
        p['Date'] = pd.to_datetime(p['Date'])
        p.set_index("Date", inplace=True)
        p = p.rename({'Adj Close':e}, axis=1)        
        # Merge
        if pl is None:
            pl=p
        else:
            pl = pd.merge(pl,p,left_index=True, right_index=True)        
    return pl

# Download data from eodhistoricaldata.com
def fetch_eod(tickers, market='US'):
    #api_token = '5cebe613e02010.08022109'
    pl = None
    p_t=['Adjusted_close']
    for e in tickers:        
        #df = get_eod_data(e, market, None, None, api_token, None)
        symbol = e + '.' + market
        df = get_historical_data(symbol)
        p = df[p_t]
        p = p.rename({'Adjusted_close':e}, axis=1)
        if pl is None:
            pl=p
        else:
            pl = pd.merge(pl,p,left_index=True, right_index=True)
    return pl

def save_eod(tickers, market='US'):
    #api_token = '5cebe613e02010.08022109'
    csv_path = os.getcwd() + "\\" #Data\\"
    for e in tickers:
        #df = get_eod_data(e, market, None, None, api_token, None)
        symbol = e + '.' + market
        df = get_historical_data(symbol)
        df = df.rename({'Adjusted_close':'Adj Close'}, axis=1)
        csv_filename = csv_path + e + '.csv'
        df.to_csv(csv_filename, encoding='utf-8')

# read price series from csv fetched from eod        
def read_ticker(ticker, end_date=''):
    csv_path = os.getcwd() + "\\Data\\"    
    csv_filename = csv_path + ticker + end_date + '.csv'
    df = pd.read_csv(csv_filename)
    p=df.sort_values(by='Date')
    p['Date'] = pd.to_datetime(p['Date'])
    p.set_index("Date", inplace=True)
    return p

# read price of a special date, from csv fetched from eod
def read_price(t_date, ticker, pl=None, freq='Daily', end_date=''): #freq=Daily, Weekly, Monthly
    if pl is None:
        pl = read_ticker(ticker, end_date=end_date)
    if isinstance(t_date, str):
        t_date = datetime.datetime.strptime(t_date,'%Y-%m-%d')
    if freq=='Daily':       
        while t_date.date() not in pl.index.date:
            t_date = t_date + datetime.timedelta(days=1)
    elif freq=='Weekly': # find weekend price
        t = datetime.datetime.weekday(t_date)
        if t<5:
            t_date = t_date + datetime.timedelta(days=4-t) # this weekend
        else:
            t_date = t_date + datetime.timedelta(days=4+7-t) # next weekend
        while t_date.date() not in pl.index.date:
            t_date = t_date + datetime.timedelta(days=-1)
    p = pl[pl.index.date == t_date.date()].iloc[0]
    return p

# get working date from base date
# previous working date or next working date
def get_working_date(t_date, previous=False):    
    if isinstance(t_date, str):
        t_date = datetime.datetime.strptime(t_date,'%Y-%m-%d')
    if previous is not True:    # find next working day
        n = 1
    else:                       # find previous working day
        n = -1
    t_date = t_date + datetime.timedelta(days=n)
    t = datetime.datetime.weekday(t_date)
    while t>4:
        t_date = t_date + datetime.timedelta(days=n)
        t = datetime.datetime.weekday(t_date)
    return t_date

def get_weekend_date(t_date, ticker, previous=False):
    if isinstance(t_date, str):
        t_date = datetime.datetime.strptime(t_date,'%Y-%m-%d')
    if previous is not True:    # find this weekend
        n = 6
    else:                       # find previous weekend
        n = -1
    t_date = t_date + datetime.timedelta(days=n)
    t = datetime.datetime.weekday(t_date)
    while t!=4:
        t_date = t_date + datetime.timedelta(days=-1)
        t = datetime.datetime.weekday(t_date)
    return t_date

# EOD Data
# https://eodhistoricaldata.com/api/eod/AAPL.US?api_token={your_api_key}
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