import os
from datetime import datetime
import pytz
import rasterio as rio
import xarray
from pyproj import CRS
import numpy as np
from rasterio.warp import calculate_default_transform, reproject, Resampling
import rasterio.crs


def sample_similarity(a1, a2, size):
    a1 = a1[a1.shape[0]//2:a1.shape[0]//2+size,a1.shape[1]//2:a1.shape[1]//2+size]
    a2 = a2[a2.shape[0]//2:a2.shape[0]//2+size,a2.shape[1]//2:a2.shape[1]//2+size]

    print('Array Shapes:')
    print(a1.shape)
    print(a2.shape)

    # one way
    # print((a1==a2).all())

    equal = np.array_equal(a1, a2)

    return equal


def band_reproject(out_file, band, src_profile, dst_profile, tags):
    with rio.open(out_file, 'w', **dst_profile) as out:

        reproject(
            source=band,
            destination=rasterio.band(out, 1),
            src_transform=src_profile['transform'],
            src_crs=src_profile['crs'],
            dst_transform=dst_profile['transform'],
            dst_crs=dst_profile['crs'],
            resampling=Resampling.nearest
        )

        factors = [2, 4, 8]
        out.build_overviews(factors, Resampling.nearest)
        out.update_tags(ns='rio_overview', resampling='nearest')
        out.update_tags(**tags)


def compare(nc_file, variable):
    with rio.open('netcdf:{}:{}'.format(nc_file, variable)) as nc:
        r = nc.read(1)

    with xarray.open_dataset(nc_file, decode_coords="all") as xds:

        if 'height_above_ground' in xds.dims:
            print('Removing unneeded dimension to maintain consistent shape')
            print('Before Dims: {}'.format(xds.dims))
            xds = xds.squeeze('height_above_ground')
            print('After Dims: {}'.format(xds.dims))

        da = xds[variable]
        x = da[0].to_numpy()

    raw = sample_similarity(r, x, 300)
    print('Equal as is: {}'.format(raw))
    flipped = sample_similarity(r, np.flip(x, 0), 300)
    print('Equal flipped: {}'.format(flipped))


def process(nc_file, variable, out_path):

    with rio.open('netcdf:{}:{}'.format(nc_file, variable)) as nc:
        dst_profile = nc.meta.copy()
        src_profile = nc.meta.copy()
        src_profile['bounds'] = nc.bounds

    with xarray.open_dataset(nc_file, decode_coords="all") as xds:

        if 'height_above_ground' in xds.dims:
            print('Removing unneeded dimension to maintain consistent shape')
            print('Before Dims: {}'.format(xds.dims))
            xds = xds.squeeze('height_above_ground')
            print('After Dims: {}'.format(xds.dims))

        da = xds[variable]

    # Redefine source CRS with KM units
    src_proj_str = '+proj=lcc +lat_1=25 +lat_0=25 +lon_0=-95 +k_0=1 +x_0=0 ' \
                   '+y_0=0 +R=6371200 +units=km +no_defs'
    src_crs = CRS.from_proj4(src_proj_str)
    src_profile['crs'] = rasterio.crs.CRS.from_user_input(src_crs)

    # Compile destination information
    dst_crs = 'EPSG:4326'

    transform, width, height = calculate_default_transform(
        src_profile['crs'], dst_crs, src_profile['width'],
        src_profile['height'], *src_profile['bounds'])

    print(transform)

    dst_profile.update(
        count=1,
        compress='LZW',
        driver='GTiff',
        interleave='pixel',
        tiled=True,
        blockxsize=256,
        blockysize=256,
        crs=dst_crs,
        transform=transform,
        width=width,
        height=height
    )

    times = da['time']
    # reftime = datetime.fromtimestamp(da['reftime'].item(0) // 1000000000, tz=pytz.UTC)

    validate_out_path(out_path)

    for i in range(len(da['time'])):
        print('Band {}'.format(str(i)))
        time = datetime.fromtimestamp(times.item(i) // 1000000000, tz=pytz.UTC)
        print(time.strftime("%Y%m%d-%H%M"))
        band = np.flip(da[i].to_numpy(), 0)
        file_name = '{}{}.tif'.format(out_path, time.strftime("%Y%m%d-%H%M"))
        band_reproject(file_name, band, src_profile, dst_profile, da.attrs)


def validate_out_path(out_path):

    path_exists = os.path.exists(out_path)

    if not path_exists:
        os.makedirs(out_path)


def describe(nc_file, variable):

    with rio.open('netcdf:{}:{}'.format(nc_file, variable)) as nc:

        print('RASTERIO METADATA')
        print('Dataset')
        print(nc)
        print('Profile')
        print(nc.profile)
        print('Tags')
        print(nc.tags())
        print('Bounds')
        print(nc.bounds)
        print('Transform')
        print(nc.transform)
        print('Shape')
        print(nc.shape)
        print('CRS')
        print(nc.crs)

    with xarray.open_dataset(nc_file, decode_coords="all") as xds:
        da = xds[variable]

        print('XARRAY METADATA')
        print('Dataarray')
        print(da)
        print('Dimensions')
        print(da.dims)
        print('Coordinates')
        print(da.coords)
        print('Attributes')
        print(da.attrs)
        print('CRS')
        print(da.rio.crs)