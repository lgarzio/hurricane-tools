#!/usr/bin/env python

"""
Author: Lori Garzio on 2/11/2021
Last modified: 2/11/2021
Creates a summary .csv file from a file created by hurricane_summary.py of all North Atlantic storms in the IBTrACS
dataset from 1970-2019 that includes storm name, dates, maximum usa_sshs (category), and minimum landfall value.
"""

import numpy as np
import os
import pandas as pd
import xarray as xr
import cftime
import matplotlib.pyplot as plt
pd.set_option('display.width', 320, "display.max_columns", 10)  # for display in pycharm console
plt.rcParams.update({'font.size': 12})


def extract_basin(ncfile_sel):
    fbasin = np.unique(ncfile_sel['basin'].values)
    basin_list = []
    for b in fbasin:
        if len(b.decode('utf-8')) > 0:
            basin_list.append(b.decode('utf-8'))
    return basin_list


def main(f, years):
    sDir = os.path.dirname(f)
    ncfile = xr.open_dataset(f, mask_and_scale=False)

    yrs = np.arange(years[0], years[1] + 1, 1)

    sf = pd.read_csv(os.path.join(sDir, 'summary_1970-2019.csv'))
    hindex = list(sf['findex'])

    # distance from land is < 60 nmile (111 km)
    storm_summary = dict(name=[], basin=[], year=[], t0=[], tf=[], max_usa_sshs=[], min_landfall=[], landfall0=[],
                         landfall111=[], findex=[])
    for i, hi in enumerate(hindex):
        ncf = ncfile.sel(storm=hi)
        t0 = min(t for t in ncf['time'].values if t > cftime.DatetimeGregorian(1800, 1, 1, 0, 0, 0, 0))
        if t0.year in yrs:
            storm_summary['name'].append(ncf['name'].values.tostring().decode('utf-8'))
            storm_summary['basin'].append(extract_basin(ncf))
            tf = max(ncf['time'].values)
            storm_summary['t0'].append(t0)
            storm_summary['tf'].append(tf)
            storm_summary['year'].append(t0.year)
            storm_summary['findex'].append(hi)
            storm_summary['max_usa_sshs'].append(np.nanmax(ncf.usa_sshs.values))
            lf = ncf.landfall.values.astype('float')
            lf[lf == -9999] = np.nan  # convert fill values to nan
            minlf = np.nanmin(lf)
            storm_summary['min_landfall'].append(minlf)
            if minlf == 0.0:
                landfall0 = 'yes'
            else:
                landfall0 = 'no'
            storm_summary['landfall0'].append(landfall0)
            if minlf > 111:
                landfall111 = 'no'
            else:
                landfall111 = 'yes'
            storm_summary['landfall111'].append(landfall111)

    df = pd.DataFrame(storm_summary)
    df.to_csv(os.path.join(sDir, 'summary_1970-2019_withcategory.csv'), index=False)


if __name__ == '__main__':
    fpath = '/Users/lgarzio/Documents/rucool/hurricanes/storms_1970-2019/IBTrACS.NA.v04r00.nc'
    yrs = [1970, 2019]  # start and end year
    main(fpath, yrs)
