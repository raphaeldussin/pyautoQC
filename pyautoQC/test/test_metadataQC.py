import pytest
import xarray as xr
import pandas as pd
import numpy as np

# TEST DATASETS
lon1 = np.arange(0, 360)
lat1 = np.arange(-90, 90)
lon, lat = np.meshgrid(lon1, lat1)
temp = 20 * np.ones((1,) + lon.shape)
temp2 = 20 * np.ones(lon.shape)

# REFERENCE
ds_ref = xr.Dataset({'temperature': (['time', 'y', 'x'], temp)},
                    coords={'lon': (['y', 'x'], lon),
                            'lat': (['y', 'x'], lat),
                            'time': (['time'], [pd.Timestamp('1900-1-1')])})

# CHANGE DIMS
ds_d00 = xr.Dataset({'temperature': (['y', 'x'], temp2)},
                    coords={'lon': (['y', 'x'], lon),
                            'lat': (['y', 'x'], lat)})

# CHANGE DATA
ds_d01 = xr.Dataset({'temperature': (['time', 'y', 'x'], 1 + temp)},
                    coords={'lon': (['y', 'x'], lon),
                            'lat': (['y', 'x'], lat),
                            'time': (['time'], [pd.Timestamp('1900-1-1')])})

# CHANGE LON
ds_d02 = xr.Dataset({'temperature': (['time', 'y', 'x'], temp)},
                    coords={'lon': (['y', 'x'], lon - 180),
                            'lat': (['y', 'x'], lat),
                            'time': (['time'], [pd.Timestamp('1900-1-1')])})

# CHANGE TIME
ds_d03 = xr.Dataset({'temperature': (['time', 'y', 'x'], temp)},
                    coords={'lon': (['y', 'x'], lon),
                            'lat': (['y', 'x'], lat),
                            'time': (['time'], [pd.Timestamp('1901-1-1')])})


def test_compare_dict():
    from pyautoQC.metadataQC import compare_dict

    dict_a = {'title': 'run1', 'history': 'created on 01/01/2001'}
    dict_b = {'title': 'run1', 'history': 'created on 01/01/2001'}
    dict_c = {'title': 'run2', 'history': 'created on 01/01/2001'}
    dict_d = {'title': 'run1'}

    # test two identical dict does not return error
    compare_dict(dict_a, dict_b)
    # test two different dict return error
    with pytest.raises(ValueError):
        compare_dict(dict_a, dict_c)
    # test different number of keys return error
    with pytest.raises(ValueError):
        compare_dict(dict_a, dict_d)
    return None


def test_compare_dataset_dims():
    from pyautoQC.metadataQC import compare_dataset_dims

    # changing data should not trigger problem
    compare_dataset_dims(ds_d01, ds_ref)
    # changing dimensions should trigger problem
    with pytest.raises(ValueError):
        compare_dataset_dims(ds_d00, ds_ref)
