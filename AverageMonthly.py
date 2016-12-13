"""
	This Program takes in a directory of csv files formatted after a MoLS run through
	the output is a separate directory full of csv files containg the monthly averages
	from each csv in the input directory
"""

import sys
import os
import re

def getDataPoint (path , filename):



	filenameOut = "./Monthly_Avg_Csvs/"+filename +".monthly.csv"

	f = open(path+"/"+filename, 'r')
	if(not os.path.isdir('./Monthly_Avg_Csvs')):
		os.mkdir("Monthly_Avg_Csvs")

	fout = open(filenameOut, 'w+')


	T_max = 0
	T_min = 0
	PrecipMM = 0
	T_ave = 0
	PrecipCM = 0
	rh_ave = 0
	abun = 0
	num = 1

	line = f.readline()
	day = line.split(",")
	month = int(day[1])
	while (line != ""):
	    day  = line.split(",")
	    
	    if (day[1]!=str(month)): 
	    	
	    	if(day[1] == "1"):
	    		y = str(int(day[0])-1)
	    		mon = "13"
	    	else:
	    		y = day[0]
	    		mon = day[1]

	    	data = y+","+str(int(mon)-1)+","+str(day[2])+","+str(day[3])+","+str(day[4])+","+str(day[5])+","+str(day[6])+","+str(day[7])+","+str(day[8])+","+str(day[9])
	    	fout.write(data)
	    	year = day[0]
	        month = day[1]
	        T_max = 0
	        T_min = 0
	        PrecipMM = 0
	        T_ave = 0
	        precipCM = 0
	        rh_ave = 0
	        abun = 0
	    T_max += float(day[3])
	    T_min += float(day[4])
	    PrecipMM += float(day[5])
	    T_ave += float(day[6])
	    PrecipCM += float(day[7])
	    rh_ave += float(day[8])
	    abun += float(day[9])
	   
	    line = f.readline()

	data = str(day[0])+","+str(day[1])+","+str(day[2])+","+str(day[3])+","+str(day[4])+","+str(day[5])+","+str(day[6])+","+str(day[7])+","+str(day[8])+","+str(day[9])
	fout.write(data)

    

	    


def main ():
    path = sys.argv[1]
    fileNames = os.listdir(path)
    

    for x in fileNames:
    	getDataPoint (path, x)



main()








			
			


















       






