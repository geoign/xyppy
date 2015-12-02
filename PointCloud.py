#!/usr/bin/env python
#coding: UTF-8
import os,numpy
import libIO, libUTM
from Grid import Grid

class PointCloud:
    __isfirst__ = True #For stats()
    extent, pts = [], 0
    def __init__(self, xyzfiles, delimiter=" "):
        self.xyzfiles, self.delimiter = xyzfiles, delimiter
        self.reset()
    def reset(self): self.input = libIO.read(self.xyzfiles, self.delimiter)

    def stats(self):
        def manipulator(XYZ):
            extmp = XYZ.min(axis=0), XYZ.max(axis=0) #Min,Max for x0,x1,x2
            self.pts += len(XYZ)
            if(self.__isfirst__):
                self.extent, self.__isfirst__ = extmp, False
            else:
                for axis in range(len(XYZ[0])):
                    if(self.extent[0][axis] > extmp[0][axis]): self.extent[0][axis] = extmp[0][axis]
                    if(self.extent[1][axis] < extmp[1][axis]): self.extent[1][axis] = extmp[1][axis]
            return XYZ
        self.__isfirst__ = True
        [manipulator(XYZ) for XYZ in self.input.a()]
        print "Extent of %d points:" % self.pts
        print "X: %f ~ %f" % (self.extent[0][0],self.extent[1][0])
        print "Y: %f ~ %f" % (self.extent[0][1],self.extent[1][1])
        print "Z: %f ~ %f" % (self.extent[0][2],self.extent[1][2])
        return self.extent

    def replace(self, outfile, new_delimiter=" "):
        output = libIO.write(outfile, new_delimiter)
        [output.a(XYZ) for XYZ in self.input.a()]
        output.close()

    def LL2UTM(self, outfile="tmp.xyz", LatLon=False):
        def converter(xyz):
            if(LatLon==True): Zone, Easting, Northing = libUTM.LLtoUTM(23,xyz[0],xyz[1])
            else: Zone, Easting, Northing = libUTM.LLtoUTM(23,xyz[1],xyz[0])
            return Easting, Northing, xyz[2]
        output = libIO.write(outfile)
        [output.a([converter(xyz) for xyz in XYZ]) for XYZ in self.input.a()]
        output.close()

    def UTM2LL(self, outfile="tmp.xyz", LatLon=False, Zone="52R"):
        def converter(xyz):
            lat, lon = libUTM.UTMtoLL(23,xyz[0],xyz[1], Zone)
            if(LatLon==True): return lat,lon,xyz[2]
            else: return lon,lat,xyz[2]
        output = xyppy.write(outfile)
        [output.a([converter(xyz) for xyz in XYZ]) for XYZ in self.input.a()]
        libIO.output.close()

class Gridding(PointCloud):
    def __init__(self, xyzfiles, bound=None, delimiter=" ", cellsize=(1.0,1.0), nodata=0):
        self.PCL = PointCloud(xyzfiles, delimiter)
        if bound: self.bound = bound
        else:
            if not self.PCL.extent: self.PCL.stats()
            self.bound = self.PCL.extent
        self.cellsize, self.nodata = cellsize, nodata
        self.x0y0 = self.bound[0][0], self.bound[0][1]
        self.xyrange = self.bound[1][0]-self.bound[0][0], self.bound[1][1]-self.bound[0][1]
        self.shape = int(numpy.ceil(self.xyrange[0]/self.cellsize[0])), int(numpy.ceil(self.xyrange[1]/self.cellsize[1]))
        print "Grid shape will be: %d x %d" % self.shape
        self.Density, self.Intensity, self.Gridded = None, None, None

    def __converter__(self, xyz, mode="both"):
        if not(self.__within__(xyz, self.bound)): return None
        x, y = xyz[0]-self.cellsize[0]/2.0, xyz[1]-self.cellsize[1]/2.0 #Shift to grid center
        ix,iy,dx,dy = self.Density.distance(x,y)
        if(dx<self.cellsize[0] and dy<self.cellsize[1]):
            if(mode=="density"): self.Density.Z[iy,ix] = self.Density.Z[iy,ix] + 1
            if(mode=="intensity"): self.Intensity.Z[iy,ix] = self.Intensity.Z[iy,ix] + xyz[2]
            if(mode=="both"):
                self.Density.Z[iy,ix] = self.Density.Z[iy,ix] + 1
                self.Intensity.Z[iy,ix] = self.Intensity.Z[iy,ix] + xyz[2]

    def __within__(self, X, bound=None):
        if not bound: return True
        return all([bool(bound[0][axis]<>None and bound[1][axis]<>None and (bound[0][axis] <= x <= bound[1][axis])) for axis, x in enumerate(X)])

    def density(self):
        print "[Density Grid]",; self.PCL.reset()
        self.Density = Grid(self.shape, self.x0y0, self.cellsize, self.nodata)
        [[self.__converter__(xyz, mode="density") for xyz in XYZ] for XYZ in self.PCL.input.a()]
        return self.Density

    def intensity(self):
        print "[Intensity Grid]",; self.PCL.reset()
        self.Intensity = Grid(self.shape, self.x0y0, self.cellsize, self.nodata)
        [[self.__converter__(xyz, mode="intensity") for xyz in XYZ] for XYZ in self.PCL.input.a()]
        return self.Intensity

    def make_grid(self):
        if not(self.Density): self.PCL.reset(); self.Density = Grid(self.shape, self.x0y0, self.cellsize, self.nodata)
        if not(self.Intensity): self.PCL.reset(); self.Intensity = Grid(self.shape, self.x0y0, self.cellsize, self.nodata)
        [[self.__converter__(xyz, mode="both") for xyz in XYZ] for XYZ in self.PCL.input.a()]
        print "[Grid = Intensity / Density] ...";
        self.Gridded = Grid(self.shape, self.x0y0, self.cellsize, self.nodata)
        self.Gridded.Z = self.Intensity.Z / self.Density.Z
        return self.Gridded

    def save(self, fname="tmp", ascii=False, binary=True):
        if(ascii):
            self.Density.xyz_save(fname+"_density.xyz")
            self.Intensity.xyz_save(fname+"_intensity.xyz")
            self.Gridded.xyz_save(fname+".xyz")
        if(binary):
            self.Density.gdal_save(fname+"_density.tif")
            self.Intensity.gdal_save(fname+"_intensity.tif")
            self.Gridded.gdal_save(fname+".tif")

    def info(self):
        if(self.PCL.extent): print self.PCL.extent
        if(self.Density): self.Density.info()
        if(self.Intensity): self.Intensity.info()
        if(self.Gridded): self.Gridded.info()
