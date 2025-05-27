import logging

import altair as alt
import numpy as np

from isimip_utils.xarray import convert_to_dataframe, get_var_name, get_var_units

logger = logging.getLogger(__name__)


def enable_vegafusion():
    alt.data_transformers.enable('vegafusion')


def plot_line(ds, title=None):
    var_name = get_var_name(ds)
    var_units = get_var_units(ds)
    var_title = f'{var_name} [{var_units}]'

    df = convert_to_dataframe(ds)

    return alt.Chart(df).mark_line().encode(
        alt.X(
            'time:T',
            title='time'
        ),
        alt.Y(
            f'{var_name}:Q',
            title=var_title,
        )
    ).properties(
        title=title,
    )

def plot_map(ds, scale_factor=1, bin_size=1, color_bin=None, color_scale=None):
    lon_size = len(ds['lon'])
    lat_size = len(ds['lat'])

    lon_bin = float(abs(ds['lon'][1] - ds['lon'][0])) * bin_size
    lat_bin = float(abs(ds['lat'][1] - ds['lat'][0])) * bin_size

    lon_domain = float(min(ds['lon']) - 0.5 * lon_bin), float(max(ds['lon']) + 0.5 * lon_bin)
    lat_domain = float(min(ds['lat']) - 0.5 * lat_bin), float(max(ds['lat']) + 0.5 * lat_bin)

    lon_ticks = np.linspace(*lon_domain, num=7)
    lat_ticks = np.linspace(*lat_domain, num=5)

    width = scale_factor * lon_size
    height = scale_factor * lat_size

    var_name = get_var_name(ds)
    var_units = get_var_units(ds)
    title = f'{var_name} [{var_units}]'

    logger.info(f'plot map title="{title}" size=({width}, {height})')

    df = convert_to_dataframe(ds)

    return alt.Chart(df).mark_rect().encode(
        alt.X(
            'lon:Q',
            title='lon',
            bin=alt.Bin(step=lon_bin),
            axis=alt.Axis(values=lon_ticks),
            scale=alt.Scale(domain=lon_domain, padding=0, round=True)
        ),
        alt.Y(
            'lat:Q',
            title='lat',
            bin=alt.Bin(step=lat_bin),
            axis=alt.Axis(values=lat_ticks),
            scale=alt.Scale(domain=lat_domain, padding=0, round=True)
        ),
        alt.Color(
            f'{var_name}:Q',
            title=title,
            bin=color_bin,
            scale=color_scale or alt.Scale()
        )
    ).properties(
        width=width,
        height=height
    )
