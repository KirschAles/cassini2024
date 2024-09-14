import requests
import ast
import datetime

import matplotlib.pyplot as plt
import matplotlib.dates as md

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots


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


def dashboard(data):
    time_coarse, time_fine, temperature, humidity, pressure, rainfall = get_time_series(data)

    dates_fine = [datetime.datetime.fromtimestamp(ts) for ts in time_fine]
    dates_coarse = [datetime.datetime.fromtimestamp(ts) for ts in time_coarse]

    fig = make_subplots(rows=2, cols=2, subplot_titles=("Temperature", "Humidity", "Pressure", "Rainfall"))

    fig.add_trace(go.Scatter(x=dates_coarse, y=temperature, name="Temperature"), row=1, col=1)
    fig.add_trace(go.Scatter(x=dates_fine, y=humidity, name="Humidity"), row=1, col=2)
    fig.add_trace(go.Scatter(x=dates_fine, y=pressure, name="Pressure"), row=2, col=1)
    fig.add_trace(go.Scatter(x=dates_fine, y=rainfall, name="Rainfall"), row=2, col=2)

    fig.update_xaxes(title_text="Time", row=2, col=1)
    fig.update_xaxes(title_text="Time", row=2, col=2)
    fig.update_yaxes(title_text="Temperature [°C]", row=1, col=1)
    fig.update_yaxes(title_text="Humidity [%]", row=1, col=2)
    fig.update_yaxes(title_text="Pressure [hPa]", row=2, col=1)
    fig.update_yaxes(title_text="Rainfall [mm]", row=2, col=2)

    fig.update_layout(height=800, width=1200, title_text="IoT Sensor Data Dashboard")
    fig.show()


def create_dashboard(data):
    time_coarse, time_fine, temperature, humidity, pressure, rainfall = get_time_series(data)

    dates_fine = [datetime.datetime.fromtimestamp(ts) for ts in time_fine]
    dates_coarse = [datetime.datetime.fromtimestamp(ts) for ts in time_coarse]

    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

    app.layout = html.Div([
        html.H1("IoT Sensor Data Dashboard"),
        dbc.Row([
            dbc.Col(dbc.Button("Overview", id="btn-overview", color="primary", className="m-1"), width="auto"),
            dbc.Col(dbc.Button("Temperature", id="btn-temperature", color="secondary", className="m-1"), width="auto"),
            dbc.Col(dbc.Button("Humidity", id="btn-humidity", color="secondary", className="m-1"), width="auto"),
            dbc.Col(dbc.Button("Pressure", id="btn-pressure", color="secondary", className="m-1"), width="auto"),
            dbc.Col(dbc.Button("Rainfall", id="btn-rainfall", color="secondary", className="m-1"), width="auto"),
        ]),
        dcc.Graph(id="graph-content", style={"height": "80vh"})
    ])

    @app.callback(
        Output("graph-content", "figure"),
        [Input("btn-overview", "n_clicks"),
         Input("btn-temperature", "n_clicks"),
         Input("btn-humidity", "n_clicks"),
         Input("btn-pressure", "n_clicks"),
         Input("btn-rainfall", "n_clicks")]
    )
    def update_graph(*args):
        ctx = dash.callback_context
        if not ctx.triggered:
            button_id = "btn-overview"
        else:
            button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if button_id == "btn-overview":
            fig = make_subplots(rows=2, cols=2, subplot_titles=("Temperature", "Humidity", "Pressure", "Rainfall"))
            fig.add_trace(go.Scatter(x=dates_coarse, y=temperature, name="Temperature"), row=1, col=1)
            fig.add_trace(go.Scatter(x=dates_fine, y=humidity, name="Humidity"), row=1, col=2)
            fig.add_trace(go.Scatter(x=dates_fine, y=pressure, name="Pressure"), row=2, col=1)
            fig.add_trace(go.Scatter(x=dates_fine, y=rainfall, name="Rainfall"), row=2, col=2)
            fig.update_xaxes(title_text="Time", row=2, col=1)
            fig.update_xaxes(title_text="Time", row=2, col=2)
            fig.update_yaxes(title_text="Temperature [°C]", row=1, col=1)
            fig.update_yaxes(title_text="Humidity [%]", row=1, col=2)
            fig.update_yaxes(title_text="Pressure [hPa]", row=2, col=1)
            fig.update_yaxes(title_text="Rainfall [mm]", row=2, col=2)
        elif button_id == "btn-temperature":
            fig = go.Figure(go.Scatter(x=dates_coarse, y=temperature, name="Temperature"))
            fig.update_layout(title="Temperature", xaxis_title="Time", yaxis_title="Temperature [°C]")
        elif button_id == "btn-humidity":
            fig = go.Figure(go.Scatter(x=dates_fine, y=humidity, name="Humidity"))
            fig.update_layout(title="Humidity", xaxis_title="Time", yaxis_title="Humidity [%]")
        elif button_id == "btn-pressure":
            fig = go.Figure(go.Scatter(x=dates_fine, y=pressure, name="Pressure"))
            fig.update_layout(title="Pressure", xaxis_title="Time", yaxis_title="Pressure [hPa]")
        elif button_id == "btn-rainfall":
            fig = go.Figure(go.Scatter(x=dates_fine, y=rainfall, name="Rainfall"))
            fig.update_layout(title="Rainfall", xaxis_title="Time", yaxis_title="Rainfall [mm]")

        fig.update_layout(height=700)
        return fig

    return app


def visualize_IOT_data(data):
    time_coarse, time_fine, temperature, humidity, pressure, rainfall = get_time_series(data)

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

def get_time_series(data):
    time_coarse = []
    time_fine = []
    temperature = []
    humidity = []
    pressure = []
    rainfall = []
    for t, d in enumerate(data):
        dtime_coarse = datetime.datetime.fromisoformat(d['created_at'][:19])
        tstamp_coarse = datetime.datetime.timestamp(dtime_coarse)
        if d['type'] == 'data' and d['device_name'] == 'chester-meteo':
            try:
                dict_data = ast.literal_eval(d['body'])

            except Exception as e:
                # dict_data = eval(str(d['body']))
                print("HAYAAA")
                print(e)
                continue

            time_coarse.append(tstamp_coarse)
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

        
        if d['device_name'] == 'chester-clime-iaq':
            print(d.keys())

            try:
                dict_data = ast.literal_eval(d['body'])
            except Exception as e:
                print("HAYAAAaaa")
                print(e)
                continue

            print(dict_data.keys())

    
    sorted_rainfall = [r for _, r in sorted(zip(time_fine, rainfall))]
    sorted_pressure = [p for _, p in sorted(zip(time_fine, pressure))]
    sorted_humidity = [h for _, h in sorted(zip(time_fine, humidity))]
    sorted_time_fine = sorted(time_fine)

    return time_coarse, sorted_time_fine, temperature, sorted_humidity, sorted_pressure, sorted_rainfall



if __name__ == "__main__":
    data = get_IOT_data()
    out = get_time_series(data)
    # app = create_dashboard(data)
    # app.run_server(debug=True)
    # visualize_IOT_data(data)
    # dashboard(data)
