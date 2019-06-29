# -*- coding: utf-8 -*-
"""
Created on Tue May  7 11:27:51 2019

@author: w
"""
import numpy as np
from KChart import figure
import matplotlib.pyplot as plt
from time import time
import csv

# use original mc
def get_performance_1(supporting_data, evaluated_data, mc_budget, strategy_function, *args, **kwargs):
    # strategy_function gets shares position for t
    # historical data of each asset in portfolio
    
    # initial
    initial_cash = 500000
    last_shares = np.zeros(len(evaluated_data.columns))
    last_cash = initial_cash
    
    zl = np.zeros(len(evaluated_data))
    pfm = evaluated_data.copy()    
    pfm = pfm.assign(Portfolio=zl)   
    s = evaluated_data.copy()
    s = s.assign(Cash=zl)
    w = evaluated_data.copy()
    indicators = evaluated_data.copy()
    mc = mc_budget.copy()
    
    histp_series = supporting_data.copy()
    
    for t in range(0, len(evaluated_data)):
        shares, cash, mc, indicator_t = strategy_function(histp_series, last_shares, last_cash, mc_budget, *args, **kwargs)
        pfm['Portfolio'][t] = 0.0
        for e in range(0, len(shares)):
            s[s.columns[e]][t]=shares[e]
            pfm['Portfolio'][t] = pfm['Portfolio'][t] + shares[e]*pfm[pfm.columns[e]][t]
        s['Cash'][t] = cash
        pfm['Portfolio'][t] = pfm['Portfolio'][t] + cash
        w.iloc[t] = _real_weights(evaluated_data.iloc[t], pfm['Portfolio'][t], shares)
        indicators.iloc[t] = indicator_t
        # for next step
        last_shares = shares
        last_cash = cash
        histp_series = histp_series.append(evaluated_data.iloc[t])    
    
    accumulated_return, total_return, annual_return, annual_std, sharp_ratio, max_loss = _get_results(pfm, supporting_data, initial_cash)
    
    return pfm, s, w, accumulated_return, total_return, annual_return, annual_std, sharp_ratio, max_loss, indicators

# remember update mc
def get_performance_2(supporting_data, evaluated_data, mc_budget, strategy_function, *args, **kwargs):
    # strategy_function gets shares position for t
    # historical data of each asset in portfolio
    
    # initial
    initial_cash = 500000
    last_shares = np.zeros(len(evaluated_data.columns))
    last_cash = initial_cash
    
    zl = np.zeros(len(evaluated_data))
    pfm = evaluated_data.copy()    
    pfm = pfm.assign(Portfolio=zl)   
    s = evaluated_data.copy()
    s = s.assign(Cash=zl)
    w = evaluated_data.copy()
    indicators = evaluated_data.copy()
    mc = mc_budget.copy()
    
    histp_series = supporting_data.copy()
    
    for t in range(0, len(evaluated_data)):
        shares, cash, mc, indicator_t = strategy_function(histp_series, last_shares, last_cash, mc, *args, **kwargs)
        pfm['Portfolio'][t] = 0.0
        for e in range(0, len(shares)):
            s[s.columns[e]][t]=shares[e]
            pfm['Portfolio'][t] = pfm['Portfolio'][t] + shares[e]*pfm[pfm.columns[e]][t]
        s['Cash'][t] = cash
        pfm['Portfolio'][t] = pfm['Portfolio'][t] + cash
        w.iloc[t] = _real_weights(evaluated_data.iloc[t], pfm['Portfolio'][t], shares)
        indicators.iloc[t] = indicator_t
        # for next step
        last_shares = shares
        last_cash = cash
        histp_series = histp_series.append(evaluated_data.iloc[t])    
    
    accumulated_return, total_return, annual_return, annual_std, sharp_ratio, max_loss = _get_results(pfm, supporting_data, initial_cash)
    
    return pfm, s, w, accumulated_return, total_return, annual_return, annual_std, sharp_ratio, max_loss, indicators

def _real_weights(p, v, s):
    w = np.zeros(len(s))
    for e in range(0,len(s)):
        w[e] = s[e]*p[e] / v
    return w

def _get_results(original_pfm, supporting_data, initial_cash, annual_factor=52):
    # structure t=-1 data
    zl = np.zeros(len(supporting_data))
    spd = supporting_data.copy()    
    spd = spd.assign(Portfolio=zl)
    spd['Portfolio'][-1] = initial_cash
    pfm = original_pfm.copy()
    pfm = pfm.append(spd.iloc[-1])
    pfm = pfm.sort_index()
       
    # accumulated return
    accumulated_return = _calc_accumulated_return(pfm)    
    # totalreturn
    total_return = _calc_total_return(accumulated_return)        
    # annualized return and std
    annual_return, annual_std = _calc_annual_return_std(accumulated_return)        
    # sharpe ratio
    sharpe_ratio = _calc_sharpe_ratio(annual_return, annual_std)        
    # max loss
    max_loss = _calc_max_loss(accumulated_return)
    
    return accumulated_return, total_return, annual_return, annual_std, sharpe_ratio, max_loss

# accumulated return
def _calc_accumulated_return(pfm):
    r = pfm.copy()
    acm_r = pfm.copy()
    for e in pfm.columns:
        r[e]=r[e].pct_change()
        r[e][0]=0.0
        acm_r[e][0]=0.0
        for t in range(1,len(r)):        
            acm_r[e][t]=(1+r[e][t])*(1+acm_r[e][t-1])-1    
    accumulated_return = acm_r
    return accumulated_return
    
# total return
def _calc_total_return(accumulated_return):
    total_return = []
    for e in accumulated_return.columns:
        total_return.append(accumulated_return[e][-1])
    return total_return

# annualized return and std
def _calc_annual_return_std(accumulated_return, annual_factor=52):
    annual_return = []
    annual_std = []
    r = accumulated_return.copy()
    for e in accumulated_return.columns:
        for t in range(1, len(r)):
            r[e][t] = (1+accumulated_return[e][t])/(1+accumulated_return[e][t-1])-1
        annual_return.append(r[e].mean()*annual_factor)        
        annual_std.append((r[e].std()**2 * annual_factor)**0.5)
    return annual_return, annual_std

# sharpe ratio
def _calc_sharpe_ratio(annual_return, annual_std, risk_free = 0.0):
    sharpe_ratio = []
    for i in range(0, len(annual_return)):
        sharpe_ratio.append(annual_return[i]/annual_std[i])
    return sharpe_ratio

# max loss
def _calc_max_loss(accumulated_return):
    max_loss = []
    p = accumulated_return.copy()
    for e in accumulated_return.columns:
        m=0
        for t in range(1,len(p)):
            d = min(p[e][t:len(p)]) - p[e][t-1]
            if m>d:
                m=d
        max_loss.append(m)
    return max_loss
    
def get_performance_by_results(w, accumulated_return, annual_factor=52):
    # unitizing
    ar = accumulated_return.copy()
    for e in ar.columns:
        for t in range(len(ar)):
            ar[e][t] = (1+ar[e][t])/(1+accumulated_return[e][0]) - 1
    # totalreturn
    total_return = _calc_total_return(ar)    
    # annualized return and std
    annual_return, annual_std = _calc_annual_return_std(ar)     
    # sharpe ratio
    sharpe_ratio = _calc_sharpe_ratio(annual_return, annual_std)        
    # max loss
    max_loss = _calc_max_loss(ar)
        
    return w, ar, total_return, annual_return, annual_std, sharpe_ratio, max_loss
        
def display_performance(w, accumulated_return, total_return, annual_return, annual_std, sharpe_ratio, max_loss, annual=1):
    start_time = str(accumulated_return.index[0])
    end_time = str(accumulated_return.index[-1])
    ep = '{:20}'.format('Evaluated_Period:') + start_time[0:10] + ' to ' + end_time[0:10]
    
    title = '{:20}'.format('Assets:')
    for e in accumulated_return.columns:
        title= title + '{:>12}'.format(e)
        
    tr ='{:20}'.format('Total_Return')
    ar ='{:20}'.format('Annualized_Return')
    std = '{:20}'.format('Annualized_STD')
    spr = '{:20}'.format('Sharpe_Ratio')
    mloss = '{:20}'.format('Max_Loss')
    for i in range(0, len(total_return)):
        tr = tr + '{:>12}'.format('%0.2f%%' %(total_return[i]*100))
        ar = ar + '{:>12}'.format('%0.2f%%' %(annual_return[i]*100))
        std = std + '{:>12}'.format('%0.2f%%' %(annual_std[i]*100))
        spr = spr + '{:>12}'.format('%0.2f' %(sharpe_ratio[i]))
        mloss = mloss + '{:>12}'.format('%0.2f%%' %(max_loss[i]*100))
    
    # annual = 1 : for each year
    if annual > 0:
        prn_txt =   ep + '\n' + \
                    title + '\n' + \
                    ar + '\n' + \
                    std + '\n' + \
                    spr + '\n' + \
                    mloss
    elif start_time[0:4] == end_time[0:4]:
        prn_txt =   ep + '\n' + \
                    title + '\n' + \
                    ar + '\n' + \
                    std + '\n' + \
                    spr + '\n' + \
                    mloss
    else:
        prn_txt =   ep + '\n' + \
                    title + '\n' + \
                    tr + '\n' + \
                    ar + '\n' + \
                    std + '\n' + \
                    spr + '\n' + \
                    mloss
    print(prn_txt)
    return prn_txt

def csv_performance(csv_file, file_mode, w, accumulated_return, total_return, annual_return, annual_std, sharpe_ratio, max_loss, annual=1):
    start_time = str(accumulated_return.index[0])
    end_time = str(accumulated_return.index[-1])
    ep = ['Evaluated_Period:']
    ep.append(start_time[0:10] + ' to ' + end_time[0:10])
    
    title = ['Assets:']
    for e in accumulated_return.columns:
        title.append(e)
        
    tr = ['Total_Return']
    ar = ['Annualized_Return']
    std = ['Annualized_STD']
    spr = ['Sharpe_Ratio']
    mloss = ['Max_Loss']
    for i in range(0, len(total_return)):
        tr.append('%0.2f%%' %(total_return[i]*100))
        ar.append('%0.2f%%' %(annual_return[i]*100))
        std.append('%0.2f%%' %(annual_std[i]*100))
        spr.append('%0.2f' %(sharpe_ratio[i]))
        mloss.append('%0.2f%%' %(max_loss[i]*100))
    
    # annual = 1 : for each year
    with open(csv_file, mode=file_mode) as csv_file:
        writer = csv.writer(csv_file, lineterminator='\n')
        writer.writerow(ep)
        writer.writerow(title)
        if annual > 0: 
            pass
        elif start_time[0:4] == end_time[0:4]:
            pass
        else:
            writer.writerow(tr)
        writer.writerow(ar)
        writer.writerow(std)
        writer.writerow(spr)
        writer.writerow(mloss)
    return csv_file

def plot_performance(weights, accumulated_return, indicators=None, figname=None):
    ar = accumulated_return.copy()
    # Set rows of figure
    if indicators is None:
        rows = 2
    else:
        rows = 3
    cols = 1
    
    # Set figure and gridspec
    fig = figure.set_fig(-1, -1, rows=rows)
    gs = figure.set_gs(rows, cols=cols, height_ratios=2)
    
    # ax1
    ax1 = fig.add_subplot(gs[0, 0])    
    plt.setp(ax1.get_xticklabels(), visible=False)
    ax1.set_xlim(ar.index[0], ar.index[-1])    
    
    for i in range(0,len(ar.columns)-1):
        ax1.plot(ar[ar.columns[i]], linewidth=2)
    ax1.plot(ar[ar.columns[len(ar.columns)-1]], color='black', linewidth=4)
    ax1.legend()
    
    # ax2
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.set_xlim(ar.index[0], ar.index[-1])
    ax2.stackplot(weights.index, weights.values.T)
    
    # ax3
    if indicators is not None:
        plt.setp(ax2.get_xticklabels(), visible=False)
        ax3 = fig.add_subplot(gs[2, 0])
        ax3.set_xlim(ar.index[0], ar.index[-1])
        for e in indicators.columns:
            #ax3.stackplot(indicators.index, indicators.values.T)
            ax3.plot(indicators[e], linewidth=2)
        ax3.legend()
    
    if figname is not None:    
        fig.savefig(figname) # save the figure to file
        plt.close(fig)
        
def get_figname(start_year, end_year, suffix='jpg'):
    figname = str(time()).split('.')[0]
    if start_year == end_year:
        figname = figname + '(' + str(start_year) + ').' + suffix
    else:
        figname = figname + '(' + str(start_year) + '-' + str(end_year) + ').' + suffix
    return figname