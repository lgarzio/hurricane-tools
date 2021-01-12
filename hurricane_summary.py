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


def append_data(data_dict, ncfile_sel, yrs_lst, findex):
    t0 = min(t for t in ncfile_sel['time'].values if t > cftime.DatetimeGregorian(1800, 1, 1, 0, 0, 0, 0))
    if t0.year in yrs_lst:
        data_dict['name'].append(ncfile_sel['name'].values.tostring().decode('utf-8'))
        data_dict['basin'].append(extract_basin(ncfile_sel))
        tf = max(ncfile_sel['time'].values)
        data_dict['t0'].append(t0)
        data_dict['tf'].append(tf)
        data_dict['year'].append(t0.year)
        data_dict['findex'].append(findex)


def extract_basin(ncfile_sel):
    fbasin = np.unique(ncfile_sel['basin'].values)
    basin_list = []
    for b in fbasin:
        if len(b.decode('utf-8')) > 0:
            basin_list.append(b.decode('utf-8'))
    return basin_list


def main(f, years, bsin):
    sDir = os.path.dirname(f)
    ncfile = xr.open_dataset(f, mask_and_scale=False)

    yrs = np.arange(years[0], years[1] + 1, 1)
    storm_summary = dict(name=[], basin=[], year=[], t0=[], tf=[], findex=[])
    for i, s in enumerate(ncfile['storm']):
        stm = ncfile.sel(storm=i)
        if bsin == 'all':
            append_data(storm_summary, stm, yrs, i)
        else:
            basin_lst = extract_basin(stm)
            if bsin in basin_lst:
                append_data(storm_summary, stm, yrs, i)
    df = pd.DataFrame(storm_summary)
    df.to_csv(os.path.join(sDir, 'summary_2019_2020.csv'))


if __name__ == '__main__':
    # fpath = '/Users/lgarzio/Documents/rucool/hurricanes/congress_brief2020/IBTrACS.NA.v04r00.nc'
    fpath = '/Users/lgarzio/Documents/rucool/hurricanes/hurricane_tracks_global_jan2021/IBTrACS.last3years.v04r00.nc'
    yrs = [2019, 2020]  # start and end year
    basin = 'all'  # 'NA'
    main(fpath, yrs, basin)
