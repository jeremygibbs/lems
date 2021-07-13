#!/usr/bin/env python
import pandas as pd

class LEMS(object):

    def __init__(self,datafile):

        self.data = pd.read_csv(datafile)

        print(self.data)

        ##############
        # data headers
        ##############
        # Year
        # Month
        # Date
        # Hour
        # Minute
        # Second
        # Bat_Lvl
        # MLX_IR_C
        # MLX_Amb_C
        # Upper_Soil_Temp
        # Upper_Soil_Mois
        # Lower_Soil_Temp
        # Lower_Soil_Mois
        # Pressure
        # BMP_Amb
        # Sonic_Dir
        # Sonic_Spd
        # Sonic_Gst
        # Sonic_Tmp
        # Sunlight
        # SHT_Amb_C
        # SHT_Hum_Pct