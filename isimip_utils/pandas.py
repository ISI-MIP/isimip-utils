def get_var(df):
    return next(iter(df.attrs['data_vars']))


def compute_area(df):
    var = get_var(df)
    attrs = df.attrs

    df['year'] = df['time'].dt.year

    df = df.groupby('year').agg(
        mean=(var, 'mean'),
        lower=(var, lambda y: y.mean() - y.std()),
        upper=(var, lambda y: y.mean() + y.std())
    ).reset_index()

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
