# -*- coding: utf-8 -*-
"""
Created on Tue Jun  4 16:43:12 2019

@author: w
"""
import numpy as np
import pandas as pd
import datetime
from Data.get_data import read_price

def mapping(tickers, delta_s, tickers_pl, \
            init_cash, trans_dates, trans_prices, shares, residual_cashs, \
            freq='D'): 
    #freq: T-trading date, D-Daily, W-Weekly, M-Monthly
    # t=0
    d = delta_s.index[0]
    mapping_date = np.array(d)
    cash = init_cash
    mapping_cash = np.array(cash)    
    s = np.zeros(len(tickers))
    mapping_shares = np.array(s)    
    c = np.zeros(len(tickers))   
    pre_t_date = delta_s.index[0] + datetime.timedelta(days=-1)    
    for e in range(len(tickers)):
        while pre_t_date.date() not in tickers_pl[tickers[e]].index.date:
            pre_t_date = pre_t_date + datetime.timedelta(days=-1)
        p = read_price(pre_t_date, tickers[e], tickers_pl[tickers[e]])
        c[e] = p.Close    
    mapping_closes = np.array(c)
    w = np.zeros(len(tickers))  
    mapping_weights = np.array(w)
    v = 0.0
    mapping_value = np.array(v)
    # t>=1
    if freq == 'D':
        start_date = delta_s.index[0]
        end_date = tickers_pl[tickers[0]].index[-1]
        range_date = pd.date_range(start=start_date, end=end_date, freq='D')
    elif freq == 'T':
        range_date = trans_dates
    else:
        range_date = trans_dates
    t = 0
    for d in range_date:
        if datetime.datetime.weekday(d)<=4:
            if d == trans_dates[t]:
                s = shares[t]
                cash = residual_cashs[t]
                if t < len(trans_dates)-1:
                    t = t + 1
            mapping_date = np.vstack([mapping_date, d])
            mapping_cash = np.vstack([mapping_cash, cash])
            mapping_shares = np.vstack([mapping_shares, s])
            for e in range(len(tickers)):
                if d.date() in tickers_pl[tickers[e]].index.date:
                    p = read_price(d, tickers[e], tickers_pl[tickers[e]])
                    c[e] = p.Close
            mapping_closes = np.vstack([mapping_closes, c])
            v = sum(s*c)
            mapping_value = np.vstack([mapping_value, v])
            for e in range(len(tickers)):
                w[e] = s[e]*c[e]/v
            mapping_weights = np.vstack([mapping_weights,w])
    return mapping_date, mapping_shares, mapping_weights, mapping_closes, mapping_cash, mapping_value
                
def get_portfolio(tickers, mapping_date, \
                  mapping_closes, mapping_cash, mapping_value):
    portfolio = pd.DataFrame(data=mapping_closes, columns=tickers)
    portfolio['Date'] = mapping_date
    portfolio['Value'] = mapping_value
    portfolio['Cash'] = mapping_cash
    portfolio['NAV'] = portfolio['Value'] + portfolio['Cash']
    portfolio.set_index("Date", inplace=True)
    portfolio = portfolio.drop(['Value', 'Cash'], axis=1)
    return portfolio

def get_pd(tickers, mapping_date, mapping_data):
    df = pd.DataFrame(data=mapping_data, columns=tickers)
    df['Date'] = mapping_date
    df.set_index("Date", inplace=True)
    return df
    
def get_performance(portfolio):
    annual_r = np.zeros(len(portfolio.columns))
    annual_std = np.zeros(len(portfolio.columns))
    total_r = np.zeros(len(portfolio.columns))
    sharpe_ratio = np.zeros(len(portfolio.columns))
    max_loss = np.zeros(len(portfolio.columns))
    for e in range(len(portfolio.columns)):
        p = portfolio[portfolio.columns[e]]
        #r = _calc_r(p)
        total_r[e] = _calc_total_r(p)
        annual_r[e] = _calc_annual_r(p)
        annual_std[e] = _calc_annual_std(p)        
        sharpe_ratio[e] = _calc_sharpe_ratio(annual_r[e], annual_std[e])
        max_loss[e] = _calc_max_loss(p)
    return annual_r, annual_std, total_r, sharpe_ratio, max_loss
    
# return at t   
def _calc_r(p):
    r = p.pct_change()
    r.fillna(0.0, inplace=True)
    return r

# annual return
def _calc_annual_r(p, annual_factor=365):
    total_r = p.iloc[-1] / p.iloc[0] - 1
    days = (p.index[-1] - p.index[0]).days
    annual_r = (1+total_r)**(annual_factor/days) - 1
    return annual_r
'''
def _calc_annual_r(r, annual_factor=360):
    days = (r.index[-1] - r.index[0]).days
    annual_r = (1+r.mean())**(len(r)*annual_factor/days) - 1
    return annual_r
'''

# annual std
def _calc_annual_std(p, annual_factor=365):
    r = p.pct_change()
    r.fillna(0.0, inplace=True)
    days = (p.index[-1] - p.index[0]).days
    r = (1+r)**(len(p)/days) - 1
    annual_std = r.std()*(annual_factor**0.5)
    return annual_std
'''
def _calc_annual_std(r, annual_factor=360):
    days = (r.index[-1] - r.index[0]).days
    annual_std = r.std()*((len(r)*annual_factor/days)**0.5)
    return annual_std
'''

# total return
def _calc_total_r(p):
    total_r = p.iloc[-1] / p.iloc[0] - 1
    return total_r

# sharpe ratio
def _calc_sharpe_ratio(annual_r, annual_std, risk_free = 0.0):
    sharpe_ratio = (annual_r-risk_free)/annual_std
    return sharpe_ratio

# max loss
def _calc_max_loss(p):    
    m = 0.0
    for t in range(1,len(p)):
        d = (min(p[t:len(p)]) / p[t-1]) - 1
        if m>d:
            m=d
    max_loss = m
    return max_loss