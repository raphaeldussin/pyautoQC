import numpy as np


def check_masksize(da, spval=1e+15, x='lon', y='lat', z='lev', time='time'):
    """ Check mask size in xarray.dataarray for all time records
    and return False if size is changing """

    check = True
    message = ''
    # compute the size of the mask in function of depth and time
    nxypts = da[x].size * da[y].size
    oceansize = da.count(dim=[x, y])
    masksize = nxypts - oceansize
    # Check that land sea mask size has reasonable value
    if z in da.dims:
        masksize_surf = masksize.isel({z: 0, time: 0})
    else:
        masksize_surf = masksize.isel({time: 0})
    # land covers 29% of earth surface, we allow 50% relative error
    expected = 0.29 * da[x].size * da[y].size
    if not (0.5 * expected) < masksize_surf.values < (1.5 * expected):
        check = False
        message = message + f'PROBLEM: mask size is not realistic\n'
    # Check that the size does not change over time
    if z in da.dims:
        masksize_sum = masksize.sum(dim=z)
    else:
        masksize_sum = masksize
    tendency = masksize_sum.diff(dim=time)
    if tendency.any() != 0:
        check = False
        message = message + f'PROBLEM: mask size is not constant in time\n'
    if z in da.dims:
        # Check that mask size is increasing with depth
        tendency = masksize.isel({time: 0}).diff(dim=z)
        if tendency.any() < 0:
            check = False
            message = message + f'PROBLEM: mask size is decreasing with depth\n'
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


def check_stats(da, ds_attrs, dirout='./', x='lon', y='lat', z='lev', time='time', tolerance=0.1):
    """ check statistics of variable """
    attrs = dict(ds_attrs)
    check = True
    message = ''
    yearly = da.groupby(da.time.dt.year)
    yearly_mean = yearly.mean(dim=[x, y, time])
    yearly_min = yearly.min(dim=[x, y, time])
    yearly_max = yearly.max(dim=[x, y, time])
    yearly_std = yearly.mean(dim=time).std(dim=y).mean(dim=[x])
    yearmin = yearly_mean['year'].min().values
    yearmax = yearly_mean['year'].max().values
    for year in yearly_mean.year:
        if yearly_mean.sel(year=year).any() == 0.:
            check = False
            message = message + f'PROBLEM: found zero in mean for year {year}\n'
        if yearly_std.sel(year=year).any() == 0.:
            check = False
            message = message + f'PROBLEM: found zero in std deviation for year {year}\n'
#       if not np.allclose(yearly_mean.sel(year=year),
#                          yearly_mean.isel(year=0),
#                          rtol=tolerance):
#           check = False
#           message = message + f'PROBLEM: statistics on yearly means is not within ' + \
#                     f'expected tolerance\n'
#       if not np.allclose(yearly_std.sel(year=year),
#                          yearly_std.isel(year=0),
#                          rtol=tolerance):
#           check = False
#           message = message + f'PROBLEM: statistics on yearly std deviation is ' + \
#                     f'not within expected tolerance\n'

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


    yearly_mean.to_netcdf(filename_mean, unlimited_dims='year')
    yearly_min.to_netcdf(filename_min, unlimited_dims='year')
    yearly_max.to_netcdf(filename_max, unlimited_dims='year')
    yearly_std.to_netcdf(filename_std, unlimited_dims='year')
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
    imin=int(windowsize/2)
    imax=int(-windowsize/2)+1
    test = (array[imin:imax] -
            np.convolve(array, np.ones(windowsize)/windowsize, mode='valid'))
    outlier = (test > 2 * np.std(array))
    return outlier


def check_outlier(variable, ds, z='z'):
    check = True
    message = ''
    if z in ds.dims:
        for k in ds.coords[z].values:
            outlier = find_outlier(ds[variable].sel({z: k}).values.squeeze())
            if outlier.any():
                check = False
                message = f'found outlier at level {k}\n'
    else:
        outlier = find_outlier(ds[variable].values.squeeze())
        if outlier.any():
            check = False
            message = f'found outlier at level {k}\n'
    return check, message
