from raster_tools import Raster

def create_raster(file):
    rs = Raster(file)
    return rs
def add_to_raster(raster, file):
    raster.add(file)
    return raster

