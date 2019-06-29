# -*- coding: utf-8 -*-
"""
Created on Wed Jan 3 17:36:21 2018
@author: easy000000000
Modified on Sun Mar 3 2019
"""
# add to syspath
import os
import sys
package_path = os.getcwd()
if package_path not in sys.path:
    sys.path.append(package_path)

import pandas as pd

from KChart.plot_chart import plot_chart
from Algorithm.twinety import bi
from Algorithm.indicators import swt, ts_swt, ts_mean_std
from Algorithm.mkstatus import real_trend, est_trend_1
from Data.get_data import save_eod

# Load data
code = '0388'
hk_etf = [code]
save_eod(hk_etf, 'HK')
data_path = package_path + '\\'
source_data = pd.read_csv(data_path+code+'.csv', parse_dates=True, index_col=0)

# 准备测试数据
end_year = 2019
start_year = 2016
hist_p = source_data[source_data.index.year<=end_year]
hist_p = hist_p[hist_p.index.year>=start_year]
df = hist_p.copy() #[3:n]

# calc main_indicator
# Calc Bench (Wavelet) and Post_Bi
bi_level = 5
cA, cD = swt(df['Adj Close'],bi_level+1)
if 'High' in df.columns.values:
    df['bi_post'] = bi(df['High'],df['Low'],bench=cA[bi_level])
else:
    df['bi_post'] = bi(df['Adj Close'],df['Adj Close'],bench=cA[bi_level])
cA, cD = ts_swt(df['Adj Close'],bi_level+1)
df['wt_long'] = cA[bi_level]
df['wt_short'] = cA[bi_level-2]
df['diff_wt'] = (df['wt_short']/df['wt_long'] - 1)*10
# calc sub_indicator
df['real_trend'] = real_trend(df['bi_post'])
df['est_trend_1'], df['slope'] = est_trend_1(df['wt_long'], v=0.5)
df['zeros'] = 0
# mean-std
df['mean'], df['std'] = ts_mean_std(df['Adj Close'])
df['diff'] = 2*df['std']*df['std'] + df['mean']
df['est_trend_2'] = 0.0       
df.est_trend_2.loc[df['diff']<0] = -0.8
df.est_trend_2.loc[df['est_trend_1']>0] = 0.0
df.est_trend_2.loc[df['diff_wt']>0.5] = 0.8
df['risk'] = 1/df['std'] / 100
# select data to plot
df = df[df.index.year>=start_year+1]

# plot ohlc candlestick
plot_chart(df,
           sub_indicator_cols=['est_trend_2', 'diff_wt', 'zeros'],
           bi_cols=['bi_post']
           )
