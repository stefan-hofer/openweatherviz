# Download met dataset
# wget ftp://ftp.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/gfs.2018092206/gfs.t06z.pgrb2.0p25.f000


import xarray as xr
ds = xr.open_dataset("gfs.t06z.pgrb2.0p25.f000", engine="pynio")
temp = ds['TMP_P0_L1_GLL0']   # 2m temp
hgt_850 = ds["HGT_P0_L100_GLL0"].sel(lv_ISBL0=85000)
# temp.plot()
