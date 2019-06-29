# -*- coding: utf-8 -*-
"""
Created on Fri May 10 15:32:26 2019

@author: w
"""

import numpy as np
from itertools import product
#from numba import jit 
# numba is not significant faster or even a lit bit slow

# structure weights matrix
def structure_weights_matrix(n_accurate, n_assets):
    w_m = [l for l in product(range(n_accurate+1), repeat=n_assets) if sum(l)==n_accurate]
    csv_filename = "weights_matrix_"+str(n_accurate)+"_"+str(n_assets)+".csv"
    np.savetxt(csv_filename, w_m, delimiter=",")
 
def get_risk_parity_weights(covariances, assets_risk_budget, n_accurate, n_assets, min_part=1):
    csv_filename = "weights_matrix_"+str(n_accurate)+"_"+str(n_assets)+".csv"
    weights_matrix = np.loadtxt(csv_filename, delimiter=",")
    w = np.array(weights_matrix)/n_accurate
    wj_cov = np.dot(covariances, w.T)
    wi_wj_cov = w.T*wj_cov
    var = np.sum(wi_wj_cov,axis=0)
    std = np.power(var,0.5)
    mc = (wi_wj_cov/std).T
    risk_budget = assets_risk_budget*np.repeat(std,n_assets,axis=0).reshape(len(std),n_assets)
    diff = np.power((mc-risk_budget),2)
    diff_sum = np.sum(diff, axis=1)
    min_idx = np.argsort(diff_sum)[:min_part]
    return w[min_idx].mean(axis=0), diff_sum[min_idx].mean(axis=0)