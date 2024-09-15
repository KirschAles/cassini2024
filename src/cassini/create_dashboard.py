import datetime
from zoneinfo import ZoneInfo
import os

import matplotlib.pyplot as plt
import matplotlib.dates as md

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.cassini.get_IOT_data import get_time_series as iot_time_series
from src.cassini.open_tif import get_time_series as sat_time_series


SAT_DATA_DIR = "satellite_data"
BANDS = ["CO", "NO2", "O3", "CH4"]


def create_dashboard(sat_data_dir):
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

    app.layout = html.Div([
        dbc.Container([
            html.H1("IoT Sensor and Satellite Data Dashboard", className="my-4"),
            dbc.Row([
                dbc.Col(dbc.Button("Overview", id="btn-overview", color="primary", className="m-1"), width="auto"),
                dbc.Col(dbc.Button("Temperature", id="btn-temperature", color="secondary", className="m-1"), width="auto"),
                dbc.Col(dbc.Button("Humidity", id="btn-humidity", color="secondary", className="m-1"), width="auto"),
                dbc.Col(dbc.Button("Pressure", id="btn-pressure", color="secondary", className="m-1"), width="auto"),
                dbc.Col(dbc.Button("Rainfall", id="btn-rainfall", color="secondary", className="m-1"), width="auto"),
                dbc.Col(dbc.Button("CO2 Level", id="btn-co2", color="secondary", className="m-1"), width="auto"),
                dbc.Col(dbc.Button("CO Level (Satellite)", id="btn-co", color="secondary", className="m-1"), width="auto"),
                dbc.Col(dbc.Button("NO2 Level (Satellite)", id="btn-no2", color="secondary", className="m-1"), width="auto"),
                dbc.Col(dbc.Button("O3 Level (Satellite)", id="btn-o3", color="secondary", className="m-1"), width="auto"),
                dbc.Col(dbc.Button("CH4 Level (Satellite)", id="btn-ch4", color="secondary", className="m-1"), width="auto"),
            ], className="mb-4"),
            dcc.Graph(id="graph-content", style={"height": "80vh"})
        ], fluid=True, className="px-4 py-3")
    ], style={"backgroundColor": "#f8f9fa"})

    #Update data every 20 minutes
    app.layout.children[0].children.append(dcc.Interval(
        id='interval-component',
        interval=20*60*1000,  # in milliseconds, 20 minutes
        n_intervals=0
    ))

    def get_updated_data():
        time_coarse, time_fine, time_co2, temperature, humidity, pressure, rainfall, co2 = iot_time_series()

        sat_dates = []
        sat_vals = []
        for band in BANDS:
            t, val = sat_time_series(sat_data_dir, band)
            dates = [datetime.datetime.strptime(ts, '%Y-%m-%d-%H-%M') for ts in t]
            sat_dates.append(dates)
            sat_vals.append(val)
        
        dates_fine = [datetime.datetime.fromtimestamp(ts, tz=ZoneInfo("Europe/Prague")) for ts in time_fine]
        dates_coarse = [datetime.datetime.fromtimestamp(ts, tz=ZoneInfo("Europe/Prague")) for ts in time_coarse]
        dates_co2 = [datetime.datetime.fromtimestamp(ts, tz=ZoneInfo("Europe/Prague")) for ts in time_co2]

        output = {"station_out": {"Temperature": (temperature, dates_coarse),
                                  "Humidity": (humidity, dates_fine),
                                  "Pressure": (pressure, dates_fine),
                                  "Rainfall": (rainfall, dates_fine),},
                 "station_in": {"CO2": (co2, dates_co2)},
                 "satellite": {band: (val, t) for band, val, t in zip(BANDS, sat_vals, sat_dates)}}
        
        return output

    @app.callback(
        [Output("graph-content", "figure"),
         Output("btn-overview", "color"),
         Output("btn-temperature", "color"),
         Output("btn-humidity", "color"),
         Output("btn-pressure", "color"),
         Output("btn-rainfall", "color"),
         Output("btn-co2", "color"),
         Output("btn-co", "color"),
         Output("btn-no2", "color"),
         Output("btn-o3", "color"),
         Output("btn-ch4", "color")],
        [Input("btn-overview", "n_clicks"),
         Input("btn-temperature", "n_clicks"),
         Input("btn-humidity", "n_clicks"),
         Input("btn-pressure", "n_clicks"),
         Input("btn-rainfall", "n_clicks"),
         Input("btn-co2", "n_clicks"),
         Input("btn-co", "n_clicks"),
         Input("btn-no2", "n_clicks"),
         Input("btn-o3", "n_clicks"),
         Input("btn-ch4", "n_clicks"),
         Input("interval-component", "n_intervals")],
         prevent_initial_call=False
    )
    def update_graph(*args):
        ctx = dash.callback_context
        if not ctx.triggered:
            button_id = "btn-overview"
        else:
            button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        # Get updated data
        data_dict = get_updated_data()

        subplot_titles = list(data_dict["station_out"].keys()) + list(data_dict["station_in"].keys()) + [key + " (Satellite)" for key in data_dict["satellite"].keys()]

        if button_id == "btn-overview":
            fig = make_subplots(rows=3, cols=3, subplot_titles=subplot_titles)
            plot_pos = (1,1)
            for i, key in enumerate(data_dict["station_out"].keys()):
                fig.add_trace(go.Scatter(x=data_dict["station_out"][key][1], y=data_dict["station_out"][key][0], name=key), row=plot_pos[0], col=plot_pos[1])
                if plot_pos[1] == 3:
                    plot_pos = (plot_pos[0]+1, 1)
                else:
                    plot_pos = (plot_pos[0], plot_pos[1]+1)
            for i, key in enumerate(data_dict["station_in"].keys()):
                fig.add_trace(go.Scatter(x=data_dict["station_in"][key][1], y=data_dict["station_in"][key][0], name=key), row=plot_pos[0], col=plot_pos[1])
                if plot_pos[1] == 3:
                    plot_pos = (plot_pos[0]+1, 1)
                else:
                    plot_pos = (plot_pos[0], plot_pos[1]+1)
            for i, key in enumerate(data_dict["satellite"].keys()):
                fig.add_trace(go.Scatter(x=data_dict["satellite"][key][1], y=data_dict["satellite"][key][0], name=key + " (Satellite)"), row=plot_pos[0], col=plot_pos[1])
                if plot_pos[1] == 3:
                    plot_pos = (plot_pos[0]+1, 1)
                else:
                    plot_pos = (plot_pos[0], plot_pos[1]+1)

            fig.update_xaxes(title_text="Time", row=3, col=1)
            fig.update_xaxes(title_text="Time", row=3, col=2)
            fig.update_xaxes(title_text="Time", row=3, col=3)
            fig.update_yaxes(title_text="Temperature [°C]", row=1, col=1)
            fig.update_yaxes(title_text="Humidity [%]", row=1, col=2)
            fig.update_yaxes(title_text="Pressure [hPa]", row=1, col=3)
            fig.update_yaxes(title_text="Rainfall [mm]", row=2, col=1)
            fig.update_yaxes(title_text="CO2 Level [ppm]", row=2, col=2)
            fig.update_yaxes(title_text="CO Level", row=2, col=3)
            fig.update_yaxes(title_text="NO2 Level", row=3, col=1)
            fig.update_yaxes(title_text="O3 Level", row=3, col=2)
            fig.update_yaxes(title_text="CH4 Level", row=3, col=3)
        elif button_id == "btn-temperature":
            t = data_dict["station_out"]["Temperature"][1]
            val = data_dict["station_out"]["Temperature"][0]
            fig = go.Figure(go.Scatter(x=t, y=val, name="Temperature"))
            fig.update_layout(title="Temperature", xaxis_title="Time", yaxis_title="Temperature [°C]")
        elif button_id == "btn-humidity":
            t = data_dict["station_out"]["Humidity"][1]
            val = data_dict["station_out"]["Humidity"][0]
            fig = go.Figure(go.Scatter(x=t, y=val, name="Humidity"))
            fig.update_layout(title="Humidity", xaxis_title="Time", yaxis_title="Humidity [%]")
        elif button_id == "btn-pressure":
            t = data_dict["station_out"]["Pressure"][1]
            val = data_dict["station_out"]["Pressure"][0]
            fig = go.Figure(go.Scatter(x=t, y=val, name="Pressure"))
            fig.update_layout(title="Pressure", xaxis_title="Time", yaxis_title="Pressure [hPa]")
        elif button_id == "btn-rainfall":
            t = data_dict["station_out"]["Rainfall"][1]
            val = data_dict["station_out"]["Rainfall"][0]
            fig = go.Figure(go.Scatter(x=t, y=val, name="Rainfall"))
            fig.update_layout(title="Rainfall", xaxis_title="Time", yaxis_title="Rainfall [mm]")
        elif button_id == "btn-co2":
            t = data_dict["station_in"]["CO2"][1]
            val = data_dict["station_in"]["CO2"][0]
            fig = go.Figure(go.Scatter(x=t, y=val, name="CO2 Level"))
            fig.update_layout(title="CO2 Level", xaxis_title="Time", yaxis_title="CO2 Level [ppm]")
        elif button_id == "btn-co":
            t = data_dict["satellite"]["CO"][1]
            val = data_dict["satellite"]["CO"][0]
            fig = go.Figure(go.Scatter(x=t, y=val, name="CO Level (Satellite)"))
            fig.update_layout(title="CO Level (Satellite)", xaxis_title="Time", yaxis_title="CO Level")
        elif button_id == "btn-no2":
            t = data_dict["satellite"]["NO2"][1]
            val = data_dict["satellite"]["NO2"][0]
            fig = go.Figure(go.Scatter(x=t, y=val, name="NO2 Level (Satellite)"))
            fig.update_layout(title="NO2 Level (Satellite)", xaxis_title="Time", yaxis_title="NO2 Level")
        elif button_id == "btn-o3":
            t = data_dict["satellite"]["O3"][1]
            val = data_dict["satellite"]["O3"][0]
            fig = go.Figure(go.Scatter(x=t, y=val, name="O3 Level (Satellite)"))
            fig.update_layout(title="O3 Level (Satellite)", xaxis_title="Time", yaxis_title="O3 Level")
        elif button_id == "btn-ch4":
            t = data_dict["satellite"]["CH4"][1]
            val = data_dict["satellite"]["CH4"][0]
            fig = go.Figure(go.Scatter(x=t, y=val, name="CH4 Level (Satellite)"))
            fig.update_layout(title="CH4 Level (Satellite)", xaxis_title="Time", yaxis_title="CH4 Level")

        fig.update_layout(height=700)

        # Update button colors
        button_colors = ["secondary"] * 10
        button_index = ["btn-overview", "btn-temperature", "btn-humidity", "btn-pressure", "btn-rainfall", "btn-co2", "btn-co", "btn-no2", "btn-o3", "btn-ch4"].index(button_id)
        button_colors[button_index] = "primary"

        return fig, *button_colors

    return app



app = create_dashboard(SAT_DATA_DIR)
server = app.server

if __name__ == "__main__":
    app.run_server(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
