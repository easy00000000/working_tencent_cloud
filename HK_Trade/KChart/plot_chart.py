# -*- coding: utf-8 -*-
"""
Author: easy00000000
Version: 0.31
Date: 2018-01-04
"""
import matplotlib.pyplot as plt
from KChart import figure
from KChart import formatter as fmt
from KChart import plotter

# Plot Candlestick or Line
def plot_chart(df, 
               figsize_width=-1, figsize_height=-1, 
               main_indicator_cols=None, 
               volume_col=None, 
               sub_indicator_cols=None,
               bi_cols=None,
               ): 
    
    # Set rows of figure
    rows = figure.get_rows(volume_col, sub_indicator_cols)
    cols = 1
    
    # Set figure and gridspec
    fig = figure.set_fig(figsize_width, figsize_height, rows=rows)
    gs = figure.set_gs(rows, cols=cols)
    
    # Set ax_%%%
    ax_main = fig.add_subplot(gs[0, 0])
    plt.setp(ax_main.get_xticklabels(), rotation=0)
    ax_vol = None
    ax_sub = None
    if volume_col is not None:
        ax_vol = fig.add_subplot(gs[1, 0], sharex=ax_main)
        plt.setp(ax_main.get_xticklabels(), visible=False)
        if sub_indicator_cols is not None:
            ax_sub = fig.add_subplot(gs[2, 0], sharex=ax_main)
            plt.setp(ax_vol.get_xticklabels(), visible=False)
    else:
        if sub_indicator_cols is not None:
            ax_sub = fig.add_subplot(gs[1, 0], sharex=ax_main)
            plt.setp(ax_main.get_xticklabels(), visible=False)

    # Plot Main Figure        
    # Set Axis     
    date_tickers = fmt.set_ticker(df.index) #strftime('%Y\n%m-%d')
    ax_main = fmt.set_ax_format(ax_main, fig, tickers=date_tickers, ylabel='Price') 
    if 'High' in df.columns.values:
        # Structure ohlc data
        ohlc_cols=['open', 'high', 'low', 'close']
        np_ohlc = fmt.format_ohlc(df, formated_cols=ohlc_cols)
        # ---
        # Plot ohlc
        plotter.plot_ohlc(ax_main, np_ohlc)
    else:
        plotter.plot_y(ax_main, df['Adj Close'].values, linewidth=2)
    # ---
    if main_indicator_cols is not None: 
        for i, col in enumerate(main_indicator_cols):
            plotter.plot_y(ax_main, df[col].values, label=main_indicator_cols[i])
    # --- 
    # Plot Bi
    if bi_cols is not None:
        # lines
        lw = ['1.','0.8','0.6','0.6','0.6','0.6']
        ls = ['-','--','--','--','--','--']
        color = ['black','blue','red','blue','blue','blue']
        for i, col in enumerate(bi_cols):
            if i<len(lw):
                plotter.plot_bi(ax_main, df[col].values, label=bi_cols[i], lw=lw[i], ls=ls[i], color=color[i])
    
    # Plot Volume Figure
    if ax_vol is not None:
        # Set Axis
        vs = fmt.dec(min(df[volume_col].values))
        vol_label = 'Volume (' + '{:1.0e}'.format(vs) + ')'
        ax_vol = fmt.set_ax_format(ax_vol, fig, ylabel=vol_label)
        # ---
        for i, col in enumerate(volume_col):
            plotter.plot_bar(ax_vol, df[col].values/vs)
        # ---
        ax_vol = fmt.zoom_yaxis(ax_vol, 0.1)
        
    # Plot Sub_Indicator Figure
    if ax_sub is not None:
        # Set Axis
        ax_sub = fmt.set_ax_format(ax_sub, fig, ylabel='Indicator')
        # ---
        for i, col in enumerate(sub_indicator_cols):
            plotter.plot_y(ax_sub, df[col].values, label=sub_indicator_cols[i])
        # ---
        ax_sub = fmt.zoom_yaxis(ax_sub, 0.1)
    