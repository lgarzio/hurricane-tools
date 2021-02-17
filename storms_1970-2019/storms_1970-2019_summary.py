#!/usr/bin/env python

"""
Author: Lori Garzio on 2/11/2021
Last modified: 2/17/2021
Creates a summary .csv file from a file created by hurricane_summary.py of each landfall west of longitude=-60 for
North Atlantic storms in the IBTrACS dataset from 1970-2019 that includes storm name, dates, maximum usa_sshs (category),
landfall latitude and longitude, eye distance from shore, and storm category, windspeed and pressure at landfall.
Landfall is defined as the eye of the storm < 60 nmile (111 km) from shore.
"""

import numpy as np
import os
import pandas as pd
import xarray as xr
import cftime
pd.set_option('display.width', 320, "display.max_columns", 10)  # for display in pycharm console


def return_clean_array(nc, varname):
    ncvar = nc[varname]
    ncvar_values = ncvar.values.astype('float')
    ncvar_values[ncvar_values == ncvar._FillValue] = np.nan
    return ncvar_values


def main(f, years):
    sDir = os.path.dirname(f)
    ncfile = xr.open_dataset(f, mask_and_scale=False)

    yrs = np.arange(years[0], years[1] + 1, 1)

    sf = pd.read_csv(os.path.join(sDir, 'summary_1970-2019.csv'))
    hindex = list(sf['findex'])

    # distance from land is < 60 nmile (111 km)
    storm_summary = dict(name=[], year=[], t0=[], tf=[], max_usa_sshs=[], landfall_lat=[], landfall_lon=[],
                         dist_from_shore_km=[], landfall_cat=[], landfall_wspd_kts=[], landfall_pres=[], findex=[])
    for i, hi in enumerate(hindex):
        ncf = ncfile.sel(storm=hi)
        t0 = min(t for t in ncf['time'].values if t > cftime.DatetimeGregorian(1800, 1, 1, 0, 0, 0, 0))
        if t0.year in yrs:
            lf = ncf.landfall.values.astype('float')
            lf[lf == -9999] = np.nan  # convert fill values to nan

            # find all landfall indices
            lf_ind = np.where(lf < 111)[0]

            # find the storm category
            cats = return_clean_array(ncf, 'usa_sshs')
            max_cat = np.nanmax(cats)

            # if the storm makes landfall and is a TS or higher
            if np.logical_and(len(lf_ind) > 0, max_cat >= 0):

                # break up index into each consecutive section
                new_ind = []
                ni = []
                for tri, index in enumerate(lf_ind):
                    if 0 < tri < len(lf_ind) - 1:
                        if index - lf_ind[tri - 1] > 1:
                            new_ind.append(ni)
                            ni = []
                            ni.append(index)
                        else:
                            ni.append(index)
                    elif tri == len(lf_ind) - 1:
                        if index - lf_ind[tri - 1] > 1:
                            new_ind.append(ni)
                            new_ind.append([index])
                        else:
                            ni.append(index)
                            new_ind.append(ni)
                    else:
                        ni.append(index)

                # find the index of the beginning of each individual landfall (not just where landfall=0)
                landfall_idx = []
                for ii, jj in enumerate(new_ind):
                    landfall_idx.append(jj[0])

                lats = return_clean_array(ncf, 'lat')
                lons = return_clean_array(ncf, 'lon')
                wspd = return_clean_array(ncf, 'usa_wind')
                pres = return_clean_array(ncf, 'usa_pres')

                # find the storm category, max windspeed, and pressure at landfall
                for idx in landfall_idx:
                    lf_lon = lons[idx]
                    if lf_lon < -60:
                        storm_summary['name'].append(ncf['name'].values.tostring().decode('utf-8'))
                        tf = max(ncf['time'].values)
                        storm_summary['t0'].append(t0)
                        storm_summary['tf'].append(tf)
                        storm_summary['year'].append(t0.year)
                        storm_summary['findex'].append(hi)
                        storm_summary['dist_from_shore_km'].append(lf[idx])
                        storm_summary['max_usa_sshs'].append(max_cat)
                        storm_summary['landfall_lat'].append(lats[idx])
                        storm_summary['landfall_lon'].append(lf_lon)
                        storm_summary['landfall_cat'].append(cats[idx])
                        storm_summary['landfall_wspd_kts'].append(wspd[idx])
                        storm_summary['landfall_pres'].append(pres[idx])

    df = pd.DataFrame(storm_summary)
    df.to_csv(os.path.join(sDir, 'NA_landfall_summary_1970-2019.csv'), index=False)


if __name__ == '__main__':
    fpath = '/Users/lgarzio/Documents/rucool/hurricanes/storms_1970-2019/IBTrACS.NA.v04r00.nc'
    yrs = [1970, 2019]  # start and end year
    main(fpath, yrs)
