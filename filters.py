#!/usr/bin/env python
#coding: UTF-8
import numpy, libUTM
from misc import *

def stats(Chunk):
    ## Get min and max of Chunk for each dimensions
    minmaxs = numpy.array([[Chunk[:,c].min(), Chunk[:,c].max()] for c in range(len(Chunk[0,:]))])
    return minmaxs.flatten()
    
def swaprow(Block, order=[1,0,2]):
    return Block[:,order]

def bool_crop(xyz, boundary=None):
    return within(xyz, boundary)
def bool_mask(xyz, boundary=None):
    return outside(xyz, boundary)

    
def conv_UTM2LL(xyz, zone="52R"):
    lat, lon = libUTM.UTMtoLL(23,xyz[0],xyz[1],zone) #23: WGS84
    return [lon, lat, xyz[2]]
    
def conv_LL2UTM(xyz):
    zone, easting, northing = libUTM.LLtoUTM(23, xyz[1],xyz[0])
    return [easting, northing, xyz[2]]
    
def conv_flipLon(xyz, makee_positive=True):
    ## Useful to make a grid covers International Date Line: -178.5 => 181.5
    if(make_positive==True and XYZ[0]<0): xyz[0]+=360
    if(make_positive==False and XYZ[0]>0): xyz[0]-=360
    return xyz
    
def conv_JAMbathy(items, flipZ=True):
    ## For to process fixed delimited JAMSTEC bathyemtry file
    try:
        while True: items.remove("")
    except ValueError:
        if(len(items)==3):
            xyz = map(float, items)
            if(flipZ): xyz[2]*=-1
            return xyz
        else: print "[Warn] Line is unlike XYZ: "+line; return None
    return None
