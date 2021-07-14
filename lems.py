#!/usr/bin/env python
import pandas as pd
from datetime import datetime
import pylab as pl
class LEMS(object):

    def __init__(self,datafile):

        # read the data and combine date/time columns
        self.data = pd.read_csv(datafile,
                                parse_dates={"date":["Year","Month","Date","Hour","Minute","Second"]},
                                date_parser=self.parse)

        self.date_time = self.data['date'].to_numpy()
        self.battery_level = self.data['Bat_Lvl'].to_numpy()
        self.sfc_temp_ir  = self.data['MLX_IR_C'].to_numpy()
        self.sfc_temp_amb = self.data['MLX_Amb_C'].to_numpy()
        self.soil_temp_u = self.data['Upper_Soil_Temp'].to_numpy()+273.15
        self.soil_mois_u = self.data['Upper_Soil_Mois'].to_numpy()
        self.soil_temp_l = self.data['Lower_Soil_Temp'].to_numpy()+273.15
        self.soil_mois_l = self.data['Lower_Soil_Mois'].to_numpy()
        self.pressure = self.data['Lower_Soil_Mois'].to_numpy()
        self.bmp_ambient = self.data['BMP_Amb'].to_numpy()
        self.sonic_dir = self.data['Sonic_Dir'].to_numpy()
        self.sonic_spd = self.data['Sonic_Spd'].to_numpy()
        self.sonic_gust = self.data['Sonic_Gst'].to_numpy()
        self.sonic_temp = self.data['Sonic_Tmp'].to_numpy()+273.15
        self.sunlight = self.data['Sunlight'].to_numpy()
        self.air_temp = self.data['SHT_Amb_C'].to_numpy()+273.15
        self.rel_hum  = self.data['SHT_Hum_Pct'].to_numpy()

        pl.plot(self.date_time,self.sfc_temp_amb)
        pl.show()

    # utlity function to format date/time
    def parse(self, year, month, day, hour, minute, second):
        return year+ '-' +month+ '-' +day+ ' ' +hour+ ':' +minute+ ':' +second