# -*- coding: utf-8 -*-
"""
Author: easy00000000
Version: 0.02
Date: 2017-12-22
"""
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

def set_fig(w, h, rows=1, width_factor=3.0, height_factor=0.5, height_ratios=3):    
    if(w<0 or h<0):
        f_size = plt.gcf().get_size_inches()
        w = f_size[0]*width_factor
        h = f_size[1]*height_factor*(height_ratios+rows-1)
    fig = plt.figure(figsize=(w, h))
    fig.get_tight_layout()
    return fig

def get_rows(volume_col, sub_indicator_cols):
    rows = 1
    if volume_col != None:
        rows = rows + 1
    if sub_indicator_cols != None:
        rows = rows + 1
    return rows

def set_gs(rows, cols=1, height_ratios=3):
    if rows>1:
        hr = [height_ratios]
        for i in range(1,rows):
            hr.append(1)
    else:
        hr = None
    wr = None
    gs = gridspec.GridSpec(rows, cols, width_ratios=wr, height_ratios=hr, hspace=0)
    return gs