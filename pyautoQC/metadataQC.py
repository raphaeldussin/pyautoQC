import xarray as xr
import numpy as np


def compare_dict(mydict, dict_ref):
    ''' compare two dictionaries and print differences, if found'''
    # first compare that number of keys is the same
    nkeys_ref = len(dict_ref.keys())
    nkeys_cur = len(mydict.keys())
    if nkeys_cur != nkeys_ref:
        raise ValueError("PROBLEM: number of keys differs between reference (%g) and current (%g)" %
                         (nkeys_ref, nkeys_cur))
    # second compare that the values are the same for each key
    for key in mydict.keys():
        if mydict[key] != dict_ref[key]:
            raise ValueError("PROBLEM: key %s differs between reference (%s) and current (%s)" %
                             (key, dict_ref[key], mydict[key]))
    return None


# Since we're raising exceptions, we need to make one function per test

def compare_dataset_dims(myds, ds_ref):
    ''' check consistency of dimensions '''
    if myds.dims != ds_ref.dims:
        raise ValueError("Dimensions are inconsistent between datasets")
    return None


def compare_dataset_coords(myds, ds_ref):
    ''' check consistency of coords '''
    listcoords_ref = list(myds.coords)
    listcoords_cur = list(ds_ref.coords)
    # test number of coordinates
    if listcoords_ref != listcoords_cur:
        raise ValueError("Coordinates list are inconsistent")
    # remove time, in any
    if 'time' in listcoords_cur:
        listcoords_cur.remove('time')
    # test the values of each coordinate
    for coord in listcoords_cur:
        if not np.array_equal(myds[coord].values, ds_ref[coord].values):
            raise ValueError("Coordinates values for %s differ between datasets" % coord)
    return None
