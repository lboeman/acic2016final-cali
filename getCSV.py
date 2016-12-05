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
def main():
	lat = 34.2
	lon = { -119.16}#, -119.04,-119.08,-119.12 }
	data_dir = "data"
	if not os.path.isdir(data_dir):
		os.mkdir(data_dir)
	
	CSV_HEADER_MAP = {
				'T_min':'tasmin_GFDL-ESM2M_rcp45(K)',
				'T_max':'tasmax_GFDL-ESM2M_rcp45(K)',
				'rhmin':'rhsmin_GFDL-ESM2M_rcp45(%)',
				'rhmax':'rhsmax_GFDL-ESM2M_rcp45(%)',
				'Precip(mm)':'pr_GFDL-ESM2M_rcp45(mm)'
			}
	url = "http://climate-dev.nkn.uidaho.edu/Services/get-netcdf-data/?download-csv=True&request_lat_lon=False&lat={}&lon={}&positive-east-longitude=True&data-path=http://thredds.northwestknowledge.net:8080/thredds/dodsC/agg_macav2metdata_tasmin_GFDL-ESM2M_r1i1p1_rcp45_2006_2099_CONUS_daily.nc&variable=air_temperature&variable-name=tasmin_GFDL-ESM2M_rcp45&data-path=http://thredds.northwestknowledge.net:8080/thredds/dodsC/agg_macav2metdata_tasmax_GFDL-ESM2M_r1i1p1_rcp45_2006_2099_CONUS_daily.nc&variable=air_temperature&variable-name=tasmax_GFDL-ESM2M_rcp45&data-path=http://thredds.northwestknowledge.net:8080/thredds/dodsC/agg_macav2metdata_rhsmin_GFDL-ESM2M_r1i1p1_rcp45_2006_2099_CONUS_daily.nc&variable=relative_humidity&variable-name=rhsmin_GFDL-ESM2M_rcp45&data-path=http://thredds.northwestknowledge.net:8080/thredds/dodsC/agg_macav2metdata_rhsmax_GFDL-ESM2M_r1i1p1_rcp45_2006_2099_CONUS_daily.nc&variable=relative_humidity&variable-name=rhsmax_GFDL-ESM2M_rcp45&data-path=http://thredds.northwestknowledge.net:8080/thredds/dodsC/agg_macav2metdata_pr_GFDL-ESM2M_r1i1p1_rcp45_2006_2099_CONUS_daily.nc&variable=precipitation&variable-name=pr_GFDL-ESM2M_rcp45"
	for l in lon:
		fn = str(lat)+'_'+str(l)+'.csv'
		print('requesting data...')
		csv = requests.get(url.format(lat,l))
		#f = open(data_dir+'/'+fn,'w')
		#print(csv.text,file=f)
		#f.close()

		#df = pd.read_csv(data_dir+'/'+fn, comment='#',header=15)
		df = pd.read_csv(StringIO(csv.text), header=15)
		
				
		df["Year"] = df['yyyy-mm-dd'][:3]
		df["Month"] = df['yyyy-mm-dd'][5:7]
		df["Day"] = df['yyyy-mm-dd'][:-2]
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
		df.rename(columns({CSV_HEADER_MAP['Precip(mm)']:'Precip(mm)'}))
		df = df[['Year','Month','Day','T_max','T_min','Precip(mm)','T_ave','Precip(cm)','rh_ave']]
		print("writing to %s" % fn)
		df.to_csv(data_dir+'/'+fn,index=False)
main()
