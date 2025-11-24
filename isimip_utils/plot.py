"""Plotting utilities using Altair for ISIMIP data visualization."""
import json
import logging
from pathlib import Path
from typing import Any

import altair as alt
import numpy as np
import pandas as pd

from isimip_utils.pandas import (
    get_first_coord,
    get_first_coord_axis,
    get_first_coord_label,
    get_first_data_var,
    get_first_data_var_label,
)
from isimip_utils.utils import get_permutations

logger = logging.getLogger(__name__)

alt.data_transformers.enable('vegafusion')

@alt.theme.register('isimip_utils', enable=True)
def custom_theme():
    return alt.theme.ThemeConfig({
        "config": {
            "mark": {
                "color": "steelblue"
            }
        }
    })


def save_plot(chart: alt.Chart, path: str | Path, *args: Any, **kwargs: Any) -> None:
    """Save an Altair chart to a file.

    Args:
        chart (alt.Chart): Altair chart to save.
        path (str | Path): Output file path.
        *args (Any): Additional positional arguments for chart.save().
        **kwargs (Any): Additional keyword arguments for chart.save().
    """
    path = Path(path)

    logger.info(f'save {path.absolute()}')
    path.parent.mkdir(exist_ok=True, parents=True)
    chart.save(path, *args, **kwargs)


def save_index(index_path: Path) -> None:
    """Save an HTML index file for browsing plot images.

    Creates an interactive HTML page for viewing SVG/PNG files in a directory.

    Args:
        index_path (Path): Path where the index.html file will be saved.
    """
    index_json = json.dumps([
        str(p.name) for p in sorted(index_path.parent.iterdir()) if p.suffix in ['.svg', '.png']
    ], indent=2).replace('\n', '\n    ')

    logger.info(f'save {index_path.absolute()}')
    index_path.with_suffix('.html').write_text(r'''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <style>
    body { height: 100%; margin: 0; font-family: sans-serif; font-size: 12px; }
    div.buttons { display: flex; gap: 10px; align-items: center; padding: 10px; border-bottom: 1px solid silver; }
    a { display: block; flex-grow: 1; line-height: 20px; text-decoration: none; color: #0681be }
    a:hover { text-decoration: underline; }
    button { background: none; border: none; height: 20px; padding: 0; margin: 0; cursor: pointer; }
    button:not(:disabled):hover { color: #0681be }
    div.img { display: flex; justify-content: center; margin-top: 10px; }
    img { display: block; max-width: calc(100vw - 20px); max-height: calc(100vh - 80px); }
  </style>
</head>
<body>
  <div class="buttons">
    <a id="file" target="_blank"></a>
    <span id="count"></span>
    <button id="prev">◀ Prev</button>
    <button id="next">Next ▶</button>
  </div>
  <div class="img">
    <img id="img" />
  </div>
  <script>
    const e = ['img', 'file', 'count', 'prev', 'next'].reduce(
      (obj, id) => ({...obj, [id]: document.getElementById(id)}), {}
    )

    const files = {{ index_json }}

    let index = 0

    const update = () => {
      e.img.src = files[index]
      e.file.href = files[index]
      e.file.innerHTML = files[index]
      e.count.innerHTML = `${index + 1} of ${files.length}`
      e.prev.disabled = index === 0
      e.next.disabled = index === files.length - 1
    }

    e.prev.onclick = () => { if (index > 0) index--; update(); }
    e.next.onclick = () => { if (index < files.length - 1) index++; update(); }

    update()
  </script>
</body>
</html>'''.replace(r'{{ index_json }}', index_json).strip())


def get_plot_title(permutation: tuple) -> dict:
    """Create a plot title from a permutation tuple.

    Args:
        permutation (tuple): Tuple of strings to join as title.

    Returns:
        Dictionary with Altair title configuration.
    """
    return {
        "text": ' · '.join(permutation),
        "fontSize": 16,
        "dy": -10
    }


def plot_line(df: pd.DataFrame, x_field: str | None = None, x_label: str | None = None,
              x_type: str | None = None, y_field: str | None = None, y_label: str | None = None,
              y_type: str | None = None, y_format: str | None = None, color_field: str | None = None,
              color_type: str | None = None, color_domain: list | None = None, color_range: list | None = None,
              color_scheme: str | None = None, color_title: str | None = 'Legend', legend: bool = True,
              empty: bool = False, **mark_kwargs: Any) -> alt.Chart:
    """Create a line plot from a DataFrame.

    Args:
        df (pd.DataFrame): DataFrame to plot.
        x_field (str | None): Column name for x-axis (default: auto-detect from attrs).
        x_label (str | None): Label for x-axis (default: auto-detect from attrs).
        x_type (str | None): Altair type for x-axis (default: 'T' for time, 'Q' for quantitative).
        y_field (str | None): Column name for y-axis (default: auto-detect from attrs).
        y_label (str | None): Label for y-axis (default: auto-detect from attrs).
        y_type (str | None): Altair type for y-axis (default: 'Q').
        y_format (str | None): Format string for y-axis values.
        color_field (str | None): Column name for color encoding (default: 'label').
        color_type (str | None): Altair type for color (default: 'N').
        color_domain (list | None): Custom color domain.
        color_range (list | None): Custom color range for scale.
        color_scheme (str | None): Custom color scheme for scale.
        color_title (str | None): Title for color (default: 'Legend').
        legend (bool): Whether to show legend (default: True).
        empty (bool): Whether to create an empty plot with NaN values (default: False).
        **mark_kwargs (Any): Additional keyword arguments for mark_line().

    Returns:
        Altair Chart object with line plot (and optional area for lower/upper bounds).
    """

    x_field = x_field or get_first_coord(df)
    x_label = x_label or get_first_coord_label(df)
    x_type = x_type or ('T' if get_first_coord_axis(df) == 'T' else 'Q')
    x = alt.X(
        f'{x_field}:{x_type}',
        title=x_label
    )

    y_field = y_field or get_first_data_var(df)
    y_label = y_label or get_first_data_var_label(df)
    y_type = y_type or 'Q'
    y = alt.Y(
        f'{y_field}:{y_type}',
        title=y_label,
        axis=alt.Axis(format=y_format) if y_format else alt.Axis(),
        scale=alt.Scale(zero=False, nice=False)
    )

    color_field = color_field or 'label'
    if empty or color_field not in df:
        color = alt.Color()
    else:
        color_type = color_type or 'N'
        color_scale_args = {}
        if color_domain:
            color_scale_args['domain'] = color_domain
        if color_range:
            color_scale_args['range'] = color_range
        if color_scheme:
            color_scale_args['scheme'] = color_scheme

        color_legend_args = {}
        if color_title:
            color_legend_args['title'] = color_title

        color = alt.Color(
            f'{color_field}:{color_type}',
            scale=alt.Scale(**color_scale_args),
            legend=alt.Legend(padding=10, **color_legend_args) if legend else None
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


def plot_map(df: pd.DataFrame, color_field: str | None = None, color_type: str | None = None,
             color_domain: list | None = None, color_range: list | None = None, color_scheme: str | None = None,
             color_label: str | None = None, color_format: str | None = None, bin_size: int = 1, legend: bool = True,
             empty: bool = False) -> alt.Chart:
    """Create a geographic map plot from a DataFrame with lat/lon coordinates.

    Args:
        df (pd.DataFrame): DataFrame with 'lat' and 'lon' columns.
        color_field (str | None): Column name for color encoding (default: auto-detect from attrs).
        color_type (str | None): Altair type for color (default: 'Q').
        color_domain (list | None): Custom color domain.
        color_range (list | None): Custom color range for scale.
        color_scheme (str | None): Custom color scheme for scale.
        color_label (str | None): Label for color legend (default: auto-detect from attrs).
        color_format (str | None): Format string for color legend values.
        bin_size (int): Bin size for aggregating grid cells (default: 1).
        legend (bool): Whether to show legend (default: True).
        empty (bool): Whether to create an empty plot (default: False).

    Returns:
        Altair Chart object with rectangular heatmap.
    """
    lon = np.sort(df['lon'].unique())
    lon_size = len(lon)
    lon_bin = float(abs(lon[1] - lon[0])) * bin_size
    lon_domain = (lon.min() - 0.5 * lon_bin, lon.max() + 0.5 * lon_bin)
    lon_ticks = np.linspace(lon_domain[0], lon_domain[1], num=7)

    x = alt.X(
        'lon:Q',
        title='lon',
        bin=alt.Bin(step=lon_bin),
        axis=alt.Axis(values=lon_ticks),
        scale=alt.Scale(domain=lon_domain, padding=0, round=True)
    )

    lat = np.sort(df['lat'].unique())
    lat_size = len(lat)
    lat_bin = float(abs(lat[1] - lat[0])) * bin_size
    lat_domain = (lat.min() - 0.5 * lat_bin, lat.max() + 0.5 * lat_bin)
    lat_ticks = np.linspace(lat_domain[0], lat_domain[1], num=5)

    y = alt.Y(
        'lat:Q',
        title='lat',
        bin=alt.Bin(step=lat_bin),
        axis=alt.Axis(values=lat_ticks),
        scale=alt.Scale(domain=lat_domain, padding=0, round=True)
    )

    if empty:
        color = alt.Color()
    else:
        color_field = color_field or get_first_data_var(df)
        color_type = color_type or 'Q'
        color_label = color_label or get_first_data_var_label(df)

        color_scale_args = {}
        if color_domain:
            color_scale_args['domain'] = color_domain
        if color_range:
            color_scale_args['range'] = color_range
        if color_scheme:
            color_scale_args['scheme'] = color_scheme

        color_legend_args = {}
        if color_format:
            color_legend_args['format'] = color_format

        color = alt.Color(
            f'{color_field}:{color_type}',
            title=color_label,
            scale=alt.Scale(**color_scale_args),
            legend=alt.Legend(padding=10, **color_legend_args) if legend else None
        )

    if empty:
        df = pd.DataFrame({
            'lon': [],
            'lat': []
        })

    return alt.Chart(df).mark_rect().encode(x=x, y=y, color=color).properties(
        width=lon_size,
        height=lat_size
    )


def plot_grid(parameters: dict, plots: dict, empty_plot: alt.Chart, layer: bool = True,
              x: str = 'shared', y: str = 'shared', color: str = 'shared') -> alt.Chart:
    """Create a grid of plots organized by parameter permutations.

    Args:
        parameters (dict): Dictionary of parameters with lists of values.
        plots (dict): Dictionary mapping permutation tuples to Chart objects.
        empty_plot (alt.Chart): Chart to use when a permutation has no data.
        layer (bool): Whether to layer plots or concatenate vertically (default: True).
        x (str): Scale resolution for x-axis ('shared', 'independent', default: 'shared').
        y (str): Scale resolution for y-axis ('shared', 'independent', default: 'shared').
        color (str): Scale resolution for color ('shared', 'independent', default: 'shared').

    Returns:
        Altair Chart object with grid layout.
    """
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
