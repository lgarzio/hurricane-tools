#!/usr/bin/env python

"""
Author: Lori Garzio on 2/11/2021
Last modified: 2/11/2021
Creates two summary .csv files containing 1) a count of the number of landfalling storms (tropical storm to cat 5), and
2) a count of the number of landfalling major hurricanes (cat 3+) by year from 1970-2019 in the North Atlantic basin.
Landfall is defined as the eye of the storm < 60 nmile from land.
Creates two maps: all storms from 1970-2019 as gray tracks with 1) landfalling storms (tropical storm to cat 5)
highlighted red, and 2) landfalling major hurricane (cat 3+) highlighted red.
"""

import numpy as np
import os
import pandas as pd
import xarray as xr
import cftime
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
pd.set_option('display.width', 320, "display.max_columns", 10)  # for display in pycharm console
plt.rcParams.update({'font.size': 12})


def add_map_features(ax, axes_limits):
    """
    Adds bathymetry and coastlines to a cartopy map object
    :param ax: plotting axis object
    :param axes_limits: optional list of axis limits [min lon, max lon, min lat, max lat]
    """
    ax.set_extent(axes_limits)
    coast = cfeature.NaturalEarthFeature('physical', 'coastline', '10m')
    ax.add_feature(coast, edgecolor='black', facecolor='none')

    ax.add_feature(cfeature.BORDERS)


def export_df(dictionary, savefile):
    df = pd.DataFrame.from_dict(dictionary, orient='index')
    df = df.reset_index()
    df.columns = ['year', 'storm_count']
    df.to_csv(savefile, index=False)


def main(f, years):
    sDir = os.path.dirname(f)
    ncfile = xr.open_dataset(f, mask_and_scale=False)

    yrs = np.arange(years[0], years[1] + 1, 1)

    sf = pd.read_csv(os.path.join(sDir, 'summary_1970-2019.csv'))
    hindex = list(sf['findex'])

    storms_all = dict()
    storms_major = dict()

    for yr in yrs:
        storms_all[yr] = 0
        storms_major[yr] = 0

    # fig_all, ax_all = plt.subplots(subplot_kw=dict(projection=ccrs.PlateCarree()))
    # fig_major, ax_major = plt.subplots(subplot_kw=dict(projection=ccrs.PlateCarree()))

    fig_all, ax_all = plt.subplots(subplot_kw=dict(projection=ccrs.Robinson()))
    fig_major, ax_major = plt.subplots(subplot_kw=dict(projection=ccrs.Robinson()))
    ax_lims = [-120, 0, 0, 55]

    for i, hi in enumerate(hindex):
        # set up map axes
        if i == 0:
            add_map_features(ax_all, ax_lims)
            add_map_features(ax_major, ax_lims)

        ncf = ncfile.sel(storm=hi)
        lat = ncf.lat.values
        lat[lat == -9999] = np.nan
        lon = ncf.lon.values
        lon[lon == -9999] = np.nan

        category = np.nanmax(ncf.usa_sshs.values)

        # distance from land is < 60 nmile (111 km)
        lf = ncf.landfall.values.astype('float')
        lf[lf == -9999] = np.nan  # convert fill values to nan
        minlf = np.nanmin(lf)
        lf_ind = np.where(lf < 111)[0]
        lf_lon = lon[lf_ind]

        # choose when landfall is < 60 nmile and the storm is west of 40 degrees W
        #if np.logical_and(minlf < 111, any(lf_lon < -60)):
        if np.logical_and(minlf < 111, any(lf_lon < -40)):
            nsamerica_lf = 'yes'
        else:
            nsamerica_lf = 'no'

        lw = 1
        bc = 'darkgray'
        alpha = .6
        mk = 'None'

        # count the storms that make landfall west of 40 degrees W each year
        if np.logical_and(category >= 0, nsamerica_lf == 'yes'):
            t0 = min(t for t in ncf.time.values if t > cftime.DatetimeGregorian(1800, 1, 1, 0, 0, 0, 0))
            storms_all[t0.year] = storms_all[t0.year] + 1
            ax_all.plot(lon, lat, c='r', marker=mk, linewidth=lw, transform=ccrs.PlateCarree())

            if category >= 3:
                storms_major[t0.year] = storms_major[t0.year] + 1
                ax_major.plot(lon, lat, c='r', marker=mk, linewidth=lw, transform=ccrs.PlateCarree())
            else:
                ax_major.plot(lon, lat, c=bc, marker=mk, linewidth=lw, alpha=alpha, transform=ccrs.PlateCarree())
        else:
            ax_all.plot(lon, lat, c=bc, marker=mk, linewidth=lw, alpha=alpha, transform=ccrs.PlateCarree())
            ax_major.plot(lon, lat, c=bc, marker=mk, linewidth=lw, alpha=alpha, transform=ccrs.PlateCarree())

    # export_df(storms_all, os.path.join(sDir, 'NA_landfalling_storms_all_1970-2019-test.csv'))
    # export_df(storms_major, os.path.join(sDir, 'NA_landfalling_storms_major_1970-2019-test.csv'))

    fig_all.savefig(os.path.join(sDir, 'NA_storms_all_1970-2019-test40deg.png'), dpi=300)
    plt.close(fig_all)

    fig_major.savefig(os.path.join(sDir, 'NA_storms_major_1970-2019-test40deg.png'), dpi=300)
    plt.close(fig_major)


if __name__ == '__main__':
    fpath = '/Users/lgarzio/Documents/rucool/hurricanes/storms_1970-2019/IBTrACS.NA.v04r00.nc'
    yrs = [1970, 2019]  # start and end year
    main(fpath, yrs)
