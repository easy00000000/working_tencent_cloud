# -*- coding: utf-8 -*-
"""
Created on Mon May  6 21:19:27 2019

@author: w
"""
import numpy as np
from itertools import product
from scipy.optimize import minimize
TOLERANCE = 1e-10

def _allocation_risk(weights, covariances):

    # We calculate the risk of the weights distribution
    portfolio_risk = np.sqrt((weights * covariances * weights.T))[0, 0]

    # It returns the risk of the weights distribution
    return portfolio_risk

def _assets_risk_contribution_to_allocation_risk(weights, covariances):

    # We calculate the risk of the weights distribution
    portfolio_risk = _allocation_risk(weights, covariances)

    # We calculate the contribution of each asset to the risk of the weights
    # distribution
    assets_risk_contribution = np.multiply(weights.T, covariances * weights.T) \
        / portfolio_risk

    # It returns the contribution of each asset to the risk of the weights
    # distribution
    return assets_risk_contribution

def _risk_budget_objective_error(weights, args):

    # The covariance matrix occupies the first position in the variable
    covariances = args[0]

    # The desired contribution of each asset to the portfolio risk occupies the
    # second position
    assets_risk_budget = args[1]

    # We convert the weights to a matrix
    weights = np.matrix(weights)

    # We calculate the risk of the weights distribution
    portfolio_risk = _allocation_risk(weights, covariances)

    # We calculate the contribution of each asset to the risk of the weights
    # distribution
    assets_risk_contribution = \
        _assets_risk_contribution_to_allocation_risk(weights, covariances)

    # We calculate the desired contribution of each asset to the risk of the
    # weights distribution
    assets_risk_target = \
        np.asmatrix(np.multiply(portfolio_risk, assets_risk_budget))

    # Error between the desired contribution and the calculated contribution of
    # each asset
    error = \
        sum(np.square(assets_risk_contribution - assets_risk_target.T))[0, 0]

    # It returns the calculated error
    return error

def get_risk_parity_weights(covariances, assets_risk_budget, initial_weights):

    # Restrictions to consider in the optimisation: only long positions whose
    # sum equals 100%
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1.0},
                   {'type': 'ineq', 'fun': lambda x: x})

    # Optimisation process in scipy
    optimize_result = minimize(fun=_risk_budget_objective_error,
                               x0=initial_weights,
                               args=[covariances, assets_risk_budget],
                               method='SLSQP',
                               constraints=constraints,
                               tol=TOLERANCE,
                               options={'disp': False})

    # Recover the weights from the optimised object
    weights = optimize_result.x

    # It returns the optimised weights
    return weights

def get_risk_parity_brute(covariances, grid, mc_budget):
    weights_grid = [l for l in product(range(grid+1), repeat=len(mc_budget)) if sum(l)==grid]
    ws = np.array(weights_grid)/grid
    diff_min = 100.0
    w_choice = None
    for w0 in ws:        
        w = get_risk_parity_weights(covariances, mc_budget, w0)
        wj_cov = np.dot(covariances, w.T)
        wi_wj_cov = w.T*wj_cov
        var = np.sum(wi_wj_cov,axis=0)
        std = np.power(var,0.5)
        mc = (wi_wj_cov/std).T
        risk_budget = np.multiply(mc_budget,std)
        diff = np.power((mc-risk_budget),2)
        diff_sum = np.sum(diff)
        if diff_min > diff_sum:
            w_choice = w
            diff_min = diff_sum
    return w_choice #, diff_min