#!/usr/bin/env python

"""
Author: Lori Garzio on 1/12/2020
Last modified: 1/12/2020
Creates plot of global storm tracks
"""

import numpy as np
import os
import cmocean
import datetime as dt
import itertools
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
pd.set_option('display.width', 320, "display.max_columns", 10)  # for display in pycharm console
plt.rcParams.update({'font.size': 12})


def add_map_features(ax, axes_limits=None):
    """
    Adds bathymetry and coastlines to a cartopy map object
    :param ax: plotting axis object
    :param axes_limits: optional list of axis limits [min lon, max lon, min lat, max lat]
    """
    if axes_limits is not None:
        ax.set_extent(axes_limits)

    # add bathymetry
    bath_file = '/home/aristizabal/bathymetry_files/GEBCO_2019.nc'
    ncbath = xr.open_dataset(bath_file)
    bath_lat = ncbath.variables['lat'][:]
    bath_lon = ncbath.variables['lon'][:]
    bath_elev = ncbath.variables['elevation'][:]

    # lon_lim = [-100.0, -10.0]
    # lat_lim = [0.0, 60.0]
    #
    # oklatbath = np.logical_and(bath_lat >= lat_lim[0], bath_lat <= lat_lim[-1])
    # oklonbath = np.logical_and(bath_lon >= lon_lim[0], bath_lon <= lon_lim[-1])
    #
    # bath_latsub = bath_lat[oklatbath]
    # bath_lonsub = bath_lon[oklonbath]
    # bath_elevs = bath_elev[oklatbath, :]
    # bath_elevsub = bath_elevs[:, oklonbath]

    lev = np.arange(-9000, 9100, 100)
    # ax.contourf(bath_lonsub, bath_latsub, bath_elevsub, lev, cmap=cmocean.cm.topo)
    ax.contourf(bath_lon, bath_lat, bath_elev, lev, cmap=cmocean.cm.topo)

    coast = cfeature.NaturalEarthFeature('physical', 'coastline', '110m')
    ax.add_feature(coast, edgecolor='black', facecolor='none')

    ax.add_feature(cfeature.BORDERS)


def subset_dataset(data_dict, ind):
    d = dict()
    for key, value in data_dict.items():
        d[key] = value[ind]

    return d


def main(f, years):
    sDir = os.path.dirname(f)
    ncfile = xr.open_dataset(f, mask_and_scale=False)

    summary_file = pd.read_csv(os.path.join(sDir, 'summary_globalstorms2019_2020.csv'))
    if len(years) == 1:
        sf = summary_file[summary_file['year'] == years[0]]
        ttl = str(years[0])
    else:
        sf = summary_file[(summary_file['year'] >= years[0]) & (summary_file['year'] <= years[1])]
        ttl = '{} - {}'.format(str(years[0]), str(years[1]))

    hnames = list(sf['name'])
    hindex = list(sf['findex'])

    #fig, ax = plt.subplots(subplot_kw=dict(projection=ccrs.PlateCarree()))
    fig, ax = plt.subplots(subplot_kw=dict(projection=ccrs.Robinson()))
    plt.title(ttl)
    ax.set_global()

    for i, hi in enumerate(hindex):
        if i == 0:
            # ax_lims = [-180, 180, 90, -90]
            # add_map_features(ax, ax_lims)
            add_map_features(ax)

        ncf = ncfile.sel(storm=hi)
        data = dict(tm=ncf['time'].values,
                    lat=ncf['lat'].values,
                    lon=ncf['lon'].values)

        lat_ind = np.where(data['lat'] != -9999.)
        full_track = subset_dataset(data, lat_ind)

        # plot full hurricane track
        ax.plot(full_track['lon'], full_track['lat'], c='darkgray', marker='.', markersize=1,
                transform=ccrs.PlateCarree())
        # ax.plot(full_track['lon'], full_track['lat'], c='cyan', marker='.', markersize=1, transform=ccrs.PlateCarree())

    plt.savefig(os.path.join(sDir, 'global_storms2019.png'), dpi=300)
    plt.close()


if __name__ == '__main__':
    # fpath = '/Users/lgarzio/Documents/rucool/hurricanes/hurricane_tracks_global_jan2021/IBTrACS.last3years.v04r00.nc'
    fpath = '/home/lgarzio/repo/lgarzio/hurricane-tools/files/IBTrACS.last3years.v04r00.nc'
    yrs = [2019]  # [2019]  [2010, 2019]
    main(fpath, yrs)
