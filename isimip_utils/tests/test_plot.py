
import numpy as np
import pandas as pd

from isimip_utils.pandas import compute_average, create_label
from isimip_utils.plot import format_title, plot_grid, plot_line, plot_map, save_index, save_plot
from isimip_utils.tests import constants
from isimip_utils.xarray import open_dataset, to_dataframe


def test_plot_line():
    extraction_path = constants.EXTRACTIONS_PATH / constants.TAS_PATH.replace('_global_', '_select-point-cdo_')

    plot_path = constants.PLOTS_PATH / 'plot_line.png'
    plot_path.unlink(missing_ok=True)

    with open_dataset(extraction_path) as ds:
        df = to_dataframe(ds)

    chart = plot_line(df)

    assert chart.data.equals(df)
    assert chart.encoding.x.shorthand == 'time:T'
    assert chart.encoding.y.shorthand == 'tas:Q'

    save_plot(chart, plot_path)

    assert plot_path.is_file


def test_plot_line_nocf():
    extraction_path = constants.EXTRACTIONS_PATH / constants.TAS_PATH.replace('_global_', '_select-point-cdo_')

    plot_path = constants.PLOTS_PATH / 'plot_line_nocf.png'
    plot_path.unlink(missing_ok=True)

    with open_dataset(extraction_path, decode_cf=True) as ds:
        df = to_dataframe(ds)

    chart = plot_line(df, x_type='Q')

    assert chart.data.equals(df)
    assert chart.encoding.x.shorthand == 'time:Q'
    assert chart.encoding.y.shorthand == 'tas:Q'

    save_plot(chart, plot_path)

    assert plot_path.is_file


def test_plot_line_empty():
    extraction_path = constants.EXTRACTIONS_PATH / constants.TAS_PATH.replace('_global_', '_select-point-cdo_')

    plot_path = constants.PLOTS_PATH / 'plot_line_empty.png'
    plot_path.unlink(missing_ok=True)

    with open_dataset(extraction_path) as ds:
        df = to_dataframe(ds)
        df_empty = pd.DataFrame({ 'time': df['time'], 'tas': np.nan })

        chart = plot_line(df, empty=True)

        assert chart.data.equals(df_empty)
        assert chart.encoding.x.shorthand == 'time:T'
        assert chart.encoding.y.shorthand == 'tas:Q'

    save_plot(chart, plot_path)

    assert plot_path.is_file


def test_plot_line_area():
    extraction_path = constants.EXTRACTIONS_PATH / constants.TAS_PATH.replace('_global_', '_select-point-cdo_')

    plot_path = constants.PLOTS_PATH / 'plot_line_area.png'
    plot_path.unlink(missing_ok=True)

    with open_dataset(extraction_path) as ds:
        df = to_dataframe(ds)
        df = compute_average(df, 'tas')

        chart = plot_line(df)

    assert chart.data.equals(df)

    mean, area = chart.layer

    assert mean.encoding.x.shorthand == 'year:T'
    assert mean.encoding.y.shorthand == 'mean:Q'

    assert area.encoding.x.shorthand == 'year:T'
    assert area.encoding.y.shorthand == 'lower:Q'
    assert area.encoding.y2.shorthand == 'upper:Q'

    save_plot(chart, plot_path)

    assert plot_path.is_file


def test_plot_line_color():
    extraction_path = constants.EXTRACTIONS_PATH / constants.TAS_PATH.replace('_global_', '_select-point-cdo_')

    plot_path = constants.PLOTS_PATH / 'plot_line_color.png'
    plot_path.unlink(missing_ok=True)

    with open_dataset(extraction_path) as ds:
        df = to_dataframe(ds)
        df = compute_average(df, 'tas')
        df = create_label(df, ('a', 'b', 'c'))

        chart = plot_line(df, color_scheme='viridis')

    assert chart.data.equals(df)

    mean, area = chart.layer

    assert mean.encoding.x.shorthand == 'year:T'
    assert mean.encoding.y.shorthand == 'mean:Q'

    assert area.encoding.x.shorthand == 'year:T'
    assert area.encoding.y.shorthand == 'lower:Q'
    assert area.encoding.y2.shorthand == 'upper:Q'

    save_plot(chart, plot_path)

    assert plot_path.is_file


def test_plot_map():
    extraction_path = constants.EXTRACTIONS_PATH / constants.TAS_PATH.replace('_global_', '_select-time-cdo_') \
                                                                     .replace('2015_2020', '20180101')

    plot_path = constants.PLOTS_PATH / 'plot_map.png'
    plot_path.unlink(missing_ok=True)

    with open_dataset(extraction_path) as ds:
        df = to_dataframe(ds)
        chart = plot_map(df)

    assert chart.data.equals(df)
    assert chart.encoding.x.shorthand == 'lon:Q'
    assert chart.encoding.y.shorthand == 'lat:Q'
    assert chart.encoding.color.shorthand == 'tas:Q'

    save_plot(chart, plot_path)

    assert plot_path.is_file


def test_plot_map_nocf():
    extraction_path = constants.EXTRACTIONS_PATH / constants.TAS_PATH.replace('_global_', '_select-time-cdo_') \
                                                                     .replace('2015_2020', '20180101')

    plot_path = constants.PLOTS_PATH / 'plot_map_nocf.png'
    plot_path.unlink(missing_ok=True)

    with open_dataset(extraction_path) as ds:
        df = to_dataframe(ds)
        chart = plot_map(df)

    assert chart.data.equals(df)
    assert chart.encoding.x.shorthand == 'lon:Q'
    assert chart.encoding.y.shorthand == 'lat:Q'
    assert chart.encoding.color.shorthand == 'tas:Q'

    save_plot(chart, plot_path)

    assert plot_path.is_file


def test_plot_map_empty():
    extraction_path = constants.EXTRACTIONS_PATH / constants.TAS_PATH.replace('_global_', '_select-time-cdo_') \
                                                                     .replace('2015_2020', '20180101')

    plot_path = constants.PLOTS_PATH / 'plot_map_empty.png'
    plot_path.unlink(missing_ok=True)

    with open_dataset(extraction_path) as ds:
        df = to_dataframe(ds)
        df_empty  = pd.DataFrame({
            'lon': [],
            'lat': []
        })

        chart = plot_map(df, empty=True)

    assert chart.data.equals(df_empty)
    assert chart.encoding.x.shorthand == 'lon:Q'
    assert chart.encoding.y.shorthand == 'lat:Q'

    save_plot(chart, plot_path)

    assert plot_path.is_file


def test_plot_grid():
    extraction_paths = [
        constants.EXTRACTIONS_PATH / dataset_path.replace('_global_', '_select-point-cdo_')
        for dataset_path in constants.TAS_SPLIT_PATHS
    ]

    plot_path = constants.PLOTS_PATH / 'plot_grid.png'
    plot_path.unlink(missing_ok=True)

    dataframes = []
    for extraction_path in extraction_paths:
        with open_dataset(extraction_path) as ds:
            dataframes.append(to_dataframe(ds))

    df_empty = pd.DataFrame({ 'time': dataframes[2]['time'], 'tas': np.nan })

    permutations = [
        ('a', 'x'),
        ('a', 'y'),
        ('b', 'x')
    ]

    plots = {}
    for permutation, df in zip(permutations, dataframes, strict=True):
        plots[permutation] = plot_line(df)

    empty_plot = plot_line(df, empty=True)

    permutations.append(('b', 'y'))

    chart = plot_grid(permutations, plots, x='independent', empty_plot=empty_plot, layer=False)

    top, bottom = chart.vconcat
    top_left, top_right = top.hconcat
    bottom_left, bottom_right = bottom.hconcat

    assert top_left.data.equals(dataframes[0])
    assert top_right.data.equals(dataframes[1])
    assert bottom_left.data.equals(dataframes[2])
    assert bottom_right.data.equals(df_empty)

    for sub_chart in [top_left, top_right, bottom_left, bottom_right]:
        assert sub_chart.resolve.scale.x == 'independent'
        assert sub_chart.resolve.scale.y == 'shared'

    save_plot(chart, plot_path)

    assert plot_path.is_file


def test_save_index():
    index_path = constants.PLOTS_PATH / 'index.html'
    index_path.unlink(missing_ok=True)

    save_index(index_path)

    assert index_path.is_file


def test_format_title():
    permutation = ('a', 'b', 'c')

    assert format_title(permutation) == {
        "text": 'a · b · c',
        "fontSize": 16,
        "dy": -10
    }
