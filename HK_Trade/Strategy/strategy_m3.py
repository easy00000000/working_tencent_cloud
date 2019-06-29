# -*- coding: utf-8 -*-
"""
Created on Tue May  7 10:01:15 2019

@author: w
"""

# historical_price_series, last_shares, last_cash

import numpy as np
from Algorithm.indicators import mean_std
from Strategy.allocation import w2s_simple as w2s
from Strategy.risk_parity import get_risk_parity_brute

def get_shares(histp_series, last_shares, last_cash, mc_budget):
    #mc_budget = [0.1, 0.5, 0.2, 0.2]
    # check historical data length
    mp = 52 # weekly data and use last year data as historical
    dw = 5 # slope    
    if len(histp_series) >= mp+dw:
        p = histp_series[len(histp_series)-mp-dw:len(histp_series)] #[0:57=52+5]
        w, mc, indicators = _get_w(p, mc_budget, mp, dw)
        shares, cash = w2s(w, p.iloc[-1], last_shares, last_cash)
    else:
        print('Not Enough Historical Data to Calc Weights') 
        shares = last_shares
        cash = last_cash
    
    return shares, cash, mc, indicators

def _get_w(p, mc_budget, mp, dw): 
    # calc covariance    
    cov = _get_cov(p)
    # calc risk budget
    mc, indicators = _get_mc(p, mc_budget, mp, dw) 
    # brute
    grid = 2
    w = get_risk_parity_brute(cov, grid, mc)
    return w, mc, indicators

def _get_cov(p):
    # r
    r=p.copy()
    for e in r.columns:
        r[e]=r[e].pct_change().dropna()  
    # calc cov matrix
    cov = np.array(r.cov())
    return cov

# if std+mean >= 0, then maintain previous mc with small change
# if std_mean < 0, then add a big risk weight
def _get_mc(p, mc_budget, mp, dw):
    # Bi
    factor = 100.0
    c = 0.0
    mc = mc_budget.copy()
    ind = np.zeros(len(p.columns))
    for e in range(0,len(p.columns)):
        mean, std = mean_std(p[p.columns[e]], dw=52)
        ind[e] = std**2 + mean
        mc[e] = (1.00-ind[e]*factor)*mc_budget[e]
        if mc[e] < 0.0001:
            mc[e] = 0.0
        c= c + mc[e]        
    for e in range(0,len(mc)):
        mc[e] = mc[e]/c
    return mc, mc