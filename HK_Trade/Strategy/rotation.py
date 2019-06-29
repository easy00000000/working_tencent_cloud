# -*- coding: utf-8 -*-
"""
Created on Wed May 22 09:53:46 2019

@author: w
"""
import numpy as np

# historical data to select Assets for next period
def select_assets(histp_series, dw=250, n_assets=3):
    pl = histp_series.dropna(axis=1) # 1:columns
    pct = pl.pct_change()
    corr = pct.corrwith(pct[pct.columns[0]])
    min_idx = np.argsort(corr)[:n_assets-1]
    return pct.columns[min_idx].values
    