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

def getPath(variable, scenario, period):
	# TODO: add in variables to each string for changing RCP45/85 and historical
	# rcp time range: 2006-2099 historical: 1950-2005
	path = "macav2metdata_{0}_GFDL-ESM2G_r1i1p1_{1}_{2}_WUSA.nc"
	if(scenario == 'historical'):
		period = '2006-2099'
	else:
		period = '1950-2005'
	return path.format(variable, scenario, period)

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
	FUTURE_DATES = ['2006-2010', '2011-2015', '2016-2020', '2021-2025', '2026-2030',
			'2031-2035', '2036-2040', '2041-2045', '2046-2050', '2051-2055',
			'2056-2060', '2061-2065', '2066-2070', '2071-2075', '2076-2080',
			'2081-2085', '2086-2090', '2091-2095', '2095-2099']
	HISTORICAL_DATES = ['1950-1954', '1955-2959', '1960-1965', '1966-1970', '1971-1975',
			    '1976-1980', '1981-1985', '1986-1990', '1991-1995', '1996-2000',
			    '2001-2005']			
	for lat,lon in coordinates:
		df = pd.DataFrame() # create a new dataframe for eah
		# CREATE data handles
		for var,idx  in VAR_PATHS.items():
			# iterate through the netcdfs based on scenario
			if(scenario == 'historical'):
				dates = HISTORICAL_DATES
			else:
				dates = FUTURE_DATES
			for period in dates:
				
				fh = Dataset(getPath(var, scenario, period),'r',format="NETCDF4")# filehandle
				
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
					
				df[VAR_HEADER_MAP[var]].append(pd.Series(datah[time_index,lat_index,lon_index]))
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
		filename = "%s_%s_%s.csv" % (scenario, lat, lon)
		df.to_csv(data_dir+'/'+filename,index=False)
main()
