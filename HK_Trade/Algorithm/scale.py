# -*- coding: utf-8 -*-
"""
Created on Tue May  7 10:59:44 2019

@author: w
"""

def linear_scale(unscale_data, to_min, to_max, from_min, from_max):
    scale_data = (to_max - to_min) * (unscale_data - from_min) / (from_max - from_min) + to_min
    return scale_data