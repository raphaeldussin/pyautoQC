import xarray as xr
import pandas as pd
import numpy as np

# TEST DATASETS
lon1 = np.arange(0, 360)
lat1 = np.arange(-90, 90)
z = np.arange(15)
lon, lat = np.meshgrid(lon1, lat1)
temp = 20 * np.cos(np.pi * lat / 180) * np.ones((24, 15,) + lon.shape)
for k in np.arange(15):
    temp[:, k, :, :] = temp[:, k, :, :] * np.exp(-k/15)
temp_m = np.ma.masked_less(temp, 8)
temp_m_rand = temp_m + np.random.rand(24, 15, 180, 360)


# REFERENCE
ds_ref = xr.Dataset({'temperature': (['time', 'z', 'y', 'x'], temp_m_rand)},
                    coords={'lon': (['y', 'x'], lon),
                            'lat': (['y', 'x'], lat),
                            'z': (['z'], z),
                            'time': pd.date_range(start='1900-1-1',
                                                  periods=24, freq='1M')})

# BAD TIME AXIS
ds_test01 = xr.Dataset({'temperature': (['time', 'z', 'y', 'x'], temp_m_rand)},
                       coords={'lon': (['y', 'x'], lon),
                               'lat': (['y', 'x'], lat),
                               'z': (['z'], z),
                               'time': pd.date_range(start='1900-1-1',
                                                     periods=24, freq='1M')})
ds_test01['time'].values[12:] = 0.

ds_test02 = xr.Dataset({'temperature': (['time', 'z', 'y', 'x'], temp_m_rand)},
                       coords={'lon': (['y', 'x'], lon),
                               'lat': (['y', 'x'], lat),
                               'z': (['z'], z),
                               'time': pd.date_range(start='1900-1-1',
                                                     periods=24, freq='2M')})

# REPEATED VALUES ON X AXIS
ds_test03 = xr.Dataset({'temperature': (['time', 'z', 'y', 'x'], temp_m)},
                       coords={'lon': (['y', 'x'], lon),
                               'lat': (['y', 'x'], lat),
                               'z': (['z'], z),
                               'time': pd.date_range(start='1900-1-1',
                                                     periods=24, freq='1M')})


def test_check_timeaxis():
    from pyautoQC.dataQC import check_timeaxis

    check, message = check_timeaxis(ds_ref)
    assert check
    assert message == ''

    check, message = check_timeaxis(ds_test01)
    assert not check
    assert message != ''

    check, message = check_timeaxis(ds_test02)
    assert not check
    assert message != ''


def test_check_masksize():
    from pyautoQC.dataQC import check_masksize

    check, message = check_masksize(ds_ref['temperature'], x='x', y='y', z='z')
    assert check
    assert message == ''


def test_check_second_derivative():
    from pyautoQC.dataQC import check_second_derivative

    check, message = check_second_derivative(ds_ref['temperature'],
                                             x='x', y='y', z='z')
    assert check
    assert message == ''

    check, message = check_second_derivative(ds_test03['temperature'],
                                             x='x', y='y', z='z')
    assert not check
    assert message != ''
