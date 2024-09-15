import openeo
import datetime
import os
from info import get_all_updates, create_bounding_box


SATELLITE_DATA_DIR = "satellite_data"

def download_sat_data(dt: datetime.datetime, bb: list[float], band: str):
    connection = openeo.connect("https://openeo.dataspace.copernicus.eu/openeo/1.2")
    connection.authenticate_oidc()

    startdate_str = dt
    enddate_str = dt + datetime.timedelta(days=1)
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
    output_folder = os.path.join("output", "output_" + dt.strftime("%Y-%m-%d-%H-%M") + "_" + band)
    job.get_results().download_files(output_folder)


def update_sat_data(positions: list[tuple[float, float]], band: str):
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

    diff_to_now = (datetime.datetime.now() - latest_date).days


    updates_all = {}

    for i in range(diff_to_now):
        from_date += datetime.timedelta(days=1)
        updates = get_all_updates(positions, from_date, width=10)

        for pos in positions:
            if pos not in updates_all:
                updates_all[pos] = []
            updates_all[pos].extend(updates[pos])

            updates_all[pos] = list(set(updates_all[pos]))
            updates_all[pos].sort()

    for pos in positions:
        bb = create_bounding_box(pos[0], pos[1], 10)
        for dtime in updates_all[pos]:
            download_sat_data(dtime, bb, band)
    

        

if __name__ == "__main__":
    positions =  [(50.087,  14.424)]
    band = "CO"
    
    update_sat_data(positions, band)
