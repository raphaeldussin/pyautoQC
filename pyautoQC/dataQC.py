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
    # land covers 29% of earth surface, we allow 30% error
    expected = 0.29 * da[x].size * da[y].size
    if not (0.7 * expected) < masksize_surf.values < (1.3 * expected):
        check = False
        message = 'PROBLEM: mask size is not realistic'
        return check, message
    # Check that the size does not change over time
    if z in da.dims:
        masksize_sum = masksize.sum(dim=z)
    else:
        masksize_sum = masksize
    tendency = masksize_sum.diff(dim=time)
    if tendency.any() != 0:
        check = False
        message = 'PROBLEM: mask size is not constant in time'
        return check, message
    if z in da.dims:
        # Check that mask size is increasing with depth
        tendency = masksize.isel({time: 0}).diff(dim=z)
        if tendency.any() < 0:
            check = False
            message = 'PROBLEM: mask size is decreasing with depth'
            return check, message
    # normal case
    return check, message


def check_timeaxis(ds, time='time'):
    """ check the time axis """

    check = True
    message = ''
    tendency = ds[time].diff(dim=time)
    for dt in tendency:
        if not np.timedelta64(28, 'D') <= dt <= np.timedelta64(31, 'D'):
            check = False
            message = 'PROBLEM: records are not correctly spaced'
    return check, message


def check_second_derivative(da, x='lon', y='lat', z='lev', time='time'):
    """ check for zero second derivative """

    check = True
    message = ''

    curv_x = da.diff(dim=x, n=2)
    curv_y = da.diff(dim=y, n=2)
    curv_z = da.diff(dim=z, n=2)

    if curv_x.values.any() == 0:
        check = False
        message = 'PROBLEM: contiguous values along x axis'
        return check, message

#    if curv_y.values.any() == 0:
#        check = False
#        message = 'PROBLEM: contiguous values along y axis'
#        return check, message
#
#    if curv_z.values.any() == 0:
#        check = False
#        message = 'PROBLEM: contiguous values along z axis'
#        return check, message
    # normal case
    return check, message


def check_stats(da, x='lon', y='lat', z='lev', time='time', tolerance=0.1):
    """ check statistics of variable """
    check = True
    message = ''
    yearly = da.groupby(da.time.dt.year)
    yearly_mean = yearly.mean(dim=[x, y, time])
    yearly_std = yearly.mean(dim=time).std(dim=y).mean(dim=[x])
    for year in yearly_mean.year:
        if yearly_mean.sel(year=year).any() == 0.:
            check = False
            message = f'PROBLEM: found zero in mean for year {year}'
        if yearly_std.sel(year=year).any() == 0.:
            check = False
            message = f'PROBLEM: found zero in std deviation for year {year}'
        if not np.allclose(yearly_mean.sel(year=year),
                           yearly_mean.isel(year=0),
                           rtol=tolerance):
            check = False
            message = f'PROBLEM: statistics on yearly means is not within' + \
                      f'expected tolerance\n'
        if not np.allclose(yearly_std.sel(year=year),
                           yearly_std.isel(year=0),
                           rtol=tolerance):
            check = False
            message = f'PROBLEM: statistics on yearly std deviation is ' + \
                      f'not within expected tolerance\n'

    filename_mean = f'QC_mean_{da.name}_{da[x].size}x{da[y].size}_{da[time].values[0]}.nc'
    filename_std = f'QC_std_{da.name}_{da[x].size}x{da[y].size}_{da[time].values[0]}.nc'
    filename_mean = filename_mean.replace(' ','_')
    filename_std = filename_std.replace(' ','_')
    yearly_mean.to_netcdf(filename_mean, unlimited_dims='year')
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
