# -*- coding: utf-8 -*-
"""
Author: easy00000000
Version: 0.10
Date: 2018-01-04
"""

import numpy as np

def bi(h,l,interval=2,bench=None):
    # Initial peaks and bottoms
    if bench is None:
        p = _pk_(h,d=interval) #find potential peak
        b = _bt_(l,d=interval) #find potential bottom
    else:
        p = _pk_(bench,d=interval)
        b = _bt_(bench,d=interval)
    # Clean
    b = _mbt_(p,b) #remove multi bottoms
    p = _mpk_(p,b) #remove multi peaks
    b = _mbt2_(p,l) #identify lowest between 2 peaks
    p = _mpk2_(b,h) #identify highest between 2 bottoms
    bi = _mbi_(p,b,h,l) #start point and end point
    # Return Results
    return bi

def _mbi_(p,b,h,l):
    bi = p+b
    if bi[0] == 0:
        for i in range(1,len(bi)):
            if bi[i]>0:
                b[0] = -l[0]
                break
            if bi[i]<0:
                p[0] = h[0]
                break
    for i in range(len(bi)-1,0,-1):
        if bi[i]>0:
            pos = i
            m = l[i]
            for j in range(i,len(bi)):
                if l[j]<m:
                    m = l[j]
                    pos = j
            if pos>i:
                b[pos] = -l[pos]
            break
        if bi[i]<0:
            pos = i
            m = h[i]
            for j in range(i,len(bi)):
                if h[j]>m:
                    m = h[j]
                    pos = j
            if pos>i:
                p[pos] = h[pos]
            break
    mbi = p+b
    return mbi

def _mpk2_(b,h):
    mp = np.zeros(len(b))
    pos1 = 0
    for i in range(1,len(b)):        
        if b[i]<0:
            pos = pos1
            pos2 = i
            m = h[pos]
            for j in range(pos1+1,pos2):
                if h[j]>m:
                    m = h[j]
                    pos = j
            pos1 = pos2
            mp[pos] = h[pos]
    return mp
            
def _mbt2_(p,l):
    mb = np.zeros(len(l))
    pos1 = 0
    for i in range(1,len(p)):        
        if p[i]>0:
            pos = pos1
            pos2 = i
            m = l[pos]
            for j in range(pos1+1,pos2):
                if l[j]<m:
                    m = l[j]
                    pos = j
            pos1 = pos2
            mb[pos] = -l[pos]
    return mb

def _mbt_(p,b):
    pos1 = 0
    for i in range(1,len(p)):        
        if p[i]>0:
            pos = pos1
            pos2 = i
            b[pos] = 0.0
            m = 0.0
            for j in range(pos1+1,pos2+1):
                if b[j]<m:
                    b[pos] = 0.0
                    m = b[j]
                    pos = j
                elif b[j]<0:
                    b[j] = 0.0
            pos1 = pos2
    return b
            
def _mpk_(p,b):
    pos1 = 0
    for i in range(1,len(b)):        
        if b[i]<0:
            pos = pos1
            pos2 = i
            p[pos] = 0.0
            m = 0.0
            for j in range(pos1+1,pos2+1):
                if p[j]>m:
                    p[pos] = 0.0
                    m = p[j]
                    pos = j
                elif p[j]>0:
                    p[j] = 0.0
            pos1 = pos2
    return p 

def _pk_(h,d=2):
    p = np.zeros(len(h))
    for i in range(d,len(h)-d):        
        if  h[i]>h[i-d] and \
            h[i]>h[i-1] :
            p[i] = h[i]
    p[i] = h[i]
    return p

def _bt_(l,d=2):
    b = np.zeros(len(l))
    for i in range(d,len(l)-d):
        if  l[i]<l[i-d] and \
            l[i]<l[i-1] :
            b[i] = -l[i]
    b[i] = -l[i]
    return b