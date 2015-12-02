#!/usr/bin/env python
#coding: UTF-8
import os, glob, numpy, gdal
import libUTM
from math import *
from scipy import stats
from matplotlib.pyplot import *

### Grid.py ###########################
# Managing `Grid` data
# e.g. Create, import/export via GDAL, fill blank nodes etc.
#######################################

class Grid:
    __c__ = 0
    def __init__(self, shape=(3,4), x0y0=(0.0,0.0), dxdy=(1.0,1.0), nodata=0):
        self.Z = numpy.zeros((shape[1],shape[0]), dtype=float)
        if nodata: self.Z += nodata
        self.nodata, self.shape = nodata, shape
        self.x0, self.y0 = x0y0[0], x0y0[1]
        self.x1, self.y1 = x0y0[0]+(shape[0]+1)*dxdy[0], x0y0[1]+(shape[1]+1)*dxdy[1]
        self.dx, self.dy = map(numpy.abs, dxdy)
        self.GT = (self.x0, self.dx, 0, self.y0, 0, -self.dy)
        self.Xs = numpy.array([self.x0+dxdy[0]*c for c in range(self.shape[0])])
        self.Ys = numpy.array([self.y0+dxdy[1]*c for c in range(self.shape[1])])

    def gdal_open(self, fname="tmp.tif", band=1):
        gdal.UseExceptions()
        if not os.path.exists(fname): print "[Error] File not exists: %s" % fname
        else: print "[Open] < %s" % fname
        ds = gdal.Open(fname)
        band = ds.GetRasterBand(band)
        DEM = band.ReadAsArray() ## Load as array
        self.GT = ds.GetGeoTransform() #x0, dx, dxdy, y0, dydx, dy
        self.__init__(shape=(band.XSize,band.YSize), x0y0=(self.GT[0],self.GT[3]), dxdy=(self.GT[1],self.GT[5]))
        self.Z = DEM
        return self
    def gdal_save(self, fname="tmp2.tif", driver="GTiff", band=1):
        ds = gdal.GetDriverByName(driver).Create(fname, self.shape[0],self.shape[1], band, gdal.GDT_Float32)
        ds.SetGeoTransform(self.GT)
        band = ds.GetRasterBand(band)
        band.SetNoDataValue(self.nodata)
        band.WriteArray(self.Z)
        print "[Save] > %s" % fname

    def nearest(self, x, y): return numpy.abs(self.Xs - x).argmin(), numpy.abs(self.Ys - y).argmin()
    def distance(self, x, y):
        ix, iy = self.nearest(x,y)
        dx, dy = (self.Xs[ix]-x), (self.Ys[iy]-y)
        return ix, iy, dx, dy

    def position(self, x, y):
        ix = numpy.where(self.Xs==x)[0]
        iy = numpy.where(self.Ys==y)[0]
        if(ix and iy): return ix,iy ## Return position in Zarray if hit the node
        else: return None ## Return None if missed the node
    def get(self, x, y):
        pos = self.position(x,y)
        if pos: return self.Z[pos[0],pos[1]]
        else:
            pos = self.nearest(x,y)
            return self.Z[pos[0],pos[1]]
    def set(self, x, y, z):
        pos = self.position(x,y)
        if pos: self.Z[pos[0],pos[1]] = z
        else: return None

    def xyz_save(self, fname="tmp.grd.xyz"):
        fw = open(fname, "w")
        [fw.write("%s %s %s\n" % (x,y,self.Z[iy,ix])) for ix,x in enumerate(self.Xs) for iy,y in enumerate(self.Ys)]
        fw.close(); print "[Save] > %s" % fname

    def info(self):
        print "Grid with %d x %d nodes:" % self.shape
        print "X: %f ~ %f" % (self.Xs[0],self.Xs[-1])
        print "Y: %f ~ %f" % (self.Ys[0],self.Ys[-1])
        print "Z: %f ~ %f" % (numpy.nanmin(self.Z),numpy.nanmax(self.Z))
        print "Cellsize: %f, %f" % (self.dx, self.dy)
        count_nan, count_all = numpy.sum(numpy.isnan(self.Z)), self.shape[0]*self.shape[1]
        print "%d out of %d nodes are NaN (%.3f%%)" % (count_nan, count_all, count_nan*100.0/count_all)

    def confidence(self, v=0.95, zrange=(-9999,9999)):
        Z2 = numpy.array([z for z in self.Z.flatten() if zrange[0]<=z<=zrange[1]], dtype=float)
        conf = stats.norm.interval(v, loc=numpy.mean(Z2), scale=numpy.std(Z2))
        return conf

    def histogram(self, bins=10):
        Zz = self.Z.flatten()
        print Zz.shape
        hist(Zz, bins=bins, log=True); show()


    def paste(self, G, overwrite=False, zrange=(-9999,9999)):
        ## Fill nodata with the other grid
        ## G should be the Grid object
        def fetch(x,y):
            ix,iy,dx,dy = G.distance(x,y)
            if(dx > self.shape[0]/2 or dy > self.shape[1]/2): return None
            z = G.Z[iy,ix]
            if(zrange[0] <= z <= zrange[1]): return z
            else: return None
        def put(ix,iy,x,y):
            self.__c__ += 1
            if(self.__c__%100000==0): print "%d%% ->" % (100*self.__c__/self.shape[0]/self.shape[1]),
            if(self.__c__%1000000==0): print "(%d / %d)" % (self.__c__, self.shape[0]*self.shape[1])
            if(numpy.isnan( self.Z[iy,ix] )):
                z = fetch(x,y)
                if(z): self.Z[iy,ix] = z
        self.__c__ = 0
        [put(ix,iy,x,y) for ix,x in enumerate(self.Xs) for iy,y in enumerate(self.Ys)]
        print "...OK"

    def fill_fromSelf(self):
        def search1(ix2,iy2):
            ixys = [(_ix_,_iy_) for _ix_ in [ix2-1,ix2,ix2+1] for _iy_ in [iy2-1,iy2,iy2+1]]
            ixys = [(_ix_,_iy_) for _ix_,_iy_ in ixys if 0<=_ix_<=self.shape[0]-1 and 0<=_iy_<=self.shape[1]-1]
            z = [self.Z[_iy_,_ix_] for _ix_,_iy_ in ixys]
            return z
        def put(ix1,iy1, threadshold, remove=False):
            self.__c__ += 1
            if(self.__c__%100000==0): print "%d%% ->" % (100*self.__c__/self.shape[0]/self.shape[1]),
            if(self.__c__%1000000==0): print "(%d / %d)" % (self.__c__, self.shape[0]*self.shape[1])
            if remove:
                zs = [z for z in search1(ix1,iy1) if not numpy.isnan(z) and z<>self.nodata]
                if(len(zs) <= threadshold): self.Z2[iy1,ix1] = numpy.nan; return True
            else:
                if numpy.isnan(self.Z2[iy1,ix1])==False or self.Z2[iy1,ix1]==self.nodata: return False ##Fill grid whenever it is Nodata
                zs = [z for z in search1(ix1,iy1) if not numpy.isnan(z) or z==self.nodata]
                if (threadshold <= len(zs)): self.Z2[iy1,ix1] = numpy.average(zs); return True
            return False
        print "[Fill from Self] Completing nodata nodes ..."
        #print "Pass 1/3: (Removing isolated nodes)"
        self.Z2 = self.Z[:]; self.__c__=0 #Threadshold: <=3
        #stats = sum([put(ix,iy,3, remove=True) for ix in range(self.shape[0]) for iy in range(self.shape[1])])
        #print "OK (%d pts removed)" % stats
        print "Pass 2/3: (Completing blank nodes)"
        #self.Z = self.Z2[:]; self.__c__=0 #Threadshold: 5<=
        stats = sum([put(ix,iy,5,remove=False) for ix in range(self.shape[0]) for iy in range(self.shape[1])])
        print "OK (%d pts completed)" % stats
        #print "Pass 3/3: (Removing isolated nodes)"
        #self.Z = self.Z2[:]; self.__c__=0 #Threadshold: <=4
        #stats = sum([put(ix,iy,4, remove=True) for ix in range(self.shape[0]) for iy in range(self.shape[1])])
        #print "OK (%d pts removed)" % stats
        self.Z = self.Z2[:]; self.__c__=0
