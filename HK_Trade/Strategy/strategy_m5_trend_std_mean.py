# -*- coding: utf-8 -*-
"""
Created on Tue June 14th 10:01:15 2019
2019/5/29
策略以主ETF进入正趋势建仓 + 选择强子ETF增强轮动配置
主ETF建仓：进入负趋势后，逐渐建仓
止损：高估值下跌5%
减仓：负趋势
未加入 慢（定投）建仓 策略
@author: w
"""

# historical_price_series, last_shares, last_cash

import numpy as np
from Algorithm.indicators import ts_swt, ts_mean_std
from Algorithm.mkstatus import est_trend_1
from Strategy.allocation import w2s_simple_int as w2s

def get_shares(histp_series, last_shares, last_cash, mc_budget):
    # check historical data length
    mp = 250 # weekly data and use last year data as historical
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

# 策略
def _get_mc(p, mc_budget, mp, dw):
    # Bi
    bi_level = 5
    up_step = 0.01
    dn_step = 0.05
    cut_loss = 0.05
    # each asset weight limit
    main_asset_mc_limit = 0.95
    single_asset_mc_limit = 0.10
    # mc_start
    single_asset_mc_init = 0.0
    mc_start = [0.8, 0.2]
    if len(p.columns)>2:
        for e in range(2,len(p.columns)):
            mc_start.append(single_asset_mc_init)
    est_trend = np.zeros(len(p.columns))
    slope = np.zeros(len(p.columns))
    mc = mc_budget.copy()    
    for e in range(1,len(p.columns)):
        cA, cD = ts_swt(p[p.columns[e]].get_values(), bi_level+1)
        # 指数ETF
        if e == 1:
            # Slope
            wt_long = cA[bi_level]
            wt_short = cA[bi_level-2]
            t1, s= est_trend_1(wt_long)
            # mean-std
            mean, std = ts_mean_std(p[p.columns[e]])
            diff = 2*std[-1]*std[-1] + mean[-1]
            t2 = 0.0
            if diff < 0 and t1[-1] < 0:
                t2 = -1.0
            #if t1[-1] > 0:
            #    t2 = 0.0
            diff_wt = 10*(wt_short[-1]/wt_long[-1]-1)
            if diff_wt > 0.5:
                t2 = 1.0
            if t2<0:
                if mc[e] <= main_asset_mc_limit:              
                    mc[e] = mc[e]+up_step
                    mc[0] = mc[0]-up_step
            elif t2>0:
                if mc[e] >= dn_step:
                    mc[e] = mc[e]-dn_step
                    mc[0] = mc[0]+dn_step
            #print(p.index[-1], t2, t1[-1], diff)
        # 行业ETF
        elif e > 1:
            # Slope
            t2, s2= est_trend_1(cA[bi_level]) 
            # calc mc 正趋势且强于指数
            if t2[-1] > 0 and sum(s2[-5:-1])>sum(s[-5:-1]):
                if s2[-1] > -100.0:
                    # 如果现值大于mc_start，则表示没止损过，继续定投；否则继续等待
                    if mc[e] >= mc_start[e]:
                        mc = _get_up_step(e, mc, up_step, single_asset_mc_limit)
                elif s2[-1] > 0.0:
                    # cut loss
                    if max(p[p.columns[e]]) > p[p.columns[e]].iloc[-1]*(1+cut_loss):
                        mc = _cut_loss(e, mc, mc_start, up_step)
            elif t2[-1] < 0:
                mc = _get_dn_step(e, mc, dn_step, mc_start)
            slope[e] = s2[-1]
            est_trend[e] = t2[-1]
        if mc[e]<0.0001:
            mc[e]=0.0
    mc = _rebalance(mc)
    w = mc
    return w, mc, est_trend #slope

def _get_up_step(e, mc, up_step, mc_limit):
    if mc[e] <= mc_limit:
        if mc[e] + up_step <= mc_limit:            
            mc[e] = mc[e] + up_step
        else:
            mc[e] = mc_limit
    return mc

def _get_dn_step(e, mc, dn_step, mc_start):
    if mc[e] >= dn_step + mc_start[e]:
        mc[e] = mc[e] - dn_step
    else:
        mc[e] = mc_start[e]
    return mc

def _cut_loss(e, mc, mc_start, cut_more):
    mc[e] = max(mc_start[e]-cut_more, 0.0)
    return mc

def _rebalance(mc):
    c = 0.0
    for e in range(1,len(mc)):
        c = c + mc[e]
    if c>1.0:
        mc[0] = 0.0
        for e in range(1,len(mc)):
            mc[e] = mc[e]/c
    else:
        mc[0] = 1.0 - c
    return mc
        