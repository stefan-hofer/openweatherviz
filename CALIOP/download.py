#!/usr/bin/env python
#wget ftp://SteHo:'H0fa1510!!!!'@ftp.cloudsat.cira.colostate.edu/2B-CWC-RVOD.P1_R05/2012/220/*
# https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.griddata.html
# http://www.cloudsat.cira.colostate.edu/sites/default/files/products/files/2B-CLDCLASS-LIDAR_PDICD.P_R04.20120522.pdf

from pyhdf.SD import SD, SDC
from pyhdf.HDF import *
from pyhdf.VS import *

import pprint

#----------------------------------------------------------------------------------------#

file_path = '/home/sh16450/Downloads/CALIOP/CLDCLASS_LIDAR/'
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
vdata_binsize = vs.attach('Vertical_binsize')
vdata_nclouds = vs.attach('ncloud:2B-CLDCLASS-LIDAR')
vdata_nbins = vs.attach('nbin:2B-CLDCLASS-LIDAR')
vdata_nray = vs.attach('nray:2B-CLDCLASS-LIDAR')
vdata_quality = vs.attach('Data_quality')
vdata_layers = vs.attach('Cloudlayer')

lat = vdata_lat[:]
long = vdata_long[:]
vbinsize = vdata_binsize[:]
nclouds = vdata_nclouds[:]
nbins = vdata_nbins[:]
nray = vdata_nray[:]
quality = vdata_quality[:]
layers = vdata_layers[:]


print('Nb pixels: ', len(lat))
print('Lat min, Lat max: ',min(lat),max(lat))

pprint.pprint( vdata_lat.attrinfo())

# for i in range(15): # sample
#     print(lat[i])

vdata_lat.detach() # "close" the vdata
vdata_long.detach() # "close" the vdata
vdata_binsize.detach() # "close" the vdata
vdata_nclouds.detach() # "close" the vdata
vdata_nbins.detach() # "close" the vdata
vdata_nray.detach() # "close" the vdata
vdata_quality.detach() # "close" the vdata
vdata_layers.detach()

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

phase_obj = file.select('CloudPhase') # select sds
height  = file.select('Height')
clfc = file.select('CloudFraction')
cl_type = file.select('CloudLayerType')
cl_base = file.select('CloudLayerBase')
cl_top = file.select('CloudLayerTop')

data_phase = phase_obj.get()
height_data = height.get()
clfc_data = clfc.get()
cltype_data = cl_type.get()
clbase_data = cl_base.get()
cltop_data = cl_top.get()


phase_info = phase_obj.info()
clfc_info = clfc.info()

print(phase_info )

pprint.pprint(phase_obj.attributes())

print(data_phase.shape)







# Cloud phase identified by using CALIPSO feature, temperature, and radar reflectivity1-ice, 2 mixed, 3-water

# The CloudFraction reports the fraction of lidar volumes in a radar resolution volume that containshydrometeors.
# It is recorded per ray and per bin as a 1-byte integer variable. It is a percentage from 0 to 100.

# Confidence level assigned to the cloud phase for each layer. It has a value ranging from 0 to 10. 10 indicates the highest confidence level.
# If confidence level is below 5, use the cloud phase with a caution.

# Cloud type for each layer. 0 = Not determined 1 = cirrus 2 = Altostratus
# 3 = Altocumulus 4 = St 5 = Sc 6= Cumulus 7 = Deep Convection 8 = Nimbostratus

# ---------------------------------------------------------------------------

import pandas as pd

df = pd.DataFrame()
