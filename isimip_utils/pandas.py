import numpy as np


def get_var(df):
    return next(iter(df.attrs['data_vars']))


def compute_mean(df, area=True):
    var = get_var(df)
    attrs = df.attrs

    df['year'] = df['time'].dt.year

    kwargs = {'mean': (var, 'mean')}
    if area:
        kwargs['lower'] = (var, lambda y: y.mean() - y.std())
        kwargs['upper'] = (var, lambda y: y.mean() + y.std())

    df = df.groupby('year').agg(**kwargs).reset_index()
    df['mean'] = df['mean'].astype(np.float64)
    df.attrs = attrs

    return df


def group_by_day(df):
    var = get_var(df)

    df['day'] = df['time'].dt.dayofyear
    df = df.groupby('day')[var].mean().reset_index()

    return normalize(df, var)


def group_by_month(df):
    var = get_var(df)

    df['month'] = df['time'].dt.month
    df = df.groupby('month')[var].mean().reset_index()

    return normalize(df, var)


def normalize(df, var):
    mean, std =  df[var].mean(), df[var].std()
    df[var] = (df[var] - mean) / (std if std > 0 else 1.0)
    return df
