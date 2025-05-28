import logging

import altair as alt
import numpy as np

from isimip_utils.pandas import get_var

logger = logging.getLogger(__name__)


def enable_vegafusion():
    alt.data_transformers.enable('vegafusion')


def save_plot(chart, path, *args, **kwargs):
    logger.info(f'save {path.absolute()}')
    path.parent.mkdir(exist_ok=True, parents=True)
    chart.save(path, *args, **kwargs)


def get_title(df):
    var = get_var(df)
    var_name = df.attrs['data_vars'][var].get('long_name', var)
    var_units = df.attrs['data_vars'][var]['units']

    return f'{var_name} [{var_units}]'


def plot_time(df, interpolate=False, x=None, y=None, color=None):
    mark_kwargs = {'interpolate': interpolate} if interpolate else {}

    return alt.Chart(df).mark_line(**mark_kwargs).encode(
        x=x or alt.X(
            'time:T',
            title='Time'
        ),
        y=y or alt.Y(
            f'{get_var(df)}:Q',
            title=get_title(df)
        ),
        color=color or alt.Color()
    )


def plot_mean(df, x=None, color=None):
    base = alt.Chart(df).encode(
        x=x or alt.X(
            'year:T',
            title='Year'
        ),
        color=color or alt.Color()
    )

    return base.mark_line(interpolate='step-after').encode(
        y=alt.Y(
            'mean:Q',
            title=get_title(df)
        )
    ) + base.mark_area(interpolate='step-after', opacity=0.5).encode(
        y='lower:Q',
        y2='upper:Q'
    )


def plot_map(df, color_scale=None):
    lon = np.sort(df['lon'].unique())
    lat = np.sort(df['lat'].unique())

    lon_size = len(lon)
    lat_size = len(lat)

    lon_bin = float(abs(lon[1] - lon[0]))
    lat_bin = float(abs(lat[1] - lat[0]))

    lon_domain = (lon.min() - 0.5 * lon_bin, lon.max() + 0.5 * lon_bin)
    lat_domain = (lat.min() - 0.5 * lat_bin, lat.max() + 0.5 * lat_bin)

    lon_ticks = np.linspace(lon_domain[0], lon_domain[1], num=7)
    lat_ticks = np.linspace(lat_domain[0], lat_domain[1], num=5)

    return alt.Chart(df).mark_rect().encode(
        x=alt.X(
            'lon:Q',
            title='lon',
            bin=alt.Bin(step=lon_bin),
            axis=alt.Axis(values=lon_ticks),
            scale=alt.Scale(domain=lon_domain, padding=0, round=True)
        ),
        y=alt.Y(
            'lat:Q',
            title='lat',
            bin=alt.Bin(step=lat_bin),
            axis=alt.Axis(values=lat_ticks),
            scale=alt.Scale(domain=lat_domain, padding=0, round=True)
        ),
        color=alt.Color(
            f'{get_var(df)}:Q',
            title=get_title(df),
            scale=color_scale or alt.Scale()
        )
    ).properties(
        width=lon_size,
        height=lat_size
    )
