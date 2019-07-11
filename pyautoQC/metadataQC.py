import xarray as xr
import numpy as np


def compare_dict(mydict, dict_ref, keyname='key'):
    ''' compare two dictionaries and print differences, if found'''
    # first compare that number of keys is the same
    nkeys_ref = len(dict_ref.keys())
    nkeys_cur = len(mydict.keys())
    if nkeys_cur != nkeys_ref:
        raise ValueError("PROBLEM: number of %ss differs between reference (%g) and current (%g)" %
                         (keyname, nkeys_ref, nkeys_cur))
    # check consistency for name of keys
    list_keys_cur = sorted(list(mydict.keys()))
    list_keys_ref = sorted(list(dict_ref.keys()))
    if list_keys_cur != list_keys_ref:
        raise ValueError("PROBLEM list of %s are different between reference (%s) and current (%s)" %
                         (keyname, list_keys_ref, list_keys_cur))
    # second compare that the values are the same for each key
    for key in mydict.keys():
        if type(mydict[key]) == xr.core.dataarray.DataArray:
            pass
        elif mydict[key] != dict_ref[key]:
            raise ValueError("PROBLEM: %s %s differs between reference (%s) and current (%s)" %
                             (keyname, key, dict_ref[key], mydict[key]))
    return None


# Since we're raising exceptions, we need to make one function per test

def compare_dataset_dims(myds, ds_ref):
    ''' check consistency of dimensions '''
    mydict = dict(myds.dims)
    dict_ref = dict(ds_ref.dims)
    compare_dict(mydict, dict_ref, keyname='dimension')
    return None


def compare_dataset_coords(myds, ds_ref):
    ''' check consistency of coords '''
    coords_ref = dict(myds.coords)
    coords_cur = dict(ds_ref.coords)
    # test number of coordinates
    compare_dict(coords_cur, coords_ref, keyname='coordinate')
    # remove time, in any
    listcoords_cur = list(myds.coords)
    if 'time' in listcoords_cur:
        listcoords_cur.remove('time')
    # test the values of each coordinate
    for coord in listcoords_cur:
        if not np.array_equal(myds[coord].values, ds_ref[coord].values):
            raise ValueError("Coordinates values for %s differ between datasets" % coord)
    return None
