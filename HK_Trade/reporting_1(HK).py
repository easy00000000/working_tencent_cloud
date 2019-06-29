# -*- coding: utf-8 -*-
#########################################
# @author: YK
#
# inputs: 
# 1. weights at t+1 calc-ed based on t
# 2. transaction prices at t+1
# 3. asset historical prices
#
# outputs:
# 1. value and cash at date end
# 2. transaction results at t+1
# 3. performance results at date end
# 4. graph for values and weights
#########################################

import os
import sys
package_path = os.getcwd()
if package_path not in sys.path:
    sys.path.append(package_path)

import pandas as pd
from time import process_time
from Reporting.placement import est_transacton_prices
from Reporting.results import mapping, get_portfolio, get_pd
from Reporting.results import get_performance
from Reporting.display import get_filename
from Reporting.display import csv_performance, plot_performance
from Data.get_data import read_ticker

init_cash = 500000

# 1. load historical data in a dict and key is ticker
tickers=['SHY','2833']
tickers_pl = {}
for e in range(len(tickers)):
    tickers_pl[tickers[e]] = read_ticker(tickers[e])

# 2.1 load delta_shares from file
path = os.getcwd() + "\\Reporting\\results\\"
delta_shares_name = path + '1560837918(2014-2019).xlsx'
df = pd.read_excel(open(delta_shares_name,'rb'), sheet_name=0)
delta_s = df.copy()
delta_s.set_index("Date", inplace=True)
tickers = delta_s.columns

# 2.2 run back test to generate delta_shares
#start_time = process_time()
#delta_s = get_shares(tickers, tickers_pl, init_cash)
#print('2.2 Est Transaction Running Time: ', process_time()-start_time)

# 3. load transaction prices
# 3.1 scenario one: estimate transaction prices, transaction dates, shares at each t and cash at each t
start_time = process_time()
trans_dates, trans_prices, shares, residual_cashs \
    = est_transacton_prices(tickers, delta_s, tickers_pl, init_cash)
print('3.1 Est Transaction Running Time: ', process_time()-start_time)

# 3.2 scenario two: input transaction prices

# 4. Mapping - calc new value with new trades
# shares, cash and value at t = 0 at delta_s[0]'s date
# move date by date, calc value for each date
# if reach delta_s.date, read the delta_s and wait placement
# if placement, write transaction slip and update shares, cash and value
# move date by date
start_time = process_time()
mapping_date, mapping_shares, mapping_weights, \
    mapping_closes, mapping_cash, mapping_value = \
    mapping(tickers, delta_s, tickers_pl, init_cash, \
    trans_dates, trans_prices, shares, residual_cashs, 'D')
#print(mapping_value)
#print(mapping_cash)
portfolio = get_portfolio(tickers, mapping_date, \
    mapping_closes, mapping_cash, mapping_value)
weights = get_pd(tickers, mapping_date, mapping_weights)
print('4. Mapping Running Time: ', process_time()-start_time)
#
start_year = portfolio.index[0].year
end_year = portfolio.index[-1].year
csv_file = get_filename(start_year, end_year, 'csv', 'Reporting\\results')
annual_r, annual_std, total_r, sharpe_ratio, max_loss = get_performance(portfolio)
csv_performance(csv_file, 'w', portfolio, \
                total_r, annual_r, annual_std, sharpe_ratio, max_loss, 0)
# Performance for each year
for n in range(start_year, end_year+1):
    p_n = portfolio[portfolio.index.year==n]
    annual_r, annual_std, total_r, sharpe_ratio, max_loss = get_performance(p_n)
    csv_performance(csv_file, 'a', p_n, \
                    total_r, annual_r, annual_std, sharpe_ratio, max_loss)
fig_file = get_filename(start_year, end_year, 'jpg', 'Reporting\\results')
plot_performance(portfolio, weights, None, None, fig_file)