#!/usr/bin/env python
#wget ftp://SteHo:'H0fa1510!!!!'@ftp.cloudsat.cira.colostate.edu/2B-CWC-RVOD.P1_R05/2012/220/*
# https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.griddata.html
from pyhdf.SD import SD, SDC
from pyhdf.HDF import *
from pyhdf.VS import *

import pprint

#----------------------------------------------------------------------------------------#

file_path = '/home/sh16450/Downloads/CLDCLASS_LIDAR/'
file_name = '2006220060015_01484_CS_2B-CLDCLASS-LIDAR_GRANULE_P1_R05_E01_F00.hdf'

#----------------------------------------------------------------------------------------#
# Get vdata info

f = HDF(file_path+file_name, SDC.READ)
vs = f.vstart()

data_info_list = vs.vdatainfo()

pprint.pprint( data_info_list )

vs.end() # terminate the vdata interface
f.close()

#----------------------------------------------------------------------------------------#
# Get latitude & longitude vdata

f = HDF(file_path+file_name, SDC.READ)
vs = f.vstart()

vdata_lat = vs.attach('Latitude')
vdata_long = vs.attach('Longitude')

lat = vdata_lat[:]
long = vdata_long[:]

print('Nb pixels: ', len(lat))
print('Lat min, Lat max: ',min(lat),max(lat))

pprint.pprint( vdata_lat.attrinfo() )

for i in range(15): # sample
    print(lat[i])

vdata_lat.detach() # "close" the vdata
vdata_long.detach() # "close" the vdata
vs.end() # terminate the vdata interface
f.close()

#----------------------------------------------------------------------------------------#
# Get SDS info

file = SD(file_path+file_name, SDC.READ)

pprint.pprint( file.info() )  # number of sds and metadata

#----------------------------------------------------------------------------------------#
# get all sds names

datasets_dic = file.datasets()

#for idx,sds in enumerate(datasets_dic.keys()):
#   print idx,sds

sds_dic = {}
for key, value in datasets_dic.items():
    #print key, value, value[3]
    sds_dic[value[3]] = key

pprint.pprint( sds_dic )

#----------------------------------------------------------------------------------------#
# get CPR_Cloud_mask

sds_obj = file.select('CloudPhase') # select sds

data = sds_obj.get()

sds_info = sds_obj.info()

print(sds_info )

pprint.pprint(sds_obj.attributes() )

print(data.shape )
