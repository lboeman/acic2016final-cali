# A script for re-projecting lat/lon coordinates written by Kyle Saxberg
# lots of hard coded thigns in here
import gdal
import numpy as np


def convertLatLon(geotrans, lat, lon):
	px = int((lon - geotrans[0]) / geotrans[1]) # x pixel
	py = int((lat - geotrans[3]) / geotrans[5]) # y pixel
	return px, py


def getMyMask(dbBand, geotrans, lat, lon):
	#TODO: fix hardcoding of masking values
	maskingValues = [21, 22, 23, 24]
	#TODO: fix assumptions on area questioning, ie threshold
	# geotrans = (xstart, xstep, ??, ystart, ??, ystep)
	px, py = convertLatLon(geotrans, lat, lon)
	
	# Single point 
	#intval = dbBand.ReadAsArray(px, py, 1, 1)
	#isItDevelopedPoint = False
	#if intval in maskingValues:
	#	isItDevelopedPoint = True
	
	# Over a small region
	# each single step in mask is ~120ft
	# this draws a ~ 1000x1000ft box over the lat/lon pair
	threshold = 30 
	boxOfInterest = dbBand.ReadAsArray(px-5, py-5, 10, 10)
	totalCount = 0
	isItDevelopedArea = False
	for i in boxOfInterest.flatten():
		if i in maskingValues:
			totalCount += 1
	if totalCount >= threshold:
		isItDevelopedArea = True
	return isItDevelopedArea
	

if __name__=="__main__":
	
	filename = "/home/cc/landCoverDataProjection"
	db = gdal.Open(filename)
	gt = db.GetGeoTransform()
	dbBand = db.GetRasterBand(1)
	geotrans = db.GetGeoTransform()

	latLons = "/home/acic2016final-cali/CaliforniaIDs.csv"
	with open(latLons) as f:
		header = f.readline()
		print(header.strip())
		for line in f:
			lat, lon = [float(x.strip()) for x in line.split(',')]
			if getMyMask(dbBand, geotrans, lat, lon):
				print(line.strip())

