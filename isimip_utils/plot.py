"""Plotting utilities using Altair for ISIMIP data visualization."""
import json
import logging
from importlib.resources import files
from pathlib import Path
from typing import Any

import altair as alt
import numpy as np
import pandas as pd

from .pandas import (
    get_first_coord,
    get_first_coord_axis,
    get_first_coord_label,
    get_first_data_var,
    get_first_data_var_label,
)

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


def check_plots(plots: dict, path: str | Path):
    """Check whether a set of plots is small enough for Vega to render.

    The limit is empirical: 1,036,800 rows (4 global 0.5-degree grids) renders, 1,296,000 (5 grids) does not.

    Args:
        plots (dict): Dictionary mapping permutation tuples to Chart objects.
        path (str | Path): Output file path, used only for the log message.

    Returns:
        True if the plots can safely be rendered, False if the file should be skipped.
    """

    values_count = sum(int(plot.data.notna().all(axis=1).sum()) for plot in plots.values())
    max_values = 1_036_800
    if values_count > max_values:
        logger.error(f'Too many values ({values_count} > {max_values}) in {path}.')
        return False
    else:
        return True


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
    index_html = files('isimip_utils').joinpath('templates/index.html').read_text(encoding='utf-8')
    index = index_html.replace(r'{{ index_json }}', index_json).strip()

    logger.info(f'save {index_path.absolute()}')
    index_path.parent.mkdir(exist_ok=True, parents=True)
    index_path.write_text(index, encoding='utf-8')


def format_title(
    text: str,
    fontSize: int = 16,
    dy: int = -10,
    **kwargs
) -> dict:
    """Format the plot title.

    Args:
        text (str): Title text. A list of strings can be passed instead to render
            the title across multiple lines.
        fontSize (int): Font size of the title, in pixels (default: 16).
        dy (int): Vertical offset of the title from its anchor, in pixels; negative
            values move it up (default: -10).
        **kwargs: Additional Altair title properties.

    Returns:
        Dictionary with Altair title configuration.
    """
    return {
        **kwargs,
        'text': text,
        'fontSize': fontSize,
        'dy': dy,
    }


def format_legend(
    symbolStrokeWidth: int = 2,
    labelFontSize: int = 14,
    titleFontSize: int = 14,
    labelLimit: int = 0,
    symbolLimit: int = 0,
    direction: str = 'vertical',
    orient: str = 'right',
    columns: int = 1,
    **kwargs
) -> dict:
    """Format the plot legend.

    Args:
        symbolStrokeWidth (int): Stroke width of the legend symbols, in pixels (default: 2).
        labelFontSize (int): Font size of the entry labels, in pixels (default: 14).
        titleFontSize (int): Font size of the legend title, in pixels (default: 14).
        labelLimit (int): Maximum width of an entry label, in pixels; longer labels are
            truncated with an ellipsis. 0 means no limit (default: 0).
        symbolLimit (int): Maximum number of entries to show; 0 means no limit (default: 0).
        direction (str): Layout direction, either 'vertical' or 'horizontal' (default: 'vertical').
        orient (str): Position relative to the chart, e.g. 'left', 'right', 'top', 'bottom',
            'top-left', or 'none' to place it manually (default: 'right').
        columns (int): Number of columns used to lay out symbol legends; ignored for
            gradient legends (default: 1).
        **kwargs: Additional Altair legend properties.

    Returns:
        Dictionary with Altair legend configuration.
    """
    return {
        **kwargs,
        'symbolStrokeWidth': symbolStrokeWidth,
        'labelFontSize': labelFontSize,
        'titleFontSize': titleFontSize,
        'labelLimit': labelLimit,
        'symbolLimit': symbolLimit,
        'direction': direction,
        'orient': orient,
        'columns': columns,
    }


def plot_line(
    df: pd.DataFrame,
    x_field: str | None = None,
    x_label: str | None = None,
    x_type: str | None = None,
    x_format: str | None = None,
    y_field: str | None = None,
    y_label: str | None = None,
    y_type: str | None = None,
    y_format: str | None = None,
    color_field: str | None = None,
    color_type: str | None = None,
    color_domain: list | None = None,
    color_range: list | None = None,
    color_scheme: str | None = None,
    color_title: str | None = None,
    legend: bool = True,
    empty: bool = False,
    **mark_kwargs: Any
) -> alt.Chart:
    """Create a line plot from a DataFrame.

    Args:
        df (pd.DataFrame): DataFrame to plot.
        x_field (str | None): Column name for x-axis (default: auto-detect from attrs).
        x_label (str | None): Label for x-axis (default: auto-detect from attrs).
        x_type (str | None): Altair type for x-axis (default: 'T' for time, 'Q' for quantitative).
        x_format (str | None): Format string for x-axis values.
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
    x_field = get_first_coord(df) if x_field is None else x_field
    x_label = get_first_coord_label(df) if x_label is None else x_label
    x_type = ('T' if get_first_coord_axis(df) == 'T' else 'Q') if x_type is None else x_type
    x = alt.X(
        f'{x_field}:{x_type}',
        title=x_label,
        axis=alt.Axis(format=x_format) if x_format else alt.Axis(),
    )

    y_field = get_first_data_var(df) if y_field is None else y_field
    y_label = get_first_data_var_label(df) if y_label is None else y_label
    y_type = 'Q' if y_type is None else y_type
    y = alt.Y(
        f'{y_field}:{y_type}',
        title=y_label,
        axis=alt.Axis(format=y_format) if y_format else alt.Axis(),
        scale=alt.Scale(zero=False, nice=False)
    )

    color_field =  'label' if color_field is None else color_field
    if empty or color_field not in df:
        color = alt.Color()
    else:
        color_type = 'N' if color_type is None else color_type
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
            legend=alt.Legend(padding=10, title=color_title) if legend else None
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


def plot_map(
    df: pd.DataFrame,
    color_field: str | None = None,
    color_type: str | None = None,
    color_scale: str | None = None,
    color_domain: list | None = None,
    color_range: list | None = None,
    color_scheme: str | None = None,
    color_label: str | None = None,
    color_format: str | None = None,
    bin_size: int = 1,
    legend: bool = True,
    empty: bool = False
) -> alt.Chart:
    """Create a geographic map plot from a DataFrame with lat/lon coordinates.

    Args:
        df (pd.DataFrame): DataFrame with 'lat' and 'lon' columns.
        color_field (str | None): Column name for color encoding (default: auto-detect from attrs).
        color_type (str | None): Altair type for color (default: 'Q').
        color_scale (list | None): Custom type for the color scale.
        color_domain (list | None): Custom domain for the color scale.
        color_range (list | None): Custom range for color scale.
        color_scheme (str | None): Custom scheme for color scale.
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
        color_field = get_first_data_var(df) if color_field is None else color_field
        color_type = 'Q' if color_type is None else color_type
        color_label = get_first_data_var_label(df) if color_label is None else color_label

        color_scale_args = {}
        if color_scale:
            color_scale_args['type'] = color_scale
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


def plot_grid(
    grid_permutations: list[tuple],
    plot_permutations: list[tuple],
    plots: dict,
    empty_plot: alt.Chart,
    x: str = "shared",
    y: str = "shared",
    color: str = "shared",
) -> alt.Chart:
    """Create a grid of plots organized by parameter permutations.

    Args:
        grid_permutations (list): List the permutations (with tuples of parameters) which span the grid.
        plot_permutations (list): List the permutations (with tuples of parameters) for each plot.
        plots (dict): Dictionary mapping permutation tuples to Chart objects.
        empty_plot (alt.Chart): Chart to use when a permutation has no data.
        x (str): Scale resolution for x-axis ('shared', 'independent', default: 'shared').
        y (str): Scale resolution for y-axis ('shared', 'independent', default: 'shared').
        color (str): Scale resolution for color ('shared', 'independent', default: 'shared').

    Returns:
        Altair Chart object with grid layout.
    """
    rows = []
    prev = None

    for grid_permutation in grid_permutations:
        row_title = grid_permutation[0] if len(grid_permutation) > 0 else ''
        column_title = grid_permutation[1] if len(grid_permutation) > 1 else ''

        if prev is None or (len(grid_permutation) > 0 and grid_permutation[0] != prev[0]):
            # start a new row
            column = []
            row = [(column_title, column)]
            rows.append((row_title, row))
        elif prev is None or (len(grid_permutation) > 1 and grid_permutation[1] != prev[1]):
            # start a new column
            column = []
            row.append((column_title, column))

        for plot_permutation in plot_permutations:
            plot = plots.get(grid_permutation + plot_permutation)
            if plot:
                column.append(plot)

        prev = grid_permutation

    chart = alt.vconcat(*[
        alt.hconcat(*[
            alt.layer(*column, title=column_title) if column else empty_plot
            for column_title, column in row
        ], title=row_title).resolve_scale(x=x, y=y)
        for row_title, row in rows
    ]).resolve_scale(x=x, y=y)

    return chart
