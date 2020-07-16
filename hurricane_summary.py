#!/usr/bin/env python

"""
Author: Lori Garzio on 7/9/2020
Last modified: 7/9/2020
Creates a summary of all hurricanes in the years and ocean basin defined by the user
"""

import numpy as np
import os
import cftime
import pandas as pd
import xarray as xr
pd.set_option('display.width', 320, "display.max_columns", 10)  # for display in pycharm console


def main(f, years, bsin):
    sDir = os.path.dirname(f)
    ncfile = xr.open_dataset(f, mask_and_scale=False)

    years_lst = np.arange(years[0], years[1] + 1, 1)
    storm_summary = dict(name=[], basin=[], year=[], t0=[], tf=[], findex=[])
    for i, s in enumerate(ncfile['storm']):
        stm = ncfile.sel(storm=i)
        fbasin = np.unique(stm['basin'].values)
        basin_lst = []
        for b in fbasin:
            if len(b.decode('utf-8')) > 0:
                basin_lst.append(b.decode('utf-8'))
        if bsin in basin_lst:
            t0 = min(t for t in stm['time'].values if t > cftime.DatetimeGregorian(1800, 1, 1, 0, 0, 0, 0))
            if t0.year in years_lst:
                print(i)
                storm_summary['name'].append(stm['name'].values.tostring().decode('utf-8'))
                storm_summary['basin'].append(basin)
                tf = max(stm['time'].values)
                storm_summary['t0'].append(t0)
                storm_summary['tf'].append(tf)
                storm_summary['year'].append(t0.year)
                storm_summary['findex'].append(i)
    df = pd.DataFrame(storm_summary)
    df.to_csv(os.path.join(sDir, 'summary_northatlantic2010_2019.csv'))


if __name__ == '__main__':
    #fpath = '/Users/lgarzio/Documents/rucool/hurricanes/congress_brief2020/IBTrACS.NA.v04r00.nc'  # on local machine
    fpath = '/home/lgarzio/rucool/hurricanes/congress_brief2020/IBTrACS.NA.v04r00.nc'  # on server
    yrs = [2010, 2019]  # start and end year
    basin = 'NA'
    main(fpath, yrs, basin)
