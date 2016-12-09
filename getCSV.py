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
import requests
from io import StringIO
"""
	1 = lat
	2 = lon
	3 = tasmin
	4 = tasmax
	5 = rhsmin
	6 = rhsmax
	7 = pr
	8 = scenario (rcp45 or rcp 85)
"""
URL = "http://climate-dev.nkn.uidaho.edu/Services/get-netcdf-data/?download-csv=True&request_lat_lon=False&lat={1}&lon={2}&positive-east-longitude=True&data-path=http://thredds.northwestknowledge.net:8080/thredds/dodsC/agg_macav2metdata_{3}_GFDL-ESM2M_r1i1p1_{8}_{9}_CONUS_daily.nc&variable=air_temperature&variable-name={3}_GFDL-ESM2M_{8}&data-path=http://thredds.northwestknowledge.net:8080/thredds/dodsC/agg_macav2metdata_{4}_GFDL-ESM2M_r1i1p1_{8}_{9}_CONUS_daily.nc&variable=air_temperature&variable-name={4}_GFDL-ESM2M_{8}&data-path=http://thredds.northwestknowledge.net:8080/thredds/dodsC/agg_macav2metdata_{5}_GFDL-ESM2M_r1i1p1_{8}_{9}_CONUS_daily.nc&variable=relative_humidity&variable-name={5}_GFDL-ESM2M_{8}&data-path=http://thredds.northwestknowledge.net:8080/thredds/dodsC/agg_macav2metdata_{6}_GFDL-ESM2M_r1i1p1_{8}_{9}_CONUS_daily.nc&variable=relative_humidity&variable-name={6}_GFDL-ESM2M_{8}&data-path=http://thredds.northwestknowledge.net:8080/thredds/dodsC/agg_macav2metdata_{7}_GFDL-ESM2M_r1i1p1_{8}_{9}_CONUS_daily.nc&variable={7}&variable-name=pr_GFDL-ESM2M_{8}"
	

CSV_HEADER_MAP = {
				'T_min':'tasmin_GFDL-ESM2M_rcp45(K)',
				'T_max':'tasmax_GFDL-ESM2M_rcp45(K)',
				'rhmin':'rhsmin_GFDL-ESM2M_rcp45(%)',
				'rhmax':'rhsmax_GFDL-ESM2M_rcp45(%)',
				'Precip(mm)':'pr_GFDL-ESM2M_rcp45(mm)'
			}

"""
	getUrl
	returns a formatted url for downloading the required csv.
	
	parameters
	----------
	lat: the latitude of the requested point
	lon: the longitude of the requested point
	scenario: the requested scenario rcp45 of 85
	historical : boolean value, decides requested time period
"""
def getUrl(lat, lon, scenario, period):
	if(historical):
		period = '1950_2005'
	else:
		period = '2006_2099'
	return URL.format(lat,lon'tasmin','tasmax','rhsmin','rhsmax','pr',scenario,period)

main():
	lat = 34.2
	lon = { -119.16}#, -119.04,-119.08,-119.12 }
	data_dir = "data"
	if not os.path.isdir(data_dir):
		os.mkdir(data_dir)
	
	
	
		for l in lon:
		
		fn = str(lat)+'_'+str(l)+'.csv'
		print('requesting data...')
		csv = requests.get(url.format(lat,l))
		f = open(data_dir+'/'+fn,'w')
		f.write(csv.text)
		f.close()

		df = pd.read_csv(data_dir+'/'+fn,header=15)
		#df = pd.read_csv(StringIO(csv.text), header=15)
		print(df.columns.values)
				
		df["Year"] = [ x[:4] for x in df['yyyy-mm-dd']]
		df["Month"] = [ x[5:7] for x in df['yyyy-mm-dd']]
		df["Day"] = [ x[-2:] for x in df['yyyy-mm-dd']]
		df["T_max"] = df[CSV_HEADER_MAP["T_max"]] - 273.15
		df["T_min"] = df[CSV_HEADER_MAP["T_min"]] - 273.15

		# calculate precipitation in cm and ave relative humidity.
		df["rh_ave"] = df[[CSV_HEADER_MAP['rhmax'], CSV_HEADER_MAP['rhmin']]].mean(axis=1)
		df["Precip(cm)"] = df[CSV_HEADER_MAP["Precip(mm)"]].multiply(10)
		df["T_ave"] = df[[CSV_HEADER_MAP['T_max'],CSV_HEADER_MAP['T_min']]].mean(axis=1)
		# remove unwanted data
		del df[CSV_HEADER_MAP["rhmax"]]
		del df[CSV_HEADER_MAP["rhmin"]]
		del df["yyyy-mm-dd"]
		
		# rename columns that we dont need to alter
		df['Precip(mm)'] = df[CSV_HEADER_MAP['Precip(mm)']]
		df = df[['Year','Month','Day','T_max','T_min','Precip(mm)','T_ave','Precip(cm)','rh_ave']]
		print("writing to %s" % fn)
		df.to_csv(data_dir+'/'+fn,index=False)
main()
