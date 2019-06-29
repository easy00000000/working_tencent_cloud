# -*- coding: utf-8 -*-
"""
Created on Tue May  7 10:01:15 2019

@author: w
"""

# historical_price_series, last_shares, last_cash

import numpy as np
import statsmodels.formula.api as smf
from Strategy.allocation import w2s_simple as w2s
from Strategy.risk_parity import get_risk_parity_brute
from Algorithm.scale import linear_scale

def get_shares(histp_series, last_shares, last_cash, mc_budget):
    #mc_budget = [0.1, 0.5, 0.2, 0.2]
    # check historical data length
    mp = 52 # weekly data and use last year data as historical
    dw = 5 # slope    
    if len(histp_series) >= mp+dw:
        p = histp_series[len(histp_series)-mp-dw:len(histp_series)] #[0:57=52+5]
        w, diff = _get_w(p, mc_budget, mp, dw)
        shares, cash = w2s(w, p.iloc[-1], last_shares, last_cash)
    else:
        print('Not Enough Historical Data to Calc Weights') 
        shares = last_shares
        cash = last_cash
    
    return shares, cash, diff

def _get_w(p, mc_budget, mp, dw): 
    # calc covariance    
    cov = _get_cov(p)
    # calc risk budget
    #mc = mc_budget
    mc = _get_mc(p, mc_budget, mp, dw) 
    # brute
    grid = 2
    w = get_risk_parity_brute(cov, grid, mc)
    return w

def _get_cov(p):
    # r
    r=p.copy()
    for e in r.columns:
        r[e]=r[e].pct_change().dropna()  
    # calc cov matrix
    cov = np.array(r.cov())
    return cov
    
def _get_mc(p, mc_budget, mp, dw):
    # ma
    ma = p.copy()
    for e in p.columns:
        ma[e] = p[e].rolling(mp,center=False,min_periods=1).mean()
    
    # distance
    dist = ma.copy()
    dist = p/ma-1
    
    # slope    
    slope = ma.copy()
    ln=len(slope)
    x=np.arange(1,dw+1)/100.0
    for e in p.columns:
        for i in range(mp,ln):
            y = ma[e][i-dw+1:i+1].values / ma[e][i-dw+1] - 1
            model = smf.OLS(y,x)
            results = model.fit()            
            slope[e][i] = results.params
    
    # calc mc_budget
    d = dist.iloc[-1]
    s = slope.iloc[-1]
    ln = len(d)
    mc = np.zeros(ln)
    c = 0.0
    for i in range(1, ln):
        if s[i]<s[i-1]:
            mc[i] = linear_scale(d[i], 0.0, 5.0, -0.1, -0.3) * mc_budget[i]
        else:
            mc[i] = linear_scale(d[i], 5.0, 1.0, -0.3, 0.3) * mc_budget[i]
        if mc[i] < 0.0001:
            mc[i] = 0.0
        c= c + mc[i]
    if c>1:
        mc = mc/c
        mc[0] = 0.0
    else:
        mc[0] = 1.0 - c
        
    return mc