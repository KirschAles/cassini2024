import rasterio
from rasterio.plot import show
import numpy as np


def open_with_rasterio(file_path):
    img = rasterio.open(file_path)

    print(img.count)
    print(img.bounds)
    print(img.height)
    print(img.width)
    print(img.crs)

    arr = img.read(1)
    print(arr.shape)
    print(arr)
    show(img)


from osgeo import gdal
def open_with_gdal():
    pass


if __name__ == "__main__":
    import os
    folder = "output"
    for file in os.listdir(folder):
        if file.endswith(".tif"):
            file_path = os.path.join(folder, file)
            open_with_rasterio(file_path)