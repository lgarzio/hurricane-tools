#!/usr/bin/env python

"""
Author: Lori Garzio on 2/17/2021
Last modified: 2/17/2021
Create scatter plots for the latitude at landfall for NA storms for 1) all storms, 2) major storms only (lifetime
category >=3) and 3) minor storms only (lifetime category < 3)
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
pd.set_option('display.width', 320, "display.max_columns", 10)  # for display in pycharm console
plt.rcParams.update({'font.size': 12})


def plot_scatter(yrs, latitudes, sfile_png):
    fig, ax = plt.subplots()
    ax.scatter(yrs, latitudes, s=5, c='k')
    ax.set_ylabel('Latitude')
    ax.set_xlabel('Year')
    plt.savefig(sfile_png, dpi=300)
    plt.close()


def main(f):
    sDir = os.path.dirname(f)
    sf = pd.read_csv(f)

    # plot all landfall latitudes (TS and higher category)
    year = sf['year']
    lats = sf['landfall_lat']
    sfile = os.path.join(sDir, 'landfall_lats_all.png')
    plot_scatter(year, lats, sfile)

    # plot landfall latitudes for major storms only (category >= 3)
    sf_filt = sf[sf['max_usa_sshs'] >= 3]
    year = sf_filt['year']
    lats = sf_filt['landfall_lat']
    sfile = os.path.join(sDir, 'landfall_lats_major.png')
    plot_scatter(year, lats, sfile)

    # plot landfall latitudes for minor storms only (category < 3)
    sf_filt = sf[sf['max_usa_sshs'] < 3]
    year = sf_filt['year']
    lats = sf_filt['landfall_lat']
    sfile = os.path.join(sDir, 'landfall_lats_minor.png')
    plot_scatter(year, lats, sfile)


if __name__ == '__main__':
    fpath = '/Users/lgarzio/Documents/rucool/hurricanes/storms_1970-2019/NA_landfall_summary_1970-2019.csv'
    main(fpath)
