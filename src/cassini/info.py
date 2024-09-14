import requests
import json
from typing import Any
from shapely import Polygon
import math
import datetime
import pandas

CATALOGUE = "https://catalogue.dataspace.copernicus.eu/stac"

LATID_CHANGE = 1/110.574

def long_change(latitude: float) -> float:
    return 1 / 111.320 / math.cos(math.radians(latitude))
def create_bounding_box(latitude, longitude, width) -> tuple[tuple[float, float]]:
    half = width / 2.0
    delta_latitude = half * LATID_CHANGE
    delta_longitude = half * long_change(latitude)

    return [(latitude + delta_latitude, longitude - delta_longitude),
            (latitude + delta_latitude, longitude + delta_longitude),
            (latitude - delta_latitude, longitude + delta_longitude),
            (latitude - delta_latitude, longitude - delta_longitude)]

def list_collections() -> list[str]:
    collection_info = json.loads(requests.get(f"{CATALOGUE}/collections").content)
    return [x['id'] for x in collection_info['collections']]

def get_collection(collection_id: str) -> dict[str, Any]:
    info = json.loads(requests.get(f"{CATALOGUE}/collections/{collection_id}").content)
    return info

def list_items(collection_id: str, bbox = None, datetime_from=None) -> list:
    addition = ''
    if bbox:
        flattened = [x for xs in bbox for x in xs]
        flattened = [str(x) for x in flattened]
        new_part = ','.join(flattened)
        new_part = 'bbox=' + new_part + '&'
        addition += new_part
    if datetime_from is not None:
        time_str = f"{datetime_from.isoformat()}/"
        new_part = f"datetime={time_str}&"
        addition += new_part
    string = f"{CATALOGUE}/collections/{collection_id}/items?{addition}limit=50&sortby=+datetime"
    info = json.loads(requests.get(string).content)
    return info['features']

def contains_bbox(bbox, geometry):
    bbox = Polygon(bbox)
    geometry = Polygon(geometry)
    return geometry.contains(bbox)

def not_too_long(x):
    start = x['properties']['start_datetime']
    end = x['properties']['end_datetime']
    start = datetime.datetime.fromisoformat(start)
    end = datetime.datetime.fromisoformat(end)
    return end - start < datetime.timedelta(hours=1)

def get_new_updates(latitude: float,
                    longitude: float,
                    time_from: datetime.datetime,
                    collection: str = "SENTINEL-5P",
                    width: float | int = 10):
    box = create_bounding_box(latitude, longitude, width)
    items = list_items(collection, bbox=[box[0], box[2]], datetime_from=time_from)
    items = [x for x in items if not_too_long(x)]
    [x for x in items if contains_bbox(box, x['geometry']['coordinates'][0])]
    datetimes = pd.DataFrame(data={'datetime': [datetime.datetime.fromisoformat(x['properties']['datetime']) for x in items]})
    datetimes['date'] = datetimes['datetime'].dt.date
    return list(datetimes.groupby(by=['date']).mean()['datetime'])

def get_all_updates(positions: list[tuple], time_from: datetime.datetime, collection: str = "SENTINEL-5P", width: float = 10) -> dict[tuple, list[datetime.datetime]]:
    all_updates = {}
    for position in positions:
        new_updates = get_new_updates(
            position[0],
            position[1],
            time_from,
            collection,
            width
        )
        if len(new_updates):
            all_updates[position] = new_updates
    return all_updates