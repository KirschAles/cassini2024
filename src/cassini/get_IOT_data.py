import requests
import ast
import datetime
import json


def get_IOT_data():
    headers = {
        'accept': 'application/json',
        # 'Authorization': '8434951c-ad94-40a2-95b1-728187b5e9b5',
        'X-API-KEY': '8434951c-ad94-40a2-95b1-728187b5e9b5',
    }

    params = {
        'limit': '20',
    }

    response = requests.get(
        'https://api.prod.hardwario.cloud/v2/spaces/0191e6b6-186f-7402-b53d-a07ee799cba8/messages',
        params=params,
        headers=headers,
    )

    return response.json()

def get_time_series():
    data = get_IOT_data()
    time_coarse = []
    time_fine = []
    time_co2 = []
    temperature = []
    humidity = []
    pressure = []
    rainfall = []
    co2 = []

    for t, d in enumerate(data):
        # dtime_coarse = datetime.datetime.fromisoformat(d['created_at'][:19])
        # tstamp_coarse = datetime.datetime.timestamp(dtime_coarse)
        if d['type'] == 'data' and d['device_name'] == 'chester-meteo':
            try:
                dict_data = ast.literal_eval(d['body'])

            except Exception as e:
                # dict_data = eval(str(d['body']))
                print("HAYAAA")
                print(e)
                continue

            # time_coarse.append(tstamp_coarse)
            # print(dict_data['message'])
            time_coarse.append(dict_data['message']['timestamp'])
            temperature.append(dict_data['thermometer']['temperature'])

            num_measutements = len(dict_data['hygrometer']['humidity']['measurements'])
            for i in range(num_measutements):
                t_rain = dict_data['weather_station']['rainfall']['measurements'][i]['timestamp']
                t_pressure = dict_data['barometer']['pressure']['measurements'][i]['timestamp']
                t_humidity = dict_data['hygrometer']['humidity']['measurements'][i]['timestamp']
                assert t_rain == t_pressure == t_humidity, "Time stamps are not the same."
                time_fine.append(t_rain)

                rainfall.append(dict_data['weather_station']['rainfall']['measurements'][i]['value'])
                pressure.append(dict_data['barometer']['pressure']['measurements'][i]['avg'])
                humidity.append(dict_data['hygrometer']['humidity']['measurements'][i]['avg'])

        
        if d['type'] == 'data' and d['device_name'] == 'chester-clime-iaq':
            try:
                dict_data = json.loads(d['body'])
            except Exception as e:
                print("HAYAAAaaa")
                print(e)
                continue
        
            num_measurements = len(dict_data['iaq_sensor']['co2_conc']['measurements'])
            # print(dict_data['iaq_sensor']['co2_conc']['measurements'])
            for i in range(num_measurements):
                time_co2.append(dict_data['iaq_sensor']['co2_conc']['measurements'][i]['timestamp'])
                co2.append(dict_data['iaq_sensor']['co2_conc']['measurements'][i]['avg'])


    
    sorted_rainfall = [r for _, r in sorted(zip(time_fine, rainfall))]
    sorted_pressure = [p for _, p in sorted(zip(time_fine, pressure))]
    sorted_humidity = [h for _, h in sorted(zip(time_fine, humidity))]
    sorted_temperature = [t for _, t in sorted(zip(time_coarse, temperature))]
    sorted_time_coarse = sorted(time_coarse)
    sorted_time_fine = sorted(time_fine)
    sorted_co2 = [c for _, c in sorted(zip(time_co2, co2))]
    sorted_time_co2 = sorted(time_co2)

    return sorted_time_coarse, sorted_time_fine, sorted_time_co2, sorted_temperature, sorted_humidity, sorted_pressure, sorted_rainfall, sorted_co2


if __name__ == "__main__":
    time_coarse, time_fine, time_co2, temperature, humidity, pressure, rainfall, co2 = get_time_series()

    date_time_coarse = [datetime.datetime.fromtimestamp(t) for t in time_coarse][-1]
    date_time_fine = [datetime.datetime.fromtimestamp(t) for t in time_fine][-1]

    print(date_time_coarse)
    print(date_time_fine)