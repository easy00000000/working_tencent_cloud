# -*- coding: utf-8 -*-
"""
Created on Mon May  6 21:27:15 2019

@author: w
"""

# calculate shares based on weights
# with checking balance and shares rounding to integer
def w2s(weights, last_price, last_shares, last_cash, smooth_factor=0.0, nShare=100):
    # last_price: each asset price at t-1
    # last_shares: each asset's shares at t-1
    # last_cash: cash at t-1
    # smooth_factor: max(smooth_factor, abs(current_shares/last_shares - 1)) for each asset    
    shares = last_shares
    last_value = last_price.dot(last_shares) + last_cash
    
    # get shares
    delta_fund = last_cash
    for i in range(0, len(weights)):
        delta_s = (weights[i]*last_value / last_price[i]) - last_shares[i]
        if smooth_factor > 0:                 
            delta_s = smooth_shares(delta_s, last_shares[i], smooth_factor)
        if delta_s > 0 : # buy the asset
            delta_s = abs(delta_s) + 0.5*nShare
            delta_s =  (delta_s // nShare) * nShare
            shares[i] = last_shares[i] + delta_s
            delta_fund = delta_fund - delta_s * last_price[i] # pay cash
        else: # sell the asset
            delta_s = abs(delta_s) + 0.5*nShare
            delta_s =  delta_s // nShare * nShare
            if last_shares[i] >= delta_s:
                shares[i] = last_shares[i] - delta_s
            else:
                shares[i] = 0.0
                delta_s = last_shares[i]
            delta_fund = delta_fund + delta_s * last_price[i] # get cash
    
    # reach balance    
    while delta_fund < 0: # no enough cash, buy less and sell more
        for i in range(0, len(weights)):
            if shares[i] >= nShare:
                shares[i] = shares[i] - nShare
                delta_fund = delta_fund + nShare * last_price[i]
    
    cash = delta_fund
    while cash > last_price[0]*nShare:
        cash = cash - last_price[0]*nShare
        shares[0] = shares[0] + nShare
    
    return shares, cash

# keep stable change from t-1 to t
def smooth_shares(delta_s, last_s, smooth_factor):
    if last_s > 0:
        if delta_s > 0:
            if delta_s > last_s * smooth_factor:
                delta_s = last_s * smooth_factor
        else:
            if abs(delta_s) > last_s * smooth_factor:
                delta_s = - last_s * smooth_factor
    return delta_s

# calculate shares based on weights without considering integer
def w2s_simple(weights, last_price, last_shares, last_cash):
    shares = last_shares
    last_value = last_price.dot(last_shares) + last_cash
    for i in range(0, len(weights)):
        shares[i] = weights[i] * last_value / last_price[i]
        if shares[i] < 1:
            shares[i] = 0.0
    cash = last_value - last_price.dot(shares)
    if cash < 0.01:
        cash = 0.0
    return shares, cash

# calculate shares based on weights and simply considering integer
def w2s_simple_int(weights, last_price, last_shares, last_cash, nShare=100):
    shares = last_shares.copy()
    last_value = last_price.dot(last_shares) + last_cash
    for i in range(0, len(weights)):
        shares[i] = weights[i] * last_value / last_price[i]
        if shares[i] < last_shares[i]:
            shares[i] = (shares[i] // nShare - 1) * nShare
        elif shares[i] > last_shares[i]:
            shares[i] = (shares[i] // nShare) * nShare
        if shares[i] < 0:
            shares[i] = 0.0
    cash = last_value - last_price.dot(shares)
    if cash < 0.01:
        cash = 0.0
    return shares, cash