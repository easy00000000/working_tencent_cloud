# -*- coding: utf-8 -*-
"""
Author: easy00000000
Version: 0.10
Date: 2018-01-05
"""

import numpy as np
import statsmodels.formula.api as smf

def real_trend(bi, v=1.0):
    t = np.zeros(len(bi))
    p = 0
    for i in range(1,len(bi)):
        if bi[i-1] > 0:
            p = -v
        elif bi[i-1] < 0:
            p = v
        t[i] = p
    return t

def strong(bi, tr=None, t=0.02, v=0.5):
    s = np.zeros(len(bi))
    pos1 = 0
    for i in range(1,len(bi)):        
        if bi[i]>0:            
            if -bi[i]/bi[pos1]-1>t:
                for j in range(pos1+1,i+1):
                    s[j] = v
            pos1 = i
        elif bi[i]<0:
            if -bi[pos1]/bi[i]-1>t:
                for j in range(pos1+1,i+1):
                    s[j] = -v
            pos1 = i
    if tr is not None:
        for i in range(len(bi)):
            if tr[i]>0 and s[i]<0:
                s[i] = 0.
            elif tr[i]<0 and s[i]>0:
                s[i] = 0.                
    return s

def est_trend_1(pl, v=1.0):
    # slope
    t = np.zeros(len(pl))
    slope = np.zeros(len(pl))
    dw=5
    x=np.arange(1,dw+1)/100.0
    for i in range(dw,len(slope)):
        #y = pl[i-dw+1:i+1].values / pl[i-dw+1:i+1].values.mean() - 1
        y = pl[i-dw+1:i+1] / pl[i-dw+1:i+1].mean() - 1
        model = smf.OLS(y,x)
        results = model.fit()            
        slope[i] = results.params
    for i in range(dw, len(pl)):
        if slope[i]>=0:
            t[i] = v
        else:
            t[i] = -v
    return t, slope

def est_trend_2(pl, bolu, bold, v=1.0):
    # boll
    t = np.zeros(len(pl))    
    for i in range(0, len(pl)):
        if pl[i] > bolu[i]:
            t[i] = v
        elif pl[i] < bold[i]:
            t[i] = -v
    return t

def est_trend_3(pl, v=1.0):
    t = np.zeros(len(pl))    
    for i in range(0, len(pl)):
        if pl[i] >= 0:
            t[i] = v
        elif pl[i] < 0:
            t[i] = -v
    return t

def get_match_trend(real_trend, est_trend, *args, **kwargs):
    up_trend_match = 0
    up_trend_mismatch = 0
    down_trend_match = 0
    down_trend_mismatch = 0
    for i in range(0, len(real_trend)):
        if real_trend[i] > 0:
            if est_trend[i] > 0:
                up_trend_match = up_trend_match + 1
            else:
                up_trend_mismatch = up_trend_mismatch + 1
        elif real_trend[i] < 0:
            if est_trend[i] < 0:
                down_trend_match = down_trend_match + 1
            else:
                down_trend_mismatch = down_trend_mismatch + 1
    total_up = up_trend_match + up_trend_mismatch
    total_down = down_trend_match + down_trend_mismatch
    up_match = up_trend_match / total_up
    up_mismatch = up_trend_mismatch / total_up
    down_match = down_trend_match / total_down
    down_mismatch = down_trend_mismatch / total_down
    return [up_match, up_mismatch, down_match, down_mismatch]

def display_match_trend(match_trend):
    up_match=match_trend[0]/(match_trend[0]+match_trend[3])
    up_mismatch=match_trend[1]/(match_trend[1]+match_trend[2])
    down_match=match_trend[2]/(match_trend[1]+match_trend[2])
    down_mismatch=match_trend[3]/(match_trend[0]+match_trend[3])
    title_trend =   '{:20}'.format('Macth Ratio:') + \
                    '{:20}'.format('est_up_trend') + \
                    '{:20}'.format('est_down_trend')
    up_trend_match ='{:20}'.format('real_up_trend') + \
                    '{:20}'.format('%0.2f%%' %(up_match*100)) + \
                    '{:20}'.format('%0.2f%%' %(up_mismatch*100))
    down_trend_match =  '{:20}'.format('real_down_trend') + \
                        '{:20}'.format('%0.2f%%' %(down_mismatch*100)) + \
                        '{:20}'.format('%0.2f%%' %(down_match*100))
    prn_txt =   title_trend + '\n' + \
                up_trend_match + '\n' + \
                down_trend_match
    
    return prn_txt