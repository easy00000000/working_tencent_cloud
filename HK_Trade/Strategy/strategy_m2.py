# -*- coding: utf-8 -*-
"""
Created on Tue May  7 10:01:15 2019

@author: w
"""

# historical_price_series, last_shares, last_cash

import numpy as np
from Algorithm.indicators import ts_swt
from Algorithm.mkstatus import est_trend_1
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
    #mc = mc_budget
    mc, indicators = _get_mc(p, mc_budget, mp, dw) 
    # brute
    grid = 4
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

# 策略 + 止损和慢（定投）建仓
# 慢（定投）建仓，很难通过risk parity解决
def _get_mc(p, mc_budget, mp, dw):
    # Bi
    up_level = 0.06
    dn_level = -0.02
    cut_loss = 0.05
    bi_level = 4
    slope = np.zeros(len(p.columns))
    c = 0.0
    mc = mc_budget.copy()
    for e in range(0,len(p.columns)):
        cA, cD = ts_swt(p[p.columns[e]].get_values(), bi_level+1)
        # Slope
        est_trend, s= est_trend_1(cA[bi_level])
        # calc mc_budget
        if s[-1]>up_level:
            #mc[e] = 0.9*mc_budget[e]
            if max(p[p.columns[e]]) > p[p.columns[e]].iloc[-1]*(1+cut_loss):
                if mc_budget[e] > 0.5:
                    mc[e] = 0.95*mc_budget[e]
        elif s[-1]<dn_level:            
            mc[e] = 1.01*mc_budget[e]
        if mc[e] < 0.0001:
            mc[e] = 0.0
        c= c + mc[e]
        slope[e] = s[-1]
    if c>1:
        for e in range(0,len(mc)):
            mc[e] = mc[e]/c
    return mc, slope