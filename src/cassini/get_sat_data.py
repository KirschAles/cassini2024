import openeo
import datetime


def download_sat_data(dt: datetime.datetime, bb: list[float], band: str):
    connection = openeo.connect("https://openeo.dataspace.copernicus.eu/openeo/1.2")
    connection.authenticate_oidc()

    startdate_str = dt - datetime.timedelta(days=1)
    enddate_str = dt + datetime.timedelta(days=1)
    startdate_str = startdate_str.strftime("%Y-%m-%d")
    enddate_str = enddate_str.strftime("%Y-%m-%d")
    temporal_extent = [startdate_str, enddate_str]
    west = bb[0][0]
    south = bb[0][1]
    east = bb[1][0]
    north = bb[1][1]
    cube = connection.load_collection("SENTINEL_5P_L2",
                                  spatial_extent={"west": west, "south": south, "east": east, "north": north},
                                  temporal_extent=temporal_extent,
                                  bands=[band])
    
    result = cube.save_result("GTiff")
    job  = result.create_job()
    job.start_and_wait()
    job.get_results().download_files("output")


if __name__ == "__main__":
    download_sat_data(datetime.datetime(2024, 9, 1), [[14.23, 49.93], [14.65, 50.25]], "CO")