import requests

response = requests.post('https://creodias.sentinel-hub.com/api/v1/process',
  headers={"Authorization" : "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJ3dE9hV1o2aFJJeUowbGlsYXctcWd4NzlUdm1hX3ZKZlNuMW1WNm5HX0tVIn0.eyJleHAiOjE3MjYzMTQ0NDQsImlhdCI6MTcyNjMxMDg0NCwianRpIjoiNTYzZDE2YjEtMzViOS00MzliLWJkOTktZjFjYmZkYzUzMDI0IiwiaXNzIjoiaHR0cHM6Ly9zZXJ2aWNlcy5zZW50aW5lbC1odWIuY29tL2F1dGgvcmVhbG1zL21haW4iLCJzdWIiOiI0Zjc2M2NkZi0yNDdmLTQ5OTctOWE1ZC1jOGIxMmRiNDA4ODMiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJkMWY1N2M4MS04NmU3LTRiNzgtYTNkNC00MGIzYjk5ZTE4MTYiLCJzY29wZSI6ImVtYWlsIHByb2ZpbGUiLCJjbGllbnRIb3N0IjoiMTkzLjE0Mi4yMDMuMTg3IiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJzZXJ2aWNlLWFjY291bnQtZDFmNTdjODEtODZlNy00Yjc4LWEzZDQtNDBiM2I5OWUxODE2IiwiY2xpZW50QWRkcmVzcyI6IjE5My4xNDIuMjAzLjE4NyIsImNsaWVudF9pZCI6ImQxZjU3YzgxLTg2ZTctNGI3OC1hM2Q0LTQwYjNiOTllMTgxNiIsImFjY291bnQiOiI5MDk2MDFlYy04YTY2LTRjZTgtOWRmOC1jZGY4OTQyYTQxNGEifQ.O6LHjLWVe4vHkOYc4L13AFqZMGKhRicjPOR2adlxWsSM7B-dQkSwww-LVX2aERbDOnZ8SgznnlQgSOtQJ0Wh4MtUNvYozLsTL-JFdmQbxU9L5EL-yXyrwHjnq9-SVp7tpdqgVEqE4TGAXXqmB8tyXVhvDwgnaf8Chp9_KfFwVNFYLJ0OZuvq3gPrS2cio931BiBl9LQf0N05WqKKVPK-FHG198ib66VGo7RHgSzfbdib5OLvvsTDlsMFAgCLUjjKaH3BGl4KIlx5coj-5cyOlzAoT1I0huMn0KyQJ4jCui1zoJnKYSpLeWE1lwIzl99bAblJxV8k5T6vtHvw9cRLKQ"},
  json={
    "input": {
        "bounds": {
            "bbox": [
                14.23,
                49.93,
                14.65,
                50.25
            ]
        },
        "data": [{
            "type": "sentinel-5p-l2",
            "dataFilter": {
                    "timeRange": {
                        "from": "2024-09-01T00:00:00Z",
                        "to": "2024-09-13T00:00:00Z"
                    }
            }
        }]
    },
    "output": {
        "width": 512,
        "height": 512
    },
    "evalscript": """
    //VERSION=3

    function setup() {
      return {
        input: ["CO"],
        output: {
          bands: 1
        }
      };
    }

    function evaluatePixel(
      sample,
      scenes,
      inputMetadata,
      customData,
      outputMetadata
    ) {
      return [sample.CO];
    }
    """
})

print(response.url)


import matplotlib.pyplot as plt
import matplotlib.dates as md
import datetime

from src.cassini.get_IOT_data import get_IOT_data as iot_time_series


def visualize_IOT_data():
    time_coarse, time_fine, temperature, humidity, pressure, rainfall = iot_time_series()

    dates_fine = [datetime.datetime.fromtimestamp(ts) for ts in time_fine]
    dates_fine = md.date2num(dates_fine)
    dates_coarse = [datetime.datetime.fromtimestamp(ts) for ts in time_coarse]
    dates_coarse = md.date2num(dates_coarse)

    plt.figure(figsize=(12, 6))
    plt.subplot(2, 2, 1)
    plt.xticks( rotation=25 )
    ax=plt.gca()
    xfmt = md.DateFormatter('%Y-%m-%d %H:%M:%S')
    ax.xaxis.set_major_formatter(xfmt)
    plt.plot(dates_coarse, temperature, label='Temperature')
    plt.ylabel("Temperature [°C]")
    plt.xlabel("Time")
    plt.title("Temperature")
    plt.subplot(2, 2, 2)
    plt.xticks( rotation=25 )
    ax=plt.gca()
    xfmt = md.DateFormatter('%Y-%m-%d %H:%M:%S')
    ax.xaxis.set_major_formatter(xfmt)
    plt.plot(dates_fine, humidity, label='Humidity')
    plt.title("Humidity")
    plt.subplot(2, 2, 3)
    plt.xticks( rotation=25 )
    ax=plt.gca()
    xfmt = md.DateFormatter('%Y-%m-%d %H:%M:%S')
    ax.xaxis.set_major_formatter(xfmt)
    plt.plot(dates_fine, pressure, label='Pressure')
    plt.ylabel("Pressure [hPa]")
    plt.xlabel("Time")
    plt.title("Pressure")
    plt.subplot(2, 2, 4)
    plt.xticks( rotation=25 )
    ax=plt.gca()
    xfmt = md.DateFormatter('%Y-%m-%d %H:%M:%S')
    ax.xaxis.set_major_formatter(xfmt)
    plt.plot(dates_fine, rainfall, label='Rainfall')
    plt.ylabel("Rainfall [mm]")
    plt.xlabel("Time")
    plt.title("Rainfall")
    plt.tight_layout()

    plt.show()