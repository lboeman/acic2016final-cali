"""
	Gdal masking script originally written by Kyle Saxberg
"""
# Script of gdal comands so far
import gdal
import numpy as np

#Working on these package imports
import osr
import ogr

# ----------------------------------------
# # Simple commands for manipulation of the dataset
#
# #Opening the only file in the data which can be opened by GDAL
# db = gdal.Open("nlcd_2011_landcover_2011_edition_2014_10_10.img")
# dbBand = db.GetRasterBand(1)
#    See the statistics: Min, Max, Mean, Stddev 
#    Negatively useful for our raster band
# dbBand.GetStatistics(True, True) 
#
#
# db.RasterXSize
# db.RasterYSize
# db.RasterCount
# 
# #The following fails for the projection type we have
# geotrans = db.GetGeoTransform()
# 
# bandtype = gdal.GetDataTypeName(dbBand.DataType)
# 
# # Read raster is the key, we can chose (xOffset, yOffset, xMax, yMax, xBufferSize, yBufferSize, datatype)
# # Meaning that the need to parse what offset means in the context of lat/long cordinates
# scaline = dbBand.ReadRaster(0, 0, dbBand.xSize, 1, dbBand.XSize, 1, dbBand.DataType)
# import struct
# vals = struct.unpack('b'*dbBand.XSize, scanline)
# # vals were all zero for first row of raster
# # Random sample of middle row yielded the appropriate assingment from landcover
# 


# ---------------------------------------
#  The method below was an attempt to convert point querry to the projection the dataset was already in.
#  This method encountered problems as the ogr module wanted EPSG csv files set to a GDAL_DATA location.

#  need to convert lat/lon to query projection
SourceEPSG = 5070
TargetEPSG = 4326

source = osr.SpatialReference()
source.ImportFromEPSG(SourceEPSG)

target = osr.SpatialReference()
target.ImportFromEPSG(TargetEPSG)

def CRSTransform(Lat, Long):
    transform = osr.CoordinateTransformation(source, target)
    #point = ogr.Geometry(ogr.wkbPoint)
    point = ogr.CreateGeometryFromWkt("POINT ("+Lat+" "+Long+")")
    #point.setPoint_2D(0, float(Long), float(Lat))
    point.Transform(transform)
    print(point.GetX() + "   " + point.getY())




#=========================================================================================
# Resources:

# associated gdal programs: https://github.com/dwtkns/gdal-cheat-sheet

# BASH STUFF
# Command used to warp image to the most commonly used lat/lon projection:
#gdalwarp -s_srs epsg:5070 -t_srs epsg:4326 nlcd_2011_landcover_2011_edition_2014_10_10.img convertedCover
#    The output file, convertedCover, is able to be loaded into QGIS and appears to have the right coordinates
#     what remains to be seen is iteration over this new matrix. 

# GDAL raster manipulation
#https://pcjericks.github.io/py-gdalogr-cookbook/raster_layers.html#get-raster-metadata
# Looking at creating a Driver for the information, "Converting an OGR file to Raster"
# Driver may be the key to abritrary iteration here. 



#=====================================
# helpful sites are helpful
# https://gis.stackexchange.com/questions/46893/getting-pixel-value-of-gdal-raster-under-ogr-point-without-numpy
filename = "convertedThing"

db = gdal.Open(filename)
gt = db.GetGeoTransform()
dbBand = db.GetRasterBand(1)

def getMyMask(dbBand, lat, lon):
    #TODO: Fix hardcoding of masking values
    #TODO: Fix Assumptions on Area questioning
    #Geotrans = (xstart, xstep, ???, ystart, ??, ystep)
    geotrans = db.GetGeoTransform()
    px, py = convertLatLon(geotrans, lat, lon)

    # Single Point 
    intval = dbBand.ReadAsArray(px, py, 1, 1)
    isItDevelopedPoint = False
    if inval in [21, 22, 23, 24]:
        isItDevelopedPoint = True

    # Average over an .... area
    #   each single step in mask is ~ 120ft
    #   draws 1000x1000 ft box over the lon/lat pair
    boxOfInterest = dbBand.ReadAsArray(px-5, py-5, 10, 10)
    totalCount = 0
    isItDevelopedArea = False
    for i in boxOfInterest.flatten():
        if i in [21, 22, 23, 24]:
            totalCount += 1
    if totalCount >= 25:
        isItDevelopedArea = True
    
    return isItDevelopedPoint

def convertLatLong(geotransform, lat, lon):
    px = int((lon - geotransform[0]) / geotransform[1]) # x pixel
    py = int((lat - geotransform[3]) / geotransform[5]) # y pixel
    
    return px, py
