def get_coord(df):
    return next(iter(df.attrs['coords']))


def get_coord_label(df):
    coord = get_coord(df)
    name = df.attrs['coords'][coord].get('long_name', coord)
    units = df.attrs['coords'][coord].get('units')
    return f'{name} [{units}]' if units else name


def get_coord_axis(df):
    coord = get_coord(df)
    return df.attrs['coords'][coord].get('axis')


def get_data_var(df):
    return next(iter(df.attrs['data_vars']))


def get_data_var_label(df):
    data_var = get_data_var(df)
    data_var_name = df.attrs['data_vars'][data_var].get('long_name', data_var)
    data_var_units = df.attrs['data_vars'][data_var].get('units')
    return f'{data_var_name} [{data_var_units}]' if data_var_units else data_var_name


def compute_average(df, area=True):
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


def group_by_day(df):
    data_var = get_data_var(df)

    df['day'] = df['time'].dt.dayofyear
    df = df.groupby('day')[data_var].mean().reset_index()
    df.attrs['coords'] = {'day': { 'long_name': 'Day of the year'}}

    return df


def group_by_month(df):
    data_var = get_data_var(df)

    df['month'] = df['time'].dt.month
    df = df.groupby('month')[data_var].mean().reset_index()
    df.attrs['coords'] = {'month': {'long_name': 'Month of the year'}}

    return df


def normalize(df):
    data_var = get_data_var(df)
    data_var_long_name = df.attrs['data_vars'][data_var].get('long_name')

    mean, std =  df[data_var].mean(), df[data_var].std()
    df[data_var] = (df[data_var] - mean) / (std if std > 0 else 1.0)
    if data_var_long_name:
        df.attrs['data_vars'][data_var]['long_name'] = f'Normalized {data_var_long_name.lower()}'
    del df.attrs['data_vars'][data_var]['units']

    return df


def create_label(df, labels):
    df['label'] = ' '.join(labels)
    return df
