"""Pandas DataFrame utilities for ISIMIP data."""
import pandas as pd


def get_coord(df: pd.DataFrame) -> str:
    """Get the first coordinate name from DataFrame attributes.

    Args:
        df (pd.DataFrame): DataFrame with 'coords' in attrs.

    Returns:
        Name of the first coordinate.
    """
    return next(iter(df.attrs['coords']))


def get_coord_label(df: pd.DataFrame) -> str:
    """Get a formatted label for the coordinate with units.

    Args:
        df (pd.DataFrame): DataFrame with 'coords' in attrs.

    Returns:
        Formatted string like "Coordinate Name [units]" or just the name if no units.
    """
    coord = get_coord(df)
    name = df.attrs['coords'][coord].get('long_name', coord)
    units = df.attrs['coords'][coord].get('units')
    return f'{name} [{units}]' if units else name


def get_coord_axis(df: pd.DataFrame) -> str | None:
    """Get the axis attribute for the coordinate.

    Args:
        df (pd.DataFrame): DataFrame with 'coords' in attrs.

    Returns:
        Axis attribute (e.g., 'T', 'X', 'Y'), or None if not set.
    """
    coord = get_coord(df)
    return df.attrs['coords'][coord].get('axis')


def get_data_var(df: pd.DataFrame) -> str:
    """Get the first data variable name from DataFrame attributes.

    Args:
        df (pd.DataFrame): DataFrame with 'data_vars' in attrs.

    Returns:
        Name of the first data variable.
    """
    return next(iter(df.attrs['data_vars']))


def get_data_var_label(df: pd.DataFrame) -> str:
    """Get a formatted label for the data variable with units.

    Args:
        df (pd.DataFrame): DataFrame with 'data_vars' in attrs.

    Returns:
        Formatted string like "Variable Name [units]" or just the name if no units.
    """
    data_var = get_data_var(df)
    data_var_name = df.attrs['data_vars'][data_var].get('long_name', data_var)
    data_var_units = df.attrs['data_vars'][data_var].get('units')
    return f'{data_var_name} [{data_var_units}]' if data_var_units else data_var_name


def compute_average(df: pd.DataFrame, area: bool = True) -> pd.DataFrame:
    """Compute yearly average with optional standard deviation bounds.

    Args:
        df (pd.DataFrame): DataFrame with time column and data variable.
        area (bool): Whether to include lower/upper bounds using std (default: True).

    Returns:
        DataFrame with yearly aggregated data.
    """
    data_var = get_data_var(df)
    data_var_long_name = df.attrs['data_vars'][data_var].get('long_name')
    data_var_units = df.attrs['data_vars'][data_var].get('units')

    attrs = df.attrs

    df['year'] = df['time'].dt.year

    kwargs = {'mean': (data_var, 'mean')}
    if area:
        kwargs['lower'] = (data_var, lambda y: y.mean() - y.std())
        kwargs['upper'] = (data_var, lambda y: y.mean() + y.std())

    df = df.groupby('year').agg(**kwargs).reset_index()

    # cast to double
    df['mean'] = df['mean'].astype('float64')
    if area:
        df['lower'] = df['lower'].astype('float64')
        df['upper'] = df['upper'].astype('float64')

    # update attrs
    df.attrs = attrs
    df.attrs['coords'] = {'year': {'long_name': 'Year', 'axis': 'T'}}
    df.attrs['data_vars'] = { 'mean': {} }
    if data_var_long_name:
        df.attrs['data_vars']['mean']['long_name'] = f'Average {data_var_long_name.lower()}'
    if data_var_units:
        df.attrs['data_vars']['mean']['units'] = data_var_units

    return df


def group_by_day(df: pd.DataFrame) -> pd.DataFrame:
    """Group data by day of year and compute mean.

    Args:
        df (pd.DataFrame): DataFrame with time column and data variable.

    Returns:
        DataFrame grouped by day of year (1-365/366).
    """
    data_var = get_data_var(df)

    df['day'] = df['time'].dt.dayofyear
    df = df.groupby('day')[data_var].mean().reset_index()
    df.attrs['coords'] = {'day': { 'long_name': 'Day of the year'}}

    return df


def group_by_month(df: pd.DataFrame) -> pd.DataFrame:
    """Group data by month and compute mean.

    Args:
        df (pd.DataFrame): DataFrame with time column and data variable.

    Returns:
        DataFrame grouped by month (1-12).
    """
    data_var = get_data_var(df)

    df['month'] = df['time'].dt.month
    df = df.groupby('month')[data_var].mean().reset_index()
    df.attrs['coords'] = {'month': {'long_name': 'Month of the year'}}

    return df


def normalize(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize data variable using z-score normalization.

    Args:
        df (pd.DataFrame): DataFrame with data variable to normalize.

    Returns:
        DataFrame with normalized data variable (mean=0, std=1).
    """
    data_var = get_data_var(df)
    data_var_long_name = df.attrs['data_vars'][data_var].get('long_name')

    mean, std =  df[data_var].mean(), df[data_var].std()
    df[data_var] = (df[data_var] - mean) / (std if std > 0 else 1.0)
    if data_var_long_name:
        df.attrs['data_vars'][data_var]['long_name'] = f'Normalized {data_var_long_name.lower()}'
    del df.attrs['data_vars'][data_var]['units']

    return df


def create_label(df: pd.DataFrame, labels: list[str]) -> pd.DataFrame:
    """Add a label column to DataFrame by joining label strings.

    Args:
        df (pd.DataFrame): DataFrame to add label to.
        labels (list[str]): List of label strings to join with spaces.

    Returns:
        DataFrame with added 'label' column.
    """
    df['label'] = ' '.join(labels)
    return df
