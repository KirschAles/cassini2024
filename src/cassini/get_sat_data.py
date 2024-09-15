import openeo
import datetime
import os
import rasterio
from rasterio.plot import show

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from src.cassini.info import get_all_updates, create_bounding_box


SATELLITE_DATA_DIR = "satellite_data"

def download_sat_data(dt: datetime.datetime, bb: list[float], band: str):
    print("Downloading satellite data for band", band, "at", dt)
    connection = openeo.connect("https://openeo.dataspace.copernicus.eu/openeo/1.2")
    connection.authenticate_oidc()

    startdate_str = dt - datetime.timedelta(hours=1)
    enddate_str = startdate_str + datetime.timedelta(days=1)
    startdate_str = startdate_str.strftime("%Y-%m-%d")
    enddate_str = enddate_str.strftime("%Y-%m-%d")
    temporal_extent = [startdate_str, enddate_str]
    west = bb[0][1]
    south = bb[2][0]
    east = bb[2][1]
    north = bb[0][0]
    cube = connection.load_collection("SENTINEL_5P_L2",
                                  spatial_extent={"west": west, "south": south, "east": east, "north": north},
                                  temporal_extent=temporal_extent,
                                  bands=[band])
    
    result = cube.save_result("GTiff")
    job  = result.create_job()
    job.start_and_wait()
    output_folder = os.path.join(SATELLITE_DATA_DIR, "output_" + dt.strftime("%Y-%m-%d-%H-%M") + "_" + band)
    job.get_results().download_files(output_folder)


def update_sat_data(positions: list[tuple[float, float]], band: str):
    print("Updating satellite data for band", band)
    if not os.path.exists(SATELLITE_DATA_DIR):
        os.makedirs(SATELLITE_DATA_DIR)

    subdirs = sorted(os.listdir(SATELLITE_DATA_DIR))
    subdirs_band = [subdir for subdir in subdirs if subdir.split("_")[2] == band]
    if len(subdirs_band) == 0:
        from_date = datetime.datetime.now() - datetime.timedelta(days=7)
    else:
        latest_date_str = subdirs_band[-1].split("_")[1]
        latest_date = datetime.datetime.strptime(latest_date_str, "%Y-%m-%d-%H-%M")

        from_date = latest_date

    diff_to_now = (datetime.datetime.now() - from_date).days


    updates_all = {}

    for i in range(diff_to_now):
        updates = get_all_updates(positions, from_date, width=10)

        for pos in positions:
            if pos not in updates_all:
                updates_all[pos] = []
            updates_all[pos].extend(updates[pos])

            updates_all[pos] = list(set(updates_all[pos]))
            updates_all[pos].sort()

        from_date += datetime.timedelta(days=1)

    for pos in positions:
        bb = create_bounding_box(pos[0], pos[1], 10)
        for dtime in updates_all[pos]:
            if datetime.datetime.now() - dtime < datetime.timedelta(days=1):
                continue
            download_sat_data(dtime, bb, band)


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
            while datetime.datetime.strptime(current, "%Y-%m-%d-%H-%M") < datetime.datetime.strptime(date, "%Y-%m-%d-%H-%M"):
                current = datetime.datetime.strptime(current, "%Y-%m-%d-%H-%M") + datetime.timedelta(hours=1)
                current = current.strftime("%Y-%m-%d-%H-%M")
                t.append(current)
                val.append(val[-1])
        t.append(date)

        for file in os.listdir(os.path.join(folder, dir)):
            if file.endswith(".tif"):
                file_path = os.path.join(folder, dir, file)
                co_center = open_with_rasterio(file_path)
                val.append(abs(co_center))
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
    # positions =  [(50.087,  14.424)]
    # bands = ["CO", "NO2", "O3", "SO2"]

    # for band in bands:
    #     update_sat_data(positions, band)

    t,  val = get_time_series(SATELLITE_DATA_DIR, "SO2")
    plot_time_series(t, [abs(v) for v in val])
