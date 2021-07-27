#!/usr/bin/env python
import argparse, os, time, datetime
import pandas as pd
import numpy as np
import netCDF4 as nc
import pylab as pl

# LEMS class
class LEMS(object):

    # initialization
    def __init__(self,datafile, window):

        print("[LEMS] \t Reading LEMS file: %s"%datafile)

        # read the csv output file and combine date/time columns
        self.data = pd.read_csv(datafile,
                                parse_dates={"date":["Year","Month","Date","Hour","Minute","Second"]},
                                date_parser=self.parse)

        # date
        self.date = [t.to_pydatetime() for t in self.data['date']]
        self.nt   = len(self.date)

        # battery level
        self.battery_level = self.data['Bat_Lvl'].rolling(window).mean()
        
        # temperature
        self.T_sfc_ir = self.data['MLX_IR_C'].rolling(window).mean()
        self.T_sfc_am = self.data['MLX_Amb_C'].rolling(window).mean()
        self.T_air_am = self.data['SHT_Amb_C'].rolling(window).mean()
        self.T_soil_u = self.data['Upper_Soil_Temp'].rolling(window).mean()
        self.T_soil_l = self.data['Lower_Soil_Temp'].rolling(window).mean()
        self.T_bmp_am = self.data['BMP_Amb'].rolling(window).mean()
        self.T_anemom = self.data['Sonic_Tmp'].rolling(window).mean()

        # moisture
        self.relh_air = self.data['SHT_Hum_Pct'].rolling(window).mean()
        self.q_soil_u = self.data['Upper_Soil_Mois'].rolling(window).mean()
        self.q_soil_l = self.data['Lower_Soil_Mois'].rolling(window).mean()
        
        # wind
        self.wind_spd = self.data['Sonic_Spd']
        self.wind_dir = self.data['Sonic_Dir']
        self.winducom = (-self.data['Sonic_Spd']*np.sin(np.pi*self.data['Sonic_Dir']/180.)).rolling(window).mean()
        self.windvcom = (-self.data['Sonic_Spd']*np.cos(np.pi*self.data['Sonic_Dir']/180.)).rolling(window).mean()
        self.wind_spd = np.sqrt(self.winducom**2 + self.windvcom**2)
        self.wind_dir = (270-np.rad2deg(np.arctan2(self.windvcom,self.winducom)))%360
        self.wind_gst = self.data['Sonic_Gst'].rolling(window).mean()

        # pressure
        self.pressure = self.data['Pressure'].rolling(window).mean()
        
        # insolation
        self.radsolar = self.data['Sunlight'].rolling(window).mean()

    # function to write data to netcdf
    def to_netcdf(self,outfile,ts=None,tf=None):
        
        print("[LEMS] \t Writing netCDF4 version: %s"%outfile)

        # create output file
        self.outfile             = nc.Dataset(outfile,'w')
        self.outfile.description = "LEMS output file"
        self.outfile.source      = "Jeremy A. Gibbs"
        #self.outfile.history     = "Created " + time.ctime(time.time())
        
        # starting time index
        tsid = 0
        if ts:
            tsid = self.nearest_ind(self.date,ts)
        
        # ending time index
        tfid = self.nt-1
        if tf:
            tfid = self.nearest_ind(self.date,tf)
        
        # get string date of starting time
        ts_str = self.date[tsid].strftime("%Y-%m-%d %H:%M:%S")
        
        # add time dimension
        ntimes = tfid-tsid + 1
        self.outfile.createDimension('t',ntimes)

        # add variables
        ncvar           = self.outfile.createVariable('time', "f8", ("t",))
        ncvar.long_name = "time"
        ncvar.units     = 'seconds since %s'%ts_str
        times           = nc.date2num(self.date[tsid:tfid+1], units=ncvar.units, calendar = 'standard')
        ncvar[:]        = times

        # temperature
        ncvar           = self.outfile.createVariable('T_sfc_ir', "f8", ("t",))
        ncvar.long_name = "IR surface temperature"
        ncvar.units     = "C"
        ncvar.setncattr("instrument","MLX")
        ncvar[:]        = self.T_sfc_ir[tsid:tfid+1]

        ncvar           = self.outfile.createVariable('T_sfc_am', "f8", ("t",))
        ncvar.long_name = "ambient surface temperature"
        ncvar.units     = "C"
        ncvar.setncattr("instrument","MLX")
        ncvar[:]        = self.T_sfc_am[tsid:tfid+1]

        ncvar           = self.outfile.createVariable('T_air_sht', "f8", ("t",))
        ncvar.long_name = "ambient air temperature from SHT"
        ncvar.units     = "C"
        ncvar.setncattr("instrument","SHT")
        ncvar.setncattr("level","1.5 m AGL")
        ncvar[:]        = self.T_air_am[tsid:tfid+1]

        ncvar           = self.outfile.createVariable('T_air_son', "f8", ("t",))
        ncvar.long_name = "ambient air temperature from sonic anemometer"
        ncvar.units     = "C"
        ncvar.setncattr("instrument","sonic")
        ncvar.setncattr("level","2 m AGL")
        ncvar[:]        = self.T_anemom[tsid:tfid+1]

        ncvar           = self.outfile.createVariable('T_air_bmp', "f8", ("t",))
        ncvar.long_name = "ambient air temperature from BMP pressure sensor"
        ncvar.units     = "C"
        ncvar.setncattr("instrument","BMP")
        ncvar.setncattr("level","1 m AGL")
        ncvar[:]        = self.T_bmp_am[tsid:tfid+1]

        ncvar           = self.outfile.createVariable('T_soil_u', "f8", ("t",))
        ncvar.long_name = "soil temperature (upper)"
        ncvar.units     = "C"
        ncvar.setncattr("instrument","5TM")
        ncvar.setncattr("level","5 cm BGL")
        ncvar[:]        = self.T_soil_u[tsid:tfid+1]

        ncvar           = self.outfile.createVariable('T_soil_l', "f8", ("t",))
        ncvar.long_name = "soil temperature (lower)"
        ncvar.units     = "C"
        ncvar.setncattr("instrument","5TM")
        ncvar.setncattr("level","50 cm BGL")
        ncvar[:]        = self.T_soil_l[tsid:tfid+1]

        # moisture
        ncvar           = self.outfile.createVariable('r_air_sht', "f8", ("t",))
        ncvar.long_name = "relative humidity of air"
        ncvar.units     = "%"
        ncvar.setncattr("instrument","SHT")
        ncvar.setncattr("level","1.5 m AGL")
        ncvar[:]        = self.relh_air[tsid:tfid+1]

        ncvar           = self.outfile.createVariable('q_soil_u', "f8", ("t",))
        ncvar.long_name = "volumetric soil water content (upper)"
        ncvar.units     = "m3 m-3"
        ncvar.setncattr("instrument","5TM")
        ncvar.setncattr("level","5 cm BGL")
        ncvar[:]        = self.q_soil_u[tsid:tfid+1]

        ncvar           = self.outfile.createVariable('q_soil_l', "f8", ("t",))
        ncvar.long_name = "volumetric soil water content (lower)"
        ncvar.units     = "m3 m-3"
        ncvar.setncattr("instrument","5TM")
        ncvar.setncattr("level","50 cm BGL")
        ncvar[:]        = self.q_soil_l[tsid:tfid+1]

        # wind
        ncvar           = self.outfile.createVariable('wind_spd', "f8", ("t",))
        ncvar.long_name = "wind speed from sonic"
        ncvar.units     = "m s-1"
        ncvar.setncattr("instrument","sonic")
        ncvar.setncattr("level","2 m AGL")
        ncvar[:]        = self.wind_spd[tsid:tfid+1]

        ncvar           = self.outfile.createVariable('wind_gst', "f8", ("t",))
        ncvar.long_name = "wind gust from sonic"
        ncvar.units     = "m s-1"
        ncvar.setncattr("instrument","sonic")
        ncvar.setncattr("level","2 m AGL")
        ncvar[:]        = self.wind_gst[tsid:tfid+1]

        ncvar           = self.outfile.createVariable('wind_dir', "f8", ("t",))
        ncvar.long_name = "wind direction from sonic"
        ncvar.units     = "deg"
        ncvar.setncattr("instrument","sonic")
        ncvar.setncattr("level","2 m AGL")
        ncvar[:]        = self.wind_dir[tsid:tfid+1]
       
        # pressure
        ncvar           = self.outfile.createVariable('pressure', "f8", ("t",))
        ncvar.long_name = "pressure from BMP sensor"
        ncvar.units     = "hPa"
        ncvar.setncattr("instrument","BMP")
        ncvar.setncattr("level","1 m AGL")
        ncvar[:]        = self.pressure[tsid:tfid+1]
        
        # insolation
        ncvar           = self.outfile.createVariable('radsolar', "f8", ("t",))
        ncvar.long_name = "incoming solar radiation"
        ncvar.units     = "W m-2"
        ncvar.setncattr("instrument","LiCor")
        ncvar.setncattr("level","2m AGL")
        ncvar[:]        = self.radsolar[tsid:tfid+1]
        
    # utlity function to format date/time for Pandas
    def parse(self, year, month, day, hour, minute, second):
        return year+ '-' +month+ '-' +day+ ' ' +hour+ ':' +minute+ ':' +second
    
    # utility function to return 
    def nearest_ind(self, items, pivot):
        diff = np.abs([item - pivot for item in items])
        return diff.argmin(0)

# main program
if __name__ == "__main__":
    
    # get case from user
    parser = argparse.ArgumentParser(description="Post-process LEMS output files")
    parser.add_argument("-i", "--infile", dest='infile',action='store', 
                        type=str, required=True, help="Name of original LEMS file")
    parser.add_argument("-o", "--outfile", dest='outfile',action='store', 
                        type=str, required=False, help="Desired name of LEMS netcdf file")
    parser.add_argument('-s', "--start", dest='start',action='store',
                        type=datetime.datetime.fromisoformat,help="start time: YYYMMDD hh:mm:ss")
    parser.add_argument('-e', "--end", dest='end',action='store',
                        type=datetime.datetime.fromisoformat,help="end time: YYYMMDD hh:mm:ss")
    parser.add_argument('-a', "--avg", dest='avg',action='store',
                        type=float,help="averaging window in minutes")
    
    args  = parser.parse_args()
    ifile = args.infile
    ofile = args.outfile
    start = args.start
    end   = args.end
    avg   = args.avg

    # convert averaging window to number of records at 10 Hz
    window = int(avg * 60 / 10) if avg else 1

    # if no netcdf output name given, use base name from input file
    if not ofile:
        ofile = os.path.splitext(ifile)[0] + '.nc'

    # create LEMS instance from file
    lems = LEMS(ifile,window=window)

    # save to netCDF file
    lems.to_netcdf(ofile,ts=start,tf=end)