# -*- coding: utf-8 -*-
"""
Author: easy00000000
Version: 0.05
Date: 2019-03-03
"""
import numpy as np
from KChart.mpl import candlestick_ohlc
from matplotlib.lines import Line2D

def plot_ohlc(ax, ohlc):
    candlestick_ohlc(ax, ohlc, colorup='r', colordown='g')
    
def plot_y(ax, y, label=None, linewidth=1):
    xax = np.arange(len(y))
    ax.plot(xax, y, label=label, linewidth=linewidth)
    ax.legend()
    
def plot_bar(ax, h, width=0.2): #h: height of bar
    xax = np.arange(len(h))
    ax.bar(xax, h, width=width)
    
def plot_fill(ax, y): #h: height of bar
    xax = np.arange(len(y))
    ax.fill_between(xax, 0, y)
    
def plot_bi(ax, bi, label=None, lw=1., ls='-', color='blue'):
    x = []
    y = []
    for i in range(len(bi)):
        if bi[i] > 0 :
            x.append(i)
            y.append(bi[i])
        elif bi[i] < 0 :
            x.append(i)
            y.append(-bi[i])
    line = Line2D(x, y,
                  label=label,
                  lw=lw,
                  color=color,
                  ls=ls)
    ax.add_line(line)
    ax.legend()
