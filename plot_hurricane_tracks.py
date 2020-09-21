#!/usr/bin/env python

"""
Author: Lori Garzio on 7/10/2020
Last modified: 8/11/2020
Creates plot of hurricane tracks, with the 3 days previous to US land impact (continental US + Puerto Rico) colored in
red. Land impact = landfall values <60 nmile (111 km)
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
plt.rcParams.update({'font.size': 13})


def add_map_features(ax, axes_limits):
    """
    Adds bathymetry and coastlines to a cartopy map object
    :param ax: plotting axis object
    :param axes_limits: optional list of axis limits [min lon, max lon, min lat, max lat]
    """
    ax.set_extent(axes_limits)

    # add bathymetry
    bath_file = '/Users/lgarzio/Documents/rucool/hurricanes/congress_brief2020/gebco_2020_n50.0_s0.0_w-100.0_e0.0.nc'
    ncbath = xr.open_dataset(bath_file)
    bath_lat = ncbath.variables['lat'][:]
    bath_lon = ncbath.variables['lon'][:]
    bath_elev = ncbath.variables['elevation'][:]

    #lon_lim = [-100.0, 0]
    lon_lim = [-100.0, -10.0]
    lat_lim = [0.0, 60.0]

    oklatbath = np.logical_and(bath_lat >= lat_lim[0], bath_lat <= lat_lim[-1])
    oklonbath = np.logical_and(bath_lon >= lon_lim[0], bath_lon <= lon_lim[-1])

    bath_latsub = bath_lat[oklatbath]
    bath_lonsub = bath_lon[oklonbath]
    bath_elevs = bath_elev[oklatbath, :]
    bath_elevsub = bath_elevs[:, oklonbath]

    lev = np.arange(-9000, 9100, 100)
    ax.contourf(bath_lonsub, bath_latsub, bath_elevsub, lev, cmap=cmocean.cm.topo)

    coast = cfeature.NaturalEarthFeature('physical', 'coastline', '10m')
    ax.add_feature(coast, edgecolor='black', facecolor='none')

    ax.add_feature(cfeature.BORDERS)


def color_landimpact_track(ax, hurr_track, landfall_ind, hurricane_index):
    # find indices that aren't consecutive and break into multiple arrays
    new_ind = []
    ni = []
    for tri, index in enumerate(landfall_ind):
        if 0 < tri < len(landfall_ind) - 1:
            if index - landfall_ind[tri - 1] > 1:
                new_ind.append(ni)
                ni = []
                ni.append(index)
            else:
                ni.append(index)
        elif tri == len(landfall_ind) - 1:
            if index - landfall_ind[tri - 1] > 1:
                new_ind.append(ni)
                new_ind.append([index])
            else:
                ni.append(index)
                new_ind.append(ni)
        else:
            ni.append(index)

    # manually fix some hurricane tracks that cross Mexico or the Caribbean before impacting the US
    if hurricane_index in [1944, 1947, 1951, 1952, 1971, 1972, 1975, 1980, 1986, 1989, 2003, 2010, 2022, 2028, 2047,
                           2050, 2051, 2052, 2071, 2081, 2121, 2130, 2136, 2157, 2171, 2182, 2193, 2200, 2204, 2217]:
        new_ind = [new_ind[-1]]
    elif hurricane_index in [1909, 2017, 2148]:
        new_ind = [new_ind[1]]
    elif hurricane_index in [1918, 1925, 1935, 1942, 1977, 2042, 2159]:
        new_ind = [new_ind[0]]
    elif hurricane_index in [1978]:
        new_ind = [new_ind[2], new_ind[3], new_ind[4]]
    elif hurricane_index in [2000]:
        new_ind = [new_ind[2], new_ind[3]]
    elif hurricane_index in [2101, 2195]:
        new_ind = [new_ind[0], new_ind[-1]]
    elif hurricane_index in [1988, 2177]:
        new_ind = [new_ind[1], new_ind[2]]
    elif hurricane_index in [2161]:
        new_ind = [[26, 27, 28]]

    for j, k in enumerate(new_ind):
        lf_times = hurr_track['tm'][k]
        if len(lf_times) > 0:
            time_range_ind = []
            for lft in lf_times:
                t0 = lft - dt.timedelta(days=3)
                t1 = lft
                tm_test = np.logical_and(t0 <= hurr_track['tm'], hurr_track['tm'] <= t1)
                res = [i for i, val in enumerate(tm_test) if val]
                time_range_ind.append(res)
            time_range_ind = np.unique(list(itertools.chain(*time_range_ind)))

            subset_track = subset_dataset(hurr_track, time_range_ind)

            # plot points 3 days before landfall in red
            ax.plot(subset_track['lon'], subset_track['lat'], c='r', marker='.', markersize=1,
                    transform=ccrs.PlateCarree())


def subset_dataset(data_dict, ind):
    d = dict()
    for key, value in data_dict.items():
        d[key] = value[ind]

    return d


def main(f, years, ic):
    sDir = os.path.dirname(f)
    ncfile = xr.open_dataset(f, mask_and_scale=False)

    summary_file = pd.read_csv(os.path.join(sDir, 'summary_northatlantic2000_2019_mod.csv'))
    if len(years) == 1:
        sf = summary_file[summary_file['year'] == years[0]]
        ttl = str(years[0])
    else:
        sf = summary_file[(summary_file['year'] >= years[0]) & (summary_file['year'] <= years[1])]
        ttl = '{} - {}'.format(str(years[0]), str(years[1]))

    if ic == 'US':
        country_flag = list(sf['usimpact'])
    hnames = list(sf['name'])
    hindex = list(sf['findex'])

    fig, ax = plt.subplots(subplot_kw=dict(projection=ccrs.PlateCarree()))

    for i, hi in enumerate(hindex):
        if i == 0:
            #ax_lims = [-105, -5, 5, 50]
            #ax_lims = [-105, -5, 2.5, 60]
            # no idea why, but set ymax = 37.7 to get ymax = 50
            # ax_lims = [-100, 0, 10, 37.7]
            ax_lims = [-100, -10, 10, 40.32]
            add_map_features(ax, ax_lims)
            #plt.title(ttl)

        ncf = ncfile.sel(storm=hi)
        data = dict(tm=ncf['time'].values,
                    lat=ncf['lat'].values,
                    lon=ncf['lon'].values,
                    lf=ncf['landfall'].values)

        lat_ind = np.where(data['lat'] != -9999.)
        full_track = subset_dataset(data, lat_ind)

        # plot full hurricane track
        ax.plot(full_track['lon'], full_track['lat'], c='darkgray', marker='.', markersize=1, alpha=.4,
                transform=ccrs.PlateCarree())

        # the last land fall value is always -9999, convert that to the previous landfall value
        full_track['lf'][-1] = full_track['lf'][-2]

        # find indices where the distance from land is < 60 nmile (111 km)
        lf_ind = np.where(full_track['lf'] < 111)

        try:
            if country_flag[i] == 'yes':
                #uscoast = dict(minlon=-100, maxlon=-65, minlat=24, maxlat=50)

                # make sure the land impact isn't in Africa
                land_impact_lon = full_track['lon'][lf_ind]

                #lon_ind = np.logical_and(land_impact_lon > uscoast['minlon'], land_impact_lon < uscoast['maxlon'])
                land_impact_lon_ind = np.where(land_impact_lon < -40)

                if len(lf_ind[0]) == len(land_impact_lon_ind[0]):
                    color_landimpact_track(ax, full_track, lf_ind[0], hi)
                else:
                    color_landimpact_track(ax, full_track, lf_ind[0][list(land_impact_lon_ind[0])], hi)

                # plt.savefig(os.path.join(sDir, 'hurricanes{}{}.png'.format(hi, hnames[i])), dpi=300)

        except NameError:
            color_landimpact_track(ax, full_track, lf_ind)

        #plt.savefig(os.path.join(sDir, 'hurricanes{}{}.png'.format(hi, hnames[i])), dpi=200)

    plt.savefig(os.path.join(sDir, 'hurricanes2000-2019.png'), dpi=300)
    plt.close()


if __name__ == '__main__':
    fpath = '/Users/lgarzio/Documents/rucool/hurricanes/congress_brief2020/2000_2019/IBTrACS.NA.v04r00.nc'
    yrs = [2000, 2019]  # [2019]  [2010, 2019]
    impact_country = 'US'  # 'US' 'na'
    main(fpath, yrs, impact_country)
