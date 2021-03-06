import numpy as np
import matplotlib.pylab as plt
try:
    import nc_time_axis
except ImportError:
    print('please run conda install -c conda-forge nc-time-axis')


def check_masksize(da, spval=1e+15, x='lon', y='lat', z='lev', time='time'):
    """ Check mask size in xarray.dataarray for all time records
    and return False if size is changing """

    check = True
    message = ''
    # check that there is no values greater than missing value (bad missing)
    if '_FillValue' in da.encoding:
        expected_fill = da.encoding['_FillValue']
    else:
        check = False
        message = message + f'PROBLEM: found FillValue is not set\n'
        expected_fill = 1.e+20
    if np.abs(da.values).max() > expected_fill:
        check = False
        message = message + f'PROBLEM: found value greater than FillValue\n'
    # compute the size of the mask in function of depth and time
    nxypts = da[x].size * da[y].size
    oceansize = da.count(dim=[x, y])
    masksize = nxypts - oceansize
    # Check that land sea mask size has reasonable value
    if z in da.dims:
        masksize_surf = masksize.isel({z: 0})
    else:
        masksize_surf = masksize
    if 'time' in da.dims:
        masksize_surf_init = masksize_surf.isel({'time': 0})
    else:
        masksize_surf_init = masksize_surf
    # land covers 29% of earth surface, we allow 50% relative error
    expected = 0.29 * da[x].size * da[y].size
    if not (0.5 * expected) < masksize_surf_init.values < (1.5 * expected):
        check = False
        message = message + f'PROBLEM: mask size is not realistic\n'
    # Check that the size does not change over time
    if 'time' in da.dims:
        if z in da.dims:
            masksize_sum = masksize.sum(dim=z)
        else:
            masksize_sum = masksize
        tendency = masksize_sum.diff(dim=time)
        if tendency.any() != 0:
            check = False
            message = message + f'PROBLEM: mask size is not constant in time\n'
    # Check that mask size is increasing with depth
    if z in da.dims:
        if 'time' in da.dims:
            tendency = masksize.isel({time: 0}).diff(dim=z)
        else:
            tendency = masksize.diff(dim=z)
        if tendency.any() < 0:
            check = False
            message = message + f'PROBLEM: mask size is decreasing ' + \
                                f'with depth\n'
    return check, message


def check_timeaxis(ds, time='time'):
    """ check the time axis """

    check = True
    message = ''
    attrs = dict(ds.attrs)
    expected_freq = attrs['frequency']
    if expected_freq == 'mon':
        expected_min = np.timedelta64(28, 'D')
        expected_max = np.timedelta64(31, 'D')
    elif expected_freq == '3hr':
        expected_min = np.timedelta64(3, 'h')
        expected_max = np.timedelta64(3, 'h')
    #  elif other frequency (add here)

    tendency = ds[time].diff(dim=time)
    for dt in tendency:
        if not expected_min <= dt <= expected_max:
            check = False
            message = message + f'PROBLEM: records are not correctly spaced\n'
    return check, message


def check_second_derivative(da, x='lon', y='lat', z='lev', time='time'):
    """ check for zero second derivative """

    check = True
    message = ''

    curv_x = da.diff(dim=x, n=2)

    if curv_x.values.any() == 0:
        check = False
        message = message + f'PROBLEM: contiguous values along x axis\n'

    return check, message


def check_stats(da, ds_attrs, dirout='./', x='lon', y='lat', z='lev',
                time='time', tolerance=0.1):
    """ check statistics of variable """
    attrs = dict(ds_attrs)
    check = True
    message = ''
    ts_min = da.min(dim=[x, y])
    ts_max = da.max(dim=[x, y])
    ts_mean = da.mean(dim=[x, y])
    # ts_std = da.mean(dim=time).std(dim=y).mean(dim=[x])
    # yearly = da.groupby(da.time.dt.year)
    # yearly_mean = yearly.mean(dim=[x, y, time])
    # yearly_min = yearly.min(dim=[x, y, time])
    # yearly_max = yearly.max(dim=[x, y, time])
    # yearly_std = yearly.mean(dim=time).std(dim=y).mean(dim=[x])
    # yearmin = str(yearly['year'].min().values).zfill(4)
    # yearmax = str(yearly['year'].max().values).zfill(4)
    yearmin = str(da[time].dt.year.min().values).zfill(4)
    yearmax = str(da[time].dt.year.max().values).zfill(4)
#    for year in yearly_mean.year:
#        if yearly_mean.sel(year=year).any() == 0.:
#            check = False
#            message = message + f'PROBLEM: found zero in mean ' + \
#                                f'for year {year}\n'
#        if yearly_std.sel(year=year).any() == 0.:
#            check = False
#            message = message + f'PROBLEM: found zero in std deviation ' + \
#                                f'for year {year}\n'
# THIS IS MAKING FALSE POSITIVE, NOT GOOD USE OF STATS
#       if not np.allclose(yearly_mean.sel(year=year),
#                          yearly_mean.isel(year=0),
#                          rtol=tolerance):
#           check = False
#           message = message + f'PROBLEM: statistics on yearly means is ' + \
#                     f'not within expected tolerance\n'
#       if not np.allclose(yearly_std.sel(year=year),
#                          yearly_std.isel(year=0),
#                          rtol=tolerance):
#           check = False
#           message = message + f'PROBLEM: statistics on yearly ' + \
#                     f'deviation is not within expected tolerance\n'

    filename_mean = f"{dirout}/QC_{attrs['source_id']}-" + \
                    f"{attrs['experiment_id']}_{attrs['grid_label']}_" + \
                    f"mean_{da.name}_{yearmin}-{yearmax}.nc"

    filename_min = f"{dirout}/QC_{attrs['source_id']}-" + \
                   f"{attrs['experiment_id']}_{attrs['grid_label']}_" + \
                   f"min_{da.name}_{yearmin}-{yearmax}.nc"

    filename_max = f"{dirout}/QC_{attrs['source_id']}-" + \
                   f"{attrs['experiment_id']}_{attrs['grid_label']}_" + \
                   f"max_{da.name}_{yearmin}-{yearmax}.nc"

    filename_std = f"{dirout}/QC_{attrs['source_id']}-" + \
                   f"{attrs['experiment_id']}_{attrs['grid_label']}_" + \
                   f"std_{da.name}_{yearmin}-{yearmax}.nc"

    # yearly_mean.to_netcdf(filename_mean, unlimited_dims='year')
    ts_mean.load()

    # test for field zero-ed out
    if (ts_mean == 0).any():
        check = False
        message = message + f'PROBLEM: statistics on mean ' + \
                  f'shows all field = 0\n'

    ts_mean.to_netcdf(filename_mean, unlimited_dims='year')

    ts_min.load()
    ts_min.to_netcdf(filename_min, unlimited_dims='time')

    ts_max.load()
    ts_max.to_netcdf(filename_max, unlimited_dims='time')
    # yearly_min.to_netcdf(filename_min, unlimited_dims='year')
    # yearly_max.to_netcdf(filename_max, unlimited_dims='year')
    # yearly_std.to_netcdf(filename_std, unlimited_dims='year')
    return check, message


def compute_spatial_average(variable, ds, ds_area=None, ds_vol=None,
                            x='lon', y='lat', z='lev', time='time'):
    """ compute the 2d/3d average of array """
    if z in ds[variable].dims:  # 3D case
        if ds_vol is None:  # we have already merged volcello in ds
            volume = ds['volcello']
        else:  # we need volcello from different dataset
            volume = ds_vol['volcello']
        weighted = (ds[variable] * volume).sum(dim=[x, y, z], skipna=True)
        norm = volume.sum(dim=[x, y, z], skipna=True)
        average = weighted / norm
    else:  # 2D case
        if ds_area is None:
            area = ds['areacello']
        else:
            area = ds_area['areacello']
        weighted = (ds[variable] * area).sum(dim=[x, y], skipna=True)
        norm = area.sum(dim=[x, y], skipna=True)
        average = weighted / norm
    return average


def find_outlier(array, windowsize=12):
    test = (array - rmean(array, t=windowsize))
    outlier = (np.abs(test) > 3 * np.std(array))
    return outlier


def check_outlier(variable, ds, z='z', windowsize=12, time='time', tag='',
                  output='./'):
    check = True
    message = ''
    if z in ds.dims:
        for k in ds.coords[z].values:
            da = ds[variable].sel({z: k}).sortby(ds[time])
            outlier = find_outlier(da.values.squeeze(),
                                   windowsize=windowsize)
            if outlier.any():
                outlier_time = ds[time].where(outlier).dropna(dim=time).values
                check = False
                message = f'PROBLEM: found outlier at depth {k} in ' + \
                          f'date(s) {outlier_time}\n'
                make_outlier_plot(da, outlier, tag=f"{tag}_z{da[z].values}",
                                  output=output)
    else:
        da = ds[variable].sortby(ds[time])
        outlier = find_outlier(da.values.squeeze(),
                               windowsize=windowsize)
        if outlier.any():
            outlier_time = ds[time].where(outlier).dropna(dim=time).values
            check = False
            message = f'PROBLEM: found outlier in year(s) {outlier_time}\n'
            make_outlier_plot(da, outlier, tag=f"{tag}", output=output)
    return check, message


def rmean(a, t=12):
    r = np.zeros(a.shape)
    r[0] = a[0]
    alpha = 1/t
    for k in range(1, a.shape[0]):
        r[k] = alpha * a[k] + (1-alpha) * r[k-1]
    return r


def make_outlier_plot(da, outlier, tag='', output='./'):
    ''' make the plot with outlier in red '''
    filename = f"{output}/{da.name}_{tag}.png"
    da.plot.line(x='time')
    da.where(outlier).plot.line(x='time', color='k', marker='o')
    plt.savefig(filename)
    plt.close()
    return None
