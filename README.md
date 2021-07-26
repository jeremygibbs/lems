# LEMS Post
This code reads a LEMS output file, writes to netCDF4, and plots the data.

## Reading LEMS file
The most basic command will load the `LEMS.csv` file and output all times for all fields to a netCDF4 file named `LEMS.nc`. 

```
 python lems_post.py -i LEMS.csv
```

## Specifying alternative netCDF4 output file
This command will will load the `LEMS.csv` file and output all times for all fields to a netCDF4 file named `ALT.nc`.

```
 python lems_post.py -i LEMS.csv -o ALT.nc
```

## Specifying a start time and/or an end time
You might not want to save the entire time record. You can specify a desired start and/or end time in 'YYYY-MM-DD hh:mm:ss' format.
```
 python lems_post.py -i LEMS.csv -s '2021-07-07 10:00:00'
 python lems_post.py -i LEMS.csv -e '2021-07-08 10:00:00'
 python lems_post.py -i LEMS.csv -s '2021-07-07 10:00:00' -e '2021-07-08 10:00:00'
```

## Specifying an averaging window
This command will will load the `LEMS.csv` file and output a rolling average over a 10-minute window for all fields to a netCDF4 file named `LEMS_avg.nc`.

```
 python lems_post.py -i LEMS.csv -o LEMS_avg.nc -a 10
```