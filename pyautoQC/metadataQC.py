import xarray as xr
import numpy as np


def compare_dict(mydict, dict_ref, keyname='key'):
    ''' compare two dictionaries and print differences, if found'''
    check = True
    message = ''
    # first compare that number of keys is the same
    nkeys_ref = len(dict_ref.keys())
    nkeys_cur = len(mydict.keys())
    if nkeys_cur != nkeys_ref:
        check = False
        message = f'PROBLEM: number of {keyname}s differs between ' + \
                  f'reference ({nkeys_ref}) and current ({nkeys_cur})\n'
        return check, message
    # check consistency for name of keys
    list_keys_cur = sorted(list(mydict.keys()))
    list_keys_ref = sorted(list(dict_ref.keys()))
    if list_keys_cur != list_keys_ref:
        check = False
        message = f'PROBLEM list of {keyname} are different between ' + \
                  f'reference ({list_keys_ref}) and current ' + \
                  f'({list_keys_cur})\n'
        return check, message
    # second compare that the values are the same for each key
    for key in mydict.keys():
        if type(mydict[key]) == xr.core.dataarray.DataArray:
            pass
        elif mydict[key] != dict_ref[key]:
            check = False
            message += f'PROBLEM: {keyname} {key} differs between ' + \
                       f'reference ({dict_ref[key]}) and current ' + \
                       f'({mydict[key]})\n'
    return check, message


def compare_dataset_dims(myds, ds_ref):
    ''' check consistency of dimensions '''
    mydict = dict(myds.dims)
    dict_ref = dict(ds_ref.dims)
    check, message = compare_dict(mydict, dict_ref, keyname='dimension')
    return check, message


def compare_dataset_coords(myds, ds_ref):
    ''' check consistency of coords '''
    coords_ref = dict(myds.coords)
    coords_cur = dict(ds_ref.coords)
    # test number of coordinates
    check, message = compare_dict(coords_cur, coords_ref, keyname='coordinate')
    if not check:
        return check, message
    # remove time, in any
    listcoords_cur = list(myds.coords)
    if 'time' in listcoords_cur:
        listcoords_cur.remove('time')
    # test the values of each coordinate
    for coord in listcoords_cur:
        if not np.array_equal(myds[coord].values, ds_ref[coord].values):
            check = False
            message += f'PROBLEM: Coordinates values for {coord} differ ' + \
                       f'between datasets\n'
    return check, message
