# -*- coding: utf-8 -*-
"""
Created on Thu May 30 16:24:17 2019

@author: w
"""
import numpy as np
import pandas as pd
import datetime
from Data.get_data import read_price # from eod csv file

def est_transacton_prices_1(tickers, delta_s, tickers_pl):
    trans_prices = delta_s.copy()
    place_date = delta_s.index.date
    #t=0
    t_date = delta_s.index[0]
    prices = np.zeros(len(tickers))
    pre_t_date = t_date + datetime.timedelta(days=-1)    
    for e in range(len(tickers)):
        while pre_t_date.date() not in tickers_pl[tickers[e]].index.date:
            pre_t_date = pre_t_date + datetime.timedelta(days=-1)
        c = read_price(pre_t_date, tickers[e], tickers_pl[tickers[e]])
        prices[e] = c.Close
    #t>=1
    for t in range(len(delta_s.index)):
        pre_prices = prices
        t_date = delta_s.index[t]        
        t_date = t_date + datetime.timedelta(days=1)
        s = delta_s.iloc[t].copy()
        for e in range(len(tickers)):
            t_date_e = t_date
            while t_date_e.date() not in tickers_pl[tickers[e]].index.date:
                t_date_e = t_date_e + datetime.timedelta(days=1)
            if s[e] > 0.0: # buy
                transaction = 'BUY'
            elif s[e] < 0.0:
                transaction = 'SELL'
            else:
                transaction = 'No Trade'
            place_price = get_transaction_price(t_date_e, tickers[e], transaction, pre_prices[e], tickers_pl[tickers[e]])
            trans_prices[tickers[e]].iloc[t] = place_price
        place_date[t] = t_date_e
        prices = get_close_price(tickers, t_date, tickers_pl, True)
    trans_prices.reset_index(level=0, inplace=True)
    trans_prices.Date = place_date
    trans_prices.set_index("Date", inplace=True)
    return trans_prices

def est_transacton_prices(tickers, delta_s, tickers_pl):
    trans_prices = pd.DataFrame(columns=delta_s.columns)
    shares = pd.DataFrame(columns=delta_s.columns)
    #t=0
    t_date = delta_s.index[0]    
    # find 1st close price
    prices = np.zeros(len(tickers))
    pre_t_date = t_date + datetime.timedelta(days=-1)
    for e in range(len(tickers)):
        while pre_t_date.date() not in tickers_pl[tickers[e]].index.date:
            pre_t_date = pre_t_date + datetime.timedelta(days=-1)
        c = read_price(pre_t_date, tickers[e], tickers_pl[tickers[e]])
        prices[e] = c.Close
    #t>=1
    for t in range(len(delta_s.index)):
        if t==0:
            # initialize dateframe
            trans_prices.loc[len(trans_prices)] = np.zeros(len(tickers))
            trans_prices['Date'] = delta_s.index[0]
            shares.loc[len(shares)] = np.zeros(len(tickers))
            shares['Date'] = delta_s.index[0]
        else:
            # add one more row
            trans_prices.loc[len(trans_prices)] = trans_prices.loc[len(trans_prices)-1]
            shares.loc[len(shares)] = shares.loc[len(shares)-1]
        pre_prices = prices
        t_date = delta_s.index[t]        
        t_date = t_date + datetime.timedelta(days=1)
        s = delta_s.iloc[t].copy()
        for e in range(len(tickers)):
            t_date_e = t_date
            while t_date_e.date() not in tickers_pl[tickers[e]].index.date:
                t_date_e = t_date_e + datetime.timedelta(days=1)
            if s[e] > 0.0: # buy
                transaction = 'BUY'
            elif s[e] < 0.0:
                transaction = 'SELL'
            else:
                transaction = 'No Trade'
            place_price = get_transaction_price(t_date_e, tickers[e], transaction, pre_prices[e], tickers_pl[tickers[e]])
            trans_prices[tickers[e]].iloc[t] = place_price
            shares[tickers[e]].iloc[t] = s[e] + shares[tickers[e]].iloc[t]
        trans_prices['Date'].iloc[t] = t_date_e
        shares['Date'].iloc[t] = t_date_e
        # find t period close price
        prices = get_close_price(tickers, t_date, tickers_pl, True) # True : weekend close
    # set date as index
    trans_prices.set_index("Date", inplace=True)
    shares.set_index("Date", inplace=True)
    return trans_prices, shares
    
def get_transaction_price(t_date, ticker, transaction, pre_Close, pl=None, worst=False):    
    p = read_price(t_date, ticker, pl)
    if transaction == 'BUY':
        price = _get_long_price(p, pre_Close)
    elif transaction == 'SELL':
        price = _get_short_price(p, pre_Close)
    else:
        price = p.Close
    return price

def _get_long_price(p, pre_Close, worst=False):
    if worst:
        long_price = p.High
    else:
        if p.Open <= pre_Close:
            long_price = p.Open
        else:
            long_price = p.Close
    return long_price

def _get_short_price(p, pre_Close, worst=False):
    if worst:
        short_price = p.Low
    else:
        if p.Open >= pre_Close:
            short_price = p.Open
        else:
            short_price = p.Close
    return short_price

# IB
# US$1<=fee<=1%
# US$0.005 per share
# transaction fee US$0.0000207*total transaction value
# sell - transaction fee US$0.000119 per share
def _calc_fee(price, delta_s, transaction):
    if delta_s != 0:
        delta_s = abs(delta_s)
        total_value = price*delta_s
        fee = 0.005 * delta_s
        if fee<1:
            fee = 1.0
        elif fee>0.01*total_value:
            fee = 0.01*total_value
        fee = fee + 0.0000207*total_value
        if transaction == 'SELL':
            fee = fee + 0.000119*delta_s
    else:
        fee = 0.0
    return fee

# pre_shares: shares of each asset at t-1    
# pre_cash: cash at t-1
# pre_prices: pre_Close at t-1
# delta_s: share change of each asset at t
# return cash and shares at t
def get_allocation(tickers, t_date, delta_s, pre_shares, pre_cash, pre_prices, tickers_pl=None, worse=False):
    shares = pre_shares.copy()
    cash = pre_cash
    prices = shares.copy()
    for e in range(len(tickers)):
        if tickers_pl is None:
            pl = None
        else:
            pl = tickers_pl[tickers[e]]
        delta_cash = 0.0
        shares[e] = pre_shares[e] + delta_s[e]
        if delta_s[e] > 0.0: # buy
            price = get_transaction_price(t_date, tickers[e], 'BUY', pre_prices[e], pl)
            fee = _calc_fee(price, delta_s[e], 'BUY')
            delta_cash = -delta_s[e] * price - fee
        else:
            price = get_transaction_price(t_date, tickers[e], 'SELL', pre_prices[e], pl)
            fee = _calc_fee(price, delta_s[e], 'SELL')
            delta_cash = -delta_s[e] * price - fee
        if e==0:
            pass #print(delta_cash)
        cash = cash + delta_cash
        prices[e] = price
    return shares, cash, prices

def get_value(tickers, t_date, shares, tickers_pl=None):
    value = 0.0
    for e in range(len(tickers)):
        if tickers_pl is None:
            pl = None
        else:
            pl = tickers_pl[tickers[e]]
        p = read_price(t_date, tickers[e], pl)
        value = value + p.Close * shares[e]
    value = value
    return value

def get_close_price(tickers, t_date, tickers_pl=None, weekend=False):
    prices = np.zeros(len(tickers))
    if weekend is not True:
        for e in range(len(tickers)):
            if tickers_pl is None:
                pl = None
            else:
                pl = tickers_pl[tickers[e]]
            p = read_price(t_date, tickers[e], pl)
            prices[e] = p.Close
    else:
        for e in range(len(tickers)):
            if tickers_pl is None:
                pl = None
            else:
                pl = tickers_pl[tickers[e]]
            p = read_price(t_date, tickers[e], pl, True)
            prices[e] = p.Close
    return prices
        