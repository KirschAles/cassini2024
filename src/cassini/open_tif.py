import rasterio
from rasterio.plot import show
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


def open_with_rasterio(file_path):
    img = rasterio.open(file_path)
    arr = img.read()
    # show(img)

    return arr[0][1,1]

def get_time_series(folder: str, band: str):
    t = []
    val = []
    subdirs_band = [subdir for subdir in os.listdir(folder) if subdir.split("_")[2] == band]
    for dir in sorted(subdirs_band):
        date = dir.split("_")[1]
        if t:
            current = t[-1]
            while datetime.strptime(current, "%Y-%m-%d-%H-%M") < datetime.strptime(date, "%Y-%m-%d-%H-%M"):
                current = datetime.strptime(current, "%Y-%m-%d-%H-%M") + timedelta(hours=1)
                current = current.strftime("%Y-%m-%d-%H-%M")
                t.append(current)
                val.append(val[-1])
        t.append(date)

        for file in os.listdir(os.path.join(folder, dir)):
            if file.endswith(".tif"):
                file_path = os.path.join(folder, dir, file)
                co_center = open_with_rasterio(file_path)
                val.append(co_center)
    return t, val

def plot_time_series(t, val):
    plt.figure(figsize=(12, 6))
    plt.plot(t, val)
    ax=plt.gca()
    loc = ticker.MultipleLocator(base=26)
    ax.xaxis.set_major_locator(loc)
    plt.xlabel("Time")
    plt.xticks(rotation=25)
    plt.ylabel("CO Level")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    folder = "output"
    band = "CO"
    t, co_val = get_time_series(folder, band)
    plot_time_series(t, co_val)
