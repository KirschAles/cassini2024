import openeo
import datetime
import os
from info import get_all_updates, create_bounding_box


def download_sat_data(dt: datetime.datetime, bb: list[float], band: str):
    connection = openeo.connect("https://openeo.dataspace.copernicus.eu/openeo/1.2")
    connection.authenticate_oidc()

    startdate_str = dt # - datetime.timedelta(days=1)
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


if __name__ == "__main__":
    positions =  [(50.087,  14.424)]
    from_now = datetime.datetime.now()

    updates_all = {}
    ts_all = []
    for i in range(1, 8):
        from_date = from_now - datetime.timedelta(days=i)
        updates = get_all_updates(positions, from_date, width=10)
        
        for pos in positions:
            if pos not in updates_all:
                updates_all[pos] = []
            updates_all[pos].extend(updates[pos])

            updates_all[pos] = list(set(updates_all[pos]))
            updates_all[pos].sort()

    BAND = "CO"
    for pos in positions:
        bb = create_bounding_box(pos[0], pos[1], 10)
        for dt in updates_all[pos]:
            download_sat_data(dt, bb, BAND)
