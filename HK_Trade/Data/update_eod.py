# -*- coding: utf-8 -*-
"""
Created on Tue May 28 09:17:41 2019

@author: w
"""
import os
import sys
package_path = os.getcwd()
if package_path not in sys.path:
    sys.path.append(package_path)

#from Data.get_data import fetch_eod
from get_data import save_eod

etf_tickers=['SHY','SPY','XLB','XLC','XLE','XLF','XLI','XLK','XLP','XLRE','XLU','XLV','XLY']
#pl=fetch_eod(etf_tickers)
save_eod(etf_tickers)

hk_etf = ['7300', '2833']
save_eod(hk_etf, 'HK')