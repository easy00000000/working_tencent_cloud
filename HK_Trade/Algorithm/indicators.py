# -*- coding: utf-8 -*-
"""
Author: easy00000000
Version: 0.01
Date: 2018-01-03
"""
import numpy as np

# up_cross
# t-1<0 and t>0, then cross(t)=v
def cross(data, v=1.0, mode='up'):
    cross = np.zeros(len(data))
    if mode == 'up':
        for t in range(1,len(data)):
            if data[t-1]<0 and data[t]>=0:
                cross[t] = v
    else:
        for t in range(1,len(data)):
            if data[t-1]>0 and data[t]<=0:
                cross[t] = -v
    return cross

def cross2(data, trend, v=1.0, mode='up'):
    cross = np.zeros(len(data))
    if mode == 'up':
        for t in range(1,len(data)):
            if data[t-1]<0 and data[t]>=0 and trend[t]>0:
                cross[t] = v
    else:
        for t in range(1,len(data)):
            if data[t-1]>0 and data[t]<=0 and trend[t]<0:
                cross[t] = -v
    return cross

# mean and std
def mean_std(hist_price, dw=250):
    # (0, t-1) - forecast (t)
    if len(hist_price)>=dw:
        m = hist_price[len(hist_price)-dw:len(hist_price)]
    else:
        m = hist_price
    r = m.pct_change()
    mean = r.mean()
    std = r.std()
    return mean, std

def ts_mean_std(data, dw=250):
    ts_mean = np.zeros(len(data))
    ts_std = np.zeros(len(data))
    for t in range(2, len(data)):
        hist_price = data[0:t-1]
        ts_mean[t], ts_std[t] =  mean_std(hist_price)
    return ts_mean, ts_std

# Bollinger Band
'''
Bollinger Band® formula:
BOLU=MA(TP,dw)+n_std∗σ[TP,dw]
BOLD=MA(TP,dw)−n_std∗σ[TP,dw]
where:
    BOLU=Upper Bollinger Band
    BOLD=Lower Bollinger Band
    MA=Moving average
    TP (typical price)=(High+Low+Close)÷3
    dw=Number of days in smoothing period (typically 20)
    n_std=Number of standard deviations (typically 2)
    σ[TP,dw]=Standard Deviation over last n periods of TP
'''
def boll(hist_price, dw=20, n_std=2):
    # (0,t-1) - forecast (t)
    if len(hist_price)>=dw:
        bo = hist_price[len(hist_price)-dw:len(hist_price)]
    else:
        bo = hist_price
    ma = bo.mean()
    std = bo.std()
    bolu = ma + n_std*std
    bold = ma - n_std*std
    return bolu, bold # value for t+1

def ts_boll(data, dw=20, n_std=2):
    # (0,t-1) - forecast (t)
    ts_bolu = data.copy()
    ts_bold = data.copy()
    for t in range(2, len(data)):
        hist_price = data[0:t-1]
        ts_bolu[t], ts_bold[t] =  boll(hist_price, dw, n_std)
    return ts_bolu, ts_bold

# Wavelet Calc
def swt(data, level):
    # level: swt level and should be >0
    ln=len(data)    
    lo=hi=lo2=hi2=0    
    cA = np.zeros((level, ln))
    cD = np.zeros((level, ln))
    for l in range(level):
        if l==0:
            t=data.copy()
        else:
            t=cA[l-1].copy()
        two=2**l
        two2=2**(l+1)
        # if data length is not enough (less than 2**level+1)
        # then not calculate and keep ZERO in these levels
        if ln>two2:
            for i in range(ln):
                lo=abs(i-two)
                hi=i+two
                if hi>=ln:
                    hi=ln+ln-hi-2           
                lo2=abs(i-two2)
                hi2=i+two2
                if hi2>=ln:
                    hi2=ln+ln-hi2-2
                cA[l][i]=(((t[lo2]+t[hi2])/16)+((t[lo]+t[hi])/4)+(3*t[i]/8))
            if l>0:
                cD[l] = cA[l-1] - cA[l]
    #cD[0] = data - cA[0]
    return cA, cD

def ts_swt(data, level):
    # (0, t) to forecast (t+1)
    ln=len(data)
    m=2**level+1
    # if data length is not enough (less than 2**level+1)
    # then just do static swt
    if ln>=m:        
        cA = np.zeros((level, ln))
        cD = np.zeros((level, ln))
        # for data between 0:m
        cA[:,:m], cD[:,:m] = swt(data[0:m], level)
        # for data between m+1:ln-1
        for i in range(m,ln):
            tcA, tcD = swt(data[i-m:i], level)
            cA[:,i], cD[:,i] = tcA[:,-1], tcD[:,-1]
    else:
        cA, cD = swt(data, level)
    return cA, cD