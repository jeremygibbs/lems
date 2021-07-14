#!/usr/bin/env python
import argparse
import pandas as pd
import pylab as pl

class LEMS(object):

    def __init__(self,datafile):

        print("[LEMS] \t Reading LEMS file: %s"%datafile)

        # read the csv output file and combine date/time columns
        self.data = pd.read_csv(datafile,
                                parse_dates={"date":["Year","Month","Date","Hour","Minute","Second"]},
                                date_parser=self.parse)

        # date
        self.date = self.data['date'].to_numpy()
        
        # battery level
        self.battery_level = self.data['Bat_Lvl'].to_numpy()
        
        # temperature
        self.T_sfc_ir = self.data['MLX_IR_C'].to_numpy()
        self.T_sfc_am = self.data['MLX_Amb_C'].to_numpy()
        self.T_air_am = self.data['SHT_Amb_C'].to_numpy()
        self.T_soil_u = self.data['Upper_Soil_Temp'].to_numpy()
        self.T_soil_l = self.data['Lower_Soil_Temp'].to_numpy()
        self.T_bmp_am = self.data['BMP_Amb'].to_numpy()
        self.T_anemom = self.data['Sonic_Tmp'].to_numpy()

        # moisture
        self.relh_air = self.data['SHT_Hum_Pct'].to_numpy()
        self.q_soil_u = self.data['Upper_Soil_Mois'].to_numpy()
        self.q_soil_l = self.data['Lower_Soil_Mois'].to_numpy()
        
        # wind
        self.wind_spd = self.data['Sonic_Spd'].to_numpy()
        self.wind_dir = self.data['Sonic_Dir'].to_numpy()
        self.wind_gst = self.data['Sonic_Gst'].to_numpy()

        # pressure
        self.pressure = self.data['Lower_Soil_Mois'].to_numpy()
        
        # insolation
        self.radsolar = self.data['Sunlight'].to_numpy()

    # utlity function to format date/time
    def parse(self, year, month, day, hour, minute, second):
        return year+ '-' +month+ '-' +day+ ' ' +hour+ ':' +minute+ ':' +second

if __name__ == "__main__":
    
    # get case from user
    parser = argparse.ArgumentParser(description="Post-process LEMS output files")
    parser.add_argument("-f", "--file", dest='file',action='store', 
                        type=str, required=True, help="Name of file")
    args  = parser.parse_args()
    dataf = args.file

    # create LEMS instance from file
    lems = LEMS(dataf)