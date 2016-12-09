"""
Gathers maca data using openDap
"""
from netCDF4 import Dataset
from dateutil.parser import parse
from datetime import (datetime, timedelta)
import os
import numpy as np
import pandas as pd
import argparse as parse

def main():
	start = datetime(1900, 1, 1)
	data_dir = "data"
	if not os.path.isdir(data_dir):
		os.mkdir(data_dir)
	# TARGET DATA, adapt to change over time
	day = 1
	longitude = 118.0
	lat_target = 34.02 # 45.0
	lon_target = 360 - longitude

	# needed vars: year, month, day,tmax, tmin, precip(mm),tave,precip(cm),rhave
	# TODO: add in variables to each string for changing RCP45/85
	path = "http://thredds.northwestknowledge.net:8080/thredds/dodsC/agg_macav1metdata_{}_GFDL-ESM2G_r1i1p1_{}_2006_2100_WUSA.nc"


	VAR_PATHS = {
			'tasmax':"air_temperature",
			'tasmin':"air_temperature",
			'pr':"precipitation_flux",
			'rhsmax':"relative_humidity",
			'rhsmin':"relative_humidity",
		}
	VAR_HEADER_MAP = {
			'tasmax':"T_max",
			'tasmin':"T_min",
			'pr':"Precip(mm)",
			'rhsmax':"rhmax",
			'rhsmin':"rhmin",
			}
				
	df = pd.DataFrame()
	# CREATE data handles
	for var,idx  in VAR_PATHS.items():
		# TODO: replace rcp45 with a cl argument
		fh = Dataset(path.format(var,"rcp45"),'r',format="NETCDF4")	# filehandle
		lath = fh.variables['lat']		# latitude handle
		lonh = fh.variables['lon']		# longitude handle
		timeh = fh.variables['time']		# time handle
		datah = fh.variables[idx] 		# handle on the 

		# extrace data
		time_length = len(timeh)		# get the number of records
		time_index = range(day-1, time_length, 2)  # step through the values one day at a time
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
		
		df[VAR_HEADER_MAP[var]] = pd.Series(datah[time_index,lat_index,lon_index])
	# Get a list of dates by adding their number of days post 1900,1,1
	days = [start+timedelta(days=int(x)) for x in time]
	# Get lists of year, month and day
	df["Year"] = [ day.year for day in days ]
	df["Month"] = [ day.month for day in days ]
	df["Day"] = [ day.day for day in days ]
	df["T_max"] = df["T_max"] - 273.15
	df["T_min"] = df["T_min"] - 273.15

	# calculate precipitation in cm and ave relative humidity.
	df["rh_ave"] = df[['rhmax', 'rhmin']].mean(axis=1)
	df["Precip(cm)"] = df["Precip(mm)"].multiply(10)
	df["T_ave"] = df[['T_max','T_min']].mean(axis=1)
	# remove unwanted data
	del df["rhmax"]
	del df["rhmin"]
	
	df = df[['Year','Month','Day','T_max','T_min','Precip(mm)','T_ave','Precip(cm)','rh_ave']]
	filename = "%s-%s.csv" % (lat,lon)
	df.to_csv(data_dir+'/'+filename,index=False)
main()
