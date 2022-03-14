from raster_tools import Raster
from xarray import DataArray
from dask import array
import matplotlib.pyplot as plt
import io
import urllib, base64

def create_raster(file):
    rs = Raster(file)
    return rs


def add_to_raster(raster, file):
    rs = Raster(file)
    fs = raster.add(rs)
    return fs


if __name__ == "__main__":
    raster = create_raster("web_function/data/pods0_like_elevation.tif")
    raster = add_to_raster(raster, "web_function/data/elevation2.tif")
    print((raster._rs[0].min().values.item()))
