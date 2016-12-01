"""
Gathers maca data using openDap
"""
from netCDF4 import Dataset
import numpy as np
import pandas as pd

# TARGET DATA, adapt to change over time

day = 1
lat_target = 45.0
lon_target = 360-117.0

# needed vars: year, month, day,tmax, tmin, precip(mm),tave,precip(cm),rhave
# TODO: add in variables to each string for changing RCP45/85
path = "http://thredds.northwestknowledge.net:8080/thredds/dodsC/agg_macav1metdata_{}_GFDL-ESM2G_r1i1p1_rcp45_2006_2100_WUSA.nc"
VAR_PATHS = {
		'tasmax':"air_temperature",
		'tasmin':"air_temperature",
		'pr':"precipitation_flux",
		'rhsmax':"relative_humidity",
		'rhsmin':"relative_humidity",
	}
VAR_HEADER_MAP = {
		'tasmax':"tmax",
		'tasmin':"tmin",
		'pr':"precip(mm)",
		'rhsmax':"rhmax",
		'rhsmin':"rhmin",
		}
			
df = pd.DataFrame()
# CREATE data handles
for var,idx  in VAR_PATHS.items():
	fh = Dataset(path.format(var),'r',format="NETCDF4")	# filehandle
	lath = fh.variables['lat']		# latitude handle
	lonh = fh.variables['lon']		# longitude handle
	timeh = fh.variables['time']		# time handle
	datah = fh.variables[idx] 		# handle on the 

	# extrace data
	time_length = len(timeh)		# get the number of records
	time_index = range(day-1, time_length, 3650)  # step through the values one day at a time
	time = timeh[time_index]
	lat = lath[:]
	lon = lonh[:]
	
	# find the indices for the targer lat/lon
	lat_index =  np.searchsorted(lat,lat_target,side='left')
	lon_index =  np.searchsorted(lon,lon_target,side='left')
	# check bounds of lat/lon
	if(lat[lat_index]>lat_target):
		if(lat_index!=0):
			lat_index = lat_index - 1
	if(lat[lat_index]<lat_target):
		if(lat_index!=len(lat)):
			lat_index =lat_index +1
	if(lon[lon_index]>lon_target):
		if(lon_index!=0):
			lon_index = lon_index - 1
	if(lon[lon_index]<lon_target):
		if(lon_index!=len(lon)):
			lon_index = lon_index + 1
	lat=lat[lat_index]
	lon=lon[lon_index]
	
	
	df[VAR_HEADER_MAP[var]] = datah[time_index,lat_index,lon_index]
df.to_csv('daters.csv')
