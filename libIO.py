#!/usr/bin/env python
#coding: UTF-8
import os, glob, numpy
from misc import *

class read:
    size_total, size_read = 0, 0
    buffer_size_bytes = 10**6 #1MB
    threadshold_filesize =5*10**6 #5MB
    verbose_interval1 = 10*10**6 #10MB
    verbose_interval2 =100*10**6 #100MB
    
    def __init__(self, fnames, delimiter=" ", verbose=True):
        self.fnames = fnames if isinstance(fnames,list) else [fnames]
        self.delimiter, self.verbose = delimiter, verbose
        for fname in self.fnames:
            if os.path.exists(fname)==False: print("[Error] File not found: "+fname)
        self.size_total = sum([os.path.getsize(fname) for fname in self.fnames])
        self.__bins1__ = range(0, self.size_total, self.verbose_interval1)
        self.__bins2__ = range(0, self.size_total, self.verbose_interval2)[1:]
    
    def a(self, dtype=float): ## Read ASCII XYZ file
        def read_and_parse(buff=True):
            #if(bound):
            #    if(buff):
            #        #return [xyz for xyz in [map(dtype, line.strip().split(self.delimiter)) for line in fr.readlines(self.buffer_size_bytes)] if self.__within__(xyz, bound)]
            #        for xyz in [map(dtype, line.strip().split(self.delimiter)) for line in fr.readlines(self.buffer_size_bytes)]:
            #            print xyz
            #            if self.__within__(xyz, bound): return xyz
            #    else:     return [xyz for xyz in [map(dtype, line.strip().split(self.delimiter)) for line in fr.readlines()] if self.__within__(xyz, bound)]
            #else:
            if(buff): X = [map(dtype, line.strip().split(self.delimiter)) for line in self.fr.readlines(self.buffer_size_bytes)]
            else:     X = [map(dtype, line.strip().split(self.delimiter)) for line in self.fr.readlines()]
            #if(bound): X = [xyz for xyz in X if self.__within__(xyz, bound)]
            return X
                
        #--------// work //-----------#
        for fname in self.fnames:
            self.fr = open(fname, "r"); print "\nLoading "+fname,
            ## If the filesize is small > Read it all
            if(os.path.getsize(fname) < self.threadshold_filesize):
                Chunk = read_and_parse(buff=False)
                yield numpy.array(Chunk, dtype)
            else: ## If the filesize is large > Read with instance
                Chunk = read_and_parse(buff=True)
                while Chunk:
                    #yield numpy.array(Chunk, dtype); self.size_read += self.buffer_size_bytes
                    ## Fall-back code ## Usually not required :(
                    try: yield numpy.array(Chunk, dtype); self.size_read += self.buffer_size_bytes
                    except ValueError:
                        errxyzs = [xyz for xyz in Chunk if len(xyz)<>3]
                        print "[ValueError] Rejected points: %s" % errxyzs
                        [Chunk.remove(errxyz) for errxyz in errxyzs]
                    if(self.verbose): self.__print_progress__()
                    Chunk = read_and_parse(buff=True)
            print "OK."; self.fr.close()
            
    def b(self, dtype=float): ## Read Binary XYZ file
        None
 
    def __within__(self, X, bound=None):
        if not bound: return True
        return all([bool(bound[0][axis]<>None and bound[1][axis]<>None and (bound[0][axis] <= x <= bound[1][axis])) for axis, x in enumerate(X)])
 
    def __print_progress__(self):
        if(self.__bins1__ and self.size_read > self.__bins1__[0]):
            print "%d%% -> " % (100.0 * self.__bins1__.pop(0) / self.size_total),
        if(self.__bins2__ and self.size_read > self.__bins2__[0]):
            print "(%d MB)" % (self.__bins2__.pop(0)/10**6)
            
class write:
    def __init__(self, fname, delimiter=" "):
        self.fname, self.delimiter = fname, delimiter
        self.fw = open(fname, "w")
    def a(self, Chunk):
        map(self.fw.write, [self.delimiter.join(map(str,items))+"\n" for items in Chunk])
                
    def close(self): self.fw.close()
        
