# -*- coding: utf-8 -*-
"""
Created on Thu Jun  6 11:42:57 2019

@author: w
"""
import csv
from time import time
import os
import matplotlib.pyplot as plt

from KChart import figure

def csv_performance(csv_file, file_mode, portfolio, total_return, annual_return, annual_std, sharpe_ratio, max_loss, annual=1):
    start_time = str(portfolio.index[0])
    end_time = str(portfolio.index[-1])
    ep, title, tr, ar, std, spr, mloss = str_performance(portfolio, total_return, annual_return, annual_std, sharpe_ratio, max_loss, annual)    
    # annual = 1 : for each year
    with open(csv_file, mode=file_mode) as csv_file:
        writer = csv.writer(csv_file, lineterminator='\n')
        writer.writerow(ep)
        writer.writerow(title)
        if annual > 0: 
            pass
        elif start_time[0:4] == end_time[0:4]:
            writer.writerow(tr)
            pass
        else:
            writer.writerow(tr)
        writer.writerow(ar)
        writer.writerow(std)
        writer.writerow(spr)
        writer.writerow(mloss)
    return csv_file
        
def str_performance(portfolio, total_return, annual_return, annual_std, sharpe_ratio, max_loss, annual=1):
    start_time = str(portfolio.index[0])
    end_time = str(portfolio.index[-1])
    ep = ['Evaluated_Period:']
    ep.append(start_time[0:10] + ' to ' + end_time[0:10])
    
    title = ['Assets:']
    for e in portfolio.columns:
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
        
    return ep, title, tr, ar, std, spr, mloss

def plot_performance(portfolio, weights, title=None, indicators=None, figname=None):
    ar = portfolio.copy()
    for e in portfolio.columns:
        d = ar[e][0]
        ar[e] = ar[e]/d
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
    if title is not None:
        ax1.set_title(title)
    
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
    
def get_filename(start_year, end_year, suffix='jpg', subpath=None):
    path = os.getcwd() + "\\"
    filename = str(time()).split('.')[0]
    if subpath is not None:
        path = path + subpath + "\\"
    filename = path + filename        
    if start_year == end_year:
        filename = filename + '(' + str(start_year) + ').' + suffix
    else:
        filename = filename + '(' + str(start_year) + '-' + str(end_year) + ').' + suffix
    return filename