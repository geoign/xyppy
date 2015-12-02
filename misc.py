#!/usr/bin/env python
#coding: UTF-8
import os, glob, numpy, gdal
from math import *

class Escape(Exception): pass

def nearest1D(self, X,xn):
    X = numpy.array(X)
    idx = (X - xn).argmin()
    distance = abs(X[idx] - xn)
    return idx, distance
def nearest2D(self, XY, x,y): 
    distances = (XY[:,0] - x)**2 + (XY[:,1] - y)**2
    idx = numpy.argmin(distances); distance = numpy.sqrt(distances[idx])
    return idx, distance

def atan2(self, dx, dy):
    #Convert dx and dy to degree with math.atan() and numpy.rad2deg
    dx = float(dx); dy = float(dy)
    if(dx > 0):
        if(dy==0): return 0.0
        if(dy>0): return numpy.rad2deg(atan(dy/dx)) #(+1,+1)
        else: return numpy.rad2deg(atan(dy/dx))+360 #(+1,-1)
    elif(dx < 0):
        if(dy==0): return 270.0
        if(dy>0): return numpy.rad2deg(atan(dy/dx))+180 #(-1,+1)
        else: return numpy.rad2deg(atan(dy/dx))+180 #(-1,-1)
    else: #dx==0
        return (90.0 if dy>0 else 270.0)

def within(self, X, boundary=None):
    # Check whether X is wihtin boundary.
    # $boundary should be [xmin,xmax,ymin,ymax,zmin,zmax] if $X is [x,y,z] 
    if not(boundary): return True
    if not(2*len(X) == len(boundary)):
        print "[Warn] Cannot bound X"; print X, boundary
        return True
    if not(isinstance(X, list)): X = [X]
    while boundary:
        x, minX, maxX = X.pop(0), boundary.pop(0), boundary.pop(0)
        if(minX and x <= minX): return False
        if(maxX and x >= maxX): return False
    return True

def outside(self, X, boundary=None):
    # Check whether X is in the outside of boundary.
    # $boundary should be [xmin,xmax,ymin,ymax,zmin,zmax] if $X is [x,y,z] 
    if not(boundary): return True
    if not(2*len(X) == len(boundary)):
        print "[Warn] Cannot bound X"; print X, boundary
        return True
    while boundary:
        x, minX, maxX = X.pop(0), boundary.pop(0), boundary.pop(0)
        if(minX and x >= minX): return False
        if(maxX and x <= maxX): return False
    return True