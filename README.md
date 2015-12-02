# xyppy
Library for processing gigabytes of XYZ data.

Maintained by Fumi "GeoIGN" Ikegami at University of Tasmania
Licensed under MIT License.

Contact:
f.ikegami at gmail.com or @geoign @fikgm in Twitter

----------------------------------------------------------
There are numerous tools to create a topographic grid file from scatter xyz points (e.g. xyz2grd in GMT).
However, they are usually designed for Megabytes of such data, which can be fit well within the memory.
xyppy allows to make a grid file from gigabytes or even terabytes of data. This is the main purpose for of the development.

Creating a grid is not the only function of the xyppy.
xyppy is primarily develped for marine geologits and geophysicists, which are often required to struggle with the bathymetry data like the followings:
1. Multiple overlapping data with different quality
2. Bad grid data with a lot of blank nodes
3. ASCII data with unknown size or extent

xyppy also provides some advanced interfaces to make the evaluation and handling of such data easier.
Despite xyppy is written in python, it is quite hard-coded in its I-O in order to get the great performance.
It is sometimes 10000000000x faster than your "easy programming". (WARNING: The number is a bluff)

Anyway, it is awesome. 

End.
----------------------------------------------------------

Usage: 

Coming soon in the next geological epoch :)

----------------------------------------------------------
