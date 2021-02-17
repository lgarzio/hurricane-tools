#!/usr/bin/env python

"""
Author: Lori Garzio on 2/17/2021
Last modified: 2/17/2021
"""

import numpy as np
import os
import pandas as pd
from geopy.distance import geodesic
pd.set_option('display.width', 320, "display.max_columns", 10)  # for display in pycharm console


def return_clean_array(nc, varname):
    ncvar = nc[varname]
    ncvar_values = ncvar.values.astype('float')
    ncvar_values[ncvar_values == ncvar._FillValue] = np.nan
    return ncvar_values


def main(f1, f2):
    sDir = os.path.dirname(f1)
    df1 = pd.read_csv(f1)
    addcols = ['Landfall_lat', 'Landfall_lon', 'Landfall_dist_km', 'Landfall_intensity', 'Landfall_wspd_kts',
               'Landfall_pres', 'max_usa_sshs']
    for ac in addcols:
        df1[ac] = ''
    df2 = pd.read_csv(f2)

    for i, row in df1.iterrows():
        ecosys_loc = [row['Lat'], -row['Lon']]

        df2_filt = df2[(df2['year'] == row['Year']) & (df2['name'].str.lower() == row['Name'].lower())]
        if len(df2_filt) > 0:
            distances = dict(dist=[], landfall_cat=[], landfall_wspd_kts=[], landfall_pres=[], lat=[], lon=[])
            for ii, rowi in df2_filt.iterrows():
                lf_loc = [rowi['landfall_lat'], rowi['landfall_lon']]
                diff_loc = round(geodesic(ecosys_loc, lf_loc).kilometers)
                distances['dist'].append(diff_loc)
                distances['landfall_cat'].append(rowi['landfall_cat'])
                distances['landfall_wspd_kts'].append(rowi['landfall_wspd_kts'])
                distances['landfall_pres'].append(rowi['landfall_pres'])
                distances['lat'].append(rowi['landfall_lat'])
                distances['lon'].append(rowi['landfall_lon'])

            # find the closest landfall distance to ecosystem and add values to dataframe
            mindist_idx = np.argmin(distances['dist'])
            df1.at[i, 'Landfall_intensity'] = distances['landfall_cat'][mindist_idx]
            df1.at[i, 'Landfall_wspd_kts'] = distances['landfall_wspd_kts'][mindist_idx]
            df1.at[i, 'Landfall_pres'] = distances['landfall_pres'][mindist_idx]
            df1.at[i, 'Landfall_lat'] = distances['lat'][mindist_idx]
            df1.at[i, 'Landfall_lon'] = distances['lon'][mindist_idx]
            df1.at[i, 'Landfall_dist_km'] = distances['dist'][mindist_idx]
            df1.at[i, 'max_usa_sshs'] = np.max(df2_filt['max_usa_sshs'])

    df1.to_csv(os.path.join(sDir, 'specific_landfall_storms-final.csv'), index=False)


if __name__ == '__main__':
    file1 = '/Users/lgarzio/Documents/rucool/hurricanes/storms_1970-2019/specific_landfall_storms-raw.csv'
    file2 = '/Users/lgarzio/Documents/rucool/hurricanes/storms_1970-2019/NA_landfall_summary_1970-2019.csv'
    main(file1, file2)
