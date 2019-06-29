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
    w, mc, indicators = _get_mc(p, mc_budget, mp, dw) 
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
# 确定定投起点：负趋势时小于dn_level和正趋势开始
# 确定定投终点：负趋势开始和止损
def _get_mc(p, mc_budget, mp, dw):
    # Bi
    mc_start = [0.8, 0.2]
    up_level = 0.08
    dn_level = -0.08
    up_step = 0.05
    dn_step = 0.20
    cut_loss = 0.05
    bi_level = 4
    est_trend = np.zeros(len(p.columns))
    slope = np.zeros(len(p.columns))
    c = mc_budget[0]
    mc = mc_budget.copy()
    for e in range(1,len(p.columns)):
        cA, cD = ts_swt(p[p.columns[e]].get_values(), bi_level+1)
        # Slope
        t, s= est_trend_1(cA[bi_level])
        # calc mc
        if t[-1] > 0 and t[-2] >= 0: #正趋势中
            if s[-1] <= up_level:
                # 如果现值大于mc_start，则表示没止损过，继续定投；否则继续等待
                if mc[e] > mc_start[e]:
                    mc[e] = mc_budget[e] + up_step
                    if mc[e] > 1.0:
                        mc[e] = 1.0
            elif s[-1] > up_level:
                # cut loss
                if max(p[p.columns[e]]) > p[p.columns[e]].iloc[-1]*(1+cut_loss):
                    mc[e] = mc_start[e]
                    mc[0] = mc_start[0]
                    c = mc[0]
        elif t[-1] >= 0 and t[-2] < 0: #开始正趋势中
            mc[e] = mc_budget[e] + up_step
        elif t[-1] < 0:
            mc[e] = mc_budget[e] - dn_step
            if mc[e] < mc_start[e]:
                mc[e] = mc_start[e]
            if s[-1] < dn_level:
                mc[e] = mc_budget[e] + up_step
        if mc[e] < 0.0001:
            mc[e] = 0.0
        c= c + mc[e]
        slope[e] = s[-1]
        est_trend[e] = t[-1]
    for e in range(0,len(mc)):
        mc[e] = mc[e]/c
    w = mc
    return w, mc, est_trend #slope