import logging
from pathlib import Path

import altair as alt
import numpy as np
import pandas as pd

from isimip_utils.pandas import get_coord, get_coord_axis, get_coord_label, get_data_var, get_data_var_label
from isimip_utils.utils import get_permutations

logger = logging.getLogger(__name__)


def default_color_theme():
    return {
        "config": {
            "mark": {"color": "steelblue"}
        }
    }


alt.data_transformers.enable('vegafusion')
alt.themes.register("default_color_theme", default_color_theme)
alt.themes.enable("default_color_theme")


def save_plot(chart, path, *args, **kwargs):
    path = Path(path)

    logger.info(f'save {path.absolute()}')
    path.parent.mkdir(exist_ok=True, parents=True)
    chart.save(path, *args, **kwargs)


def get_plot_title(permutation):
    return {
        "text": ' · '.join(permutation),
        "fontSize": 16,
        "dy": -10
    }


def plot_line(df, x_field=None, x_label=None, x_type=None,
                  y_field=None, y_label=None, y_type=None, y_format=None,
                  color_field=None, color_type=None, color_range=None,
                  legend=True, empty=False, **mark_kwargs):

    x_field = x_field or get_coord(df)
    x_label = x_label or get_coord_label(df)
    x_type = x_type or ('T' if get_coord_axis(df) == 'T' else 'Q')
    x = alt.X(
        f'{x_field}:{x_type}',
        title=x_label
    )

    y_field = y_field or get_data_var(df)
    y_label = y_label or get_data_var_label(df)
    y_type = y_type or 'Q'
    y = alt.Y(
        f'{y_field}:{y_type}',
        title=y_label,
        axis=alt.Axis(format=y_format) if y_format else alt.Axis(),
        scale=alt.Scale(zero=False, nice=False)
    )

    if empty:
        color = alt.Color()
    else:
        color_field = color_field or 'label'
        color_type = color_type or 'N'
        color = alt.Color(
            f'{color_field}:{color_type}',
            scale=alt.Scale(range=color_range) if color_range else alt.Scale(),
            legend=alt.Legend(title='Legend', padding=10) if legend else None
        )

    if empty:
        df = pd.DataFrame({
            x_field: df[x_field],
            y_field: np.full_like(df[y_field], np.nan, dtype=float)
        })

    # the base chart contains only the x axis
    base = alt.Chart(df).mark_line(**mark_kwargs).encode(x=x)

    chart = base.mark_line(**mark_kwargs).encode(y=y, color=color)

    if 'lower' in df and 'upper' in df:
        chart += base.mark_area(**mark_kwargs, opacity=0.5).encode(
            y='lower:Q',
            y2='upper:Q',
            color=color
        )

    return chart


def plot_map(df, x=None, y=None, color=None, empty=False):
    if not x:
        lon = np.sort(df['lon'].unique())
        lon_size = len(lon)
        lon_bin = float(abs(lon[1] - lon[0]))
        lon_domain = (lon.min() - 0.5 * lon_bin, lon.max() + 0.5 * lon_bin)
        lon_ticks = np.linspace(lon_domain[0], lon_domain[1], num=7)

        x = alt.X(
            'lon:Q',
            title='lon',
            bin=alt.Bin(step=lon_bin),
            axis=alt.Axis(values=lon_ticks),
            scale=alt.Scale(domain=lon_domain, padding=0, round=True)
        )

    if not y:
        lat = np.sort(df['lat'].unique())
        lat_size = len(lat)
        lat_bin = float(abs(lat[1] - lat[0]))
        lat_domain = (lat.min() - 0.5 * lat_bin, lat.max() + 0.5 * lat_bin)
        lat_ticks = np.linspace(lat_domain[0], lat_domain[1], num=5)

        y = alt.Y(
            'lat:Q',
            title='lat',
            bin=alt.Bin(step=lat_bin),
            axis=alt.Axis(values=lat_ticks),
            scale=alt.Scale(domain=lat_domain, padding=0, round=True)
        )

    if not color:
        color_field = get_data_var(df)
        color_label = get_data_var_label(df)

        color = alt.Color(
            f'{color_field}:Q',
            title=color_label,
            scale=alt.Scale()
        )

    if empty:
        df = pd.DataFrame({'lon': [], 'lat': [], color.to_dict().get('field'): []})

    return alt.Chart(df).mark_rect().encode(x=x, y=y, color=color).properties(
        width=lon_size,
        height=lat_size
    )


def plot_grid(parameters, plots, empty_plot, layer=True, x='shared', y='shared', color='shared'):
    rows = []
    prev_permutation = None

    for permutation in get_permutations(parameters):
        row_title = permutation[0] if len(permutation) > 0 else ''
        column_title = permutation[1] if len(permutation) > 1 else ''

        if prev_permutation is None or (len(permutation) > 0 and permutation[0] != prev_permutation[0]):
            # start a new row
            column = []
            row = [(column_title, column)]
            rows.append((row_title, row))
        elif prev_permutation is None or (len(permutation) > 1 and permutation[1] != prev_permutation[1]):
            # start a new column
            column = []
            row.append((column_title, column))

        plot = plots.get(permutation, empty_plot)
        if not layer:
            plot = plot.properties(title=' '.join(permutation[2:]))

        column.append(plot)

        prev_permutation = permutation

    chart = alt.vconcat(*[
        alt.hconcat(*[
            alt.layer(*column, title=column_title)
            if layer else
            alt.vconcat(*column, title=column_title).resolve_scale(x=x, y=y, color=color)
            for column_title, column in row
        ], title=row_title).resolve_scale(x=x, y=y)
        for row_title, row in rows
    ]).resolve_scale(x=x, y=y)

    return chart
