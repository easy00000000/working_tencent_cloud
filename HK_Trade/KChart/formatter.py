# -*- coding: utf-8 -*-
"""
Author: easy00000000
Version: 0.20
Date: 2017-12-23
"""
import numpy as np
import matplotlib.ticker as mticker

try:
    from itertools import izip
except ImportError:
    izip = zip

def dec(v):
    d = 1e1
    vs = v/d
    while vs>1:
        d=d*10
        vs = v/d
    return d

def _match_col(col, columns):
    for c in columns:
        if col == c.lower():
            return c
        
def format_ohlc(df, formated_cols=['open', 'high', 'low', 'close']):
    cols = formated_cols
    # format Dataframe as formated columns name
    matched = []
    for col in cols:
        match = _match_col(col, df.columns)
        if match:
            matched.append(match)
            continue
        raise Exception('{col} not found'.format(col=col))
    formated_df = df[matched]
    formated_df.columns = cols
    formated_df.index = df.index
    # convert zip format
    f = formated_df
    xax = np.arange(len(df.index))
    np_ohlc = izip(xax, f[cols[0]], f[cols[1]], f[cols[2]], f[cols[3]])
    return np_ohlc

def set_ax_format(ax, fig, tickers=None, xlabel=None, ylabel=None):
    if tickers is not None:
        ax = set_xlimit(ax, tickers)    
        def format_date(x, pos=None):
            if x<0 or x>len(tickers)-1:
                return ''
            return tickers[int(x)]    
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(format_date))    
        ax = set_xlocator(ax, tickers, fig)
    if xlabel is not None:
        ax.set_xlabel(xlabel)
    if ylabel is not None:
        ax.set_ylabel(ylabel)
    return ax

def _get_freq(w, l, u=50, s=5):
    '''
    w : figure pixel
    l : number of tickers
    u : one ticker in pixel
    s : search min l%freq via freq+s
    '''
    f = w//u
    d = l%f
    freq = f
    for i in range(s):
        if d > l%(f+i):
            d = l%(f+i)
            freq = f+i
    return freq

def set_xlocator(ax, tickers, fig):
    fig_width = fig.get_size_inches()[0] * fig.dpi
    num_tickers = len(tickers)
    freq = _get_freq(fig_width, num_tickers)
    if freq < num_tickers :
        ax.xaxis.set_major_locator(mticker.MaxNLocator(freq, prune='both'))
    return ax
    
def set_xlimit(ax, tickers):
    xax = np.arange(len(tickers))
    xmin = xax[0]-1
    xmax = xax[-1]+1
    ax.set_xlim(xmin, xmax)
    return ax

def zoom_yaxis(ax, f):
    '''
    f : zoom factor
    f = 0 : unchange
    f < 0 : zoom in
    f > 0 : zoom out
    '''
    l = ax.get_ylim()
    new_l = (l[0] + l[1])/2 + np.array((-0.5, 0.5)) * (l[1] - l[0]) * (1 + f)
    ax.set_ylim(new_l)
    return ax

def set_datetime_format(dt):
    freq_minutes = np.diff(dt).min().astype(float)/1000000000/60/60
    if freq_minutes < 24:
        datetime_format = '%Y\n%m-%d\n%H-%M'
    elif freq_minutes < 672:
        datetime_format = '%Y\n%m-%d'
    else:
        datetime_format = '%Y-%m'
    return datetime_format

def set_ticker(dt):
    datetime_format = set_datetime_format(dt)
    tickers = dt.strftime(datetime_format)
    return tickers

