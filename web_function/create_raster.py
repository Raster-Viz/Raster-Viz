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
    raster.add(file)
    return raster


if __name__ == "__main__":
    raster = create_raster("web_function/data/elevation.tif")
    raster = add_to_raster(raster, "web_function/data/elevation2.tif")
    print((raster._rs))
    arr = raster._to_presentable_xarray()
    arr.plot()
    plot = plt.gcf()

