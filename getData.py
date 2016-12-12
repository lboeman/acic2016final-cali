"""
Gathers maca data using openDap
"""
import numpy as np
from netCDF4 import Dataset
from dateutil.parser import parse
from datetime import (datetime, timedelta)
import os
import pandas as pd
import argparse as parse

def getPath(input_dir, variable, scenario, period):
	# TODO: add in variables to each string for changing RCP45/85 and historical
	# rcp time range: 2006-2099 historical: 1950-2005
	path = "macav2metdata_{0}_GFDL-ESM2G_r1i1p1_{1}_{2}_CONUS_daily.nc"
	# 	macav2metdata_{0}_GFDL-ESM2G_r1i1p1_{1}_{2}_CONUS_daily.nc
	return input_dir+'/'+path.format(variable, scenario, period)

def main():
	start = datetime(1900, 1, 1)
	input_dir = "/mnt/store/one-model-data"
	data_dir = 'data'
	if not os.path.isdir(data_dir):
		print("Data directory does not exist")
		sys.exit(1)
	# needed vars: year, month, day,tmax, tmin, precip(mm),tave,precip(cm),rhave
	day = 1
	VAR_PATHS = {
			'tasmax':"air_temperature",
			'tasmin':"air_temperature",
			'pr':"precipitation",
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
	FUTURE_DATES = ['2006_2010', '2011_2015', '2016_2020', '2021_2025', '2026_2030',
			'2031_2035', '2036_2040', '2041_2045', '2046_2050', '2051_2055',
			'2056_2060', '2061_2065', '2066_2070', '2071_2075', '2076_2080',
			'2081_2085', '2086_2090', '2091_2095', '2096_2099']
	HISTORICAL_DATES = ['1950_1954', '1955_2959', '1960_1965', '1966_1970', '1971_1975',
			    '1976_1980', '1981_1985', '1986_1990', '1991_1995', '1996_2000',
			    '2001_2005']			
	scenario = 'rcp45'
	coordinates = pd.read_csv('SouthernCalifornia.csv')
	count = 0
	for i in coordinates.index:
		lat_target = coordinates.Lat[i]
		lon_target = 360 + float(coordinates.Lon[i])
		df = pd.DataFrame() # create a new dataframe for eah
		#set a boolean to know if we've already added time values
		time_added = False
		time_series = pd.Series()
		# CREATE data handles
		for var,idx  in VAR_PATHS.items():
			var_series = pd.Series()
			# iterate through the netcdfs based on scenario
			if scenario == 'historical' :
				dates = HISTORICAL_DATES
			else:
				dates = FUTURE_DATES
			for period in dates:
				fh = Dataset(getPath(input_dir, var, scenario, period),'r')# filehandle
				lath = fh.variables['lat']		# latitude handle
				lonh = fh.variables['lon']		# longitude handle
				timeh = fh.variables['time']		# time handle
				datah = fh.variables[idx] 		# handle on the 

				# extrace data
				time_length = len(timeh)		# get the number of records
				time_index = range(day-1, time_length, 1)  # step through the values one day at a time
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
					
				var_series = var_series.append(pd.Series(datah[time_index,lat_index,lon_index]))
				#if VAR_HEADER_MAP[var] in df.columns:
 					# TODO: build a series and concat them at the end of this loop.
				#	df[VAR_HEADER_MAP[var]] = pd.concat((df[VAR_HEADER_MAP[var]],pd.Series(datah[time_index,lat_index,lon_index])),axis=1)
				#else:
				#	df[VAR_HEADER_MAP[var]] = pd.Series(datah[time_index,lat_index,lon_index])
				if not time_added:
					time_series = time_series.append(pd.Series(time))
				fh.close()
				# End period loop
			if not time_added:
				df['time'] = time_series
			time_added=True
			# 		
			df[VAR_HEADER_MAP[var]] = var_series
			# end variable loop

		# Get a list of dates by adding their number of days post 1900,1,1
		days = [start+timedelta(days=int(x)) for x in df['time']]
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
		filename = "%s_%s_%s.csv" % (scenario, lat, float(lon-360))
		count = count + 1
		print("%s: Writing: %s" % (count, filename))
		df.to_csv(data_dir+'/'+filename,index=False)
main()
