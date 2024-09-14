import datetime

import matplotlib.pyplot as plt
import matplotlib.dates as md

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from get_iot_data import get_time_series as iot_time_series
from open_tif import get_time_series as sat_time_series


SAT_DATA_DIR = "output"


def create_dashboard(sat_data_dir):
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

    app.layout = html.Div([
        html.H1("IoT Sensor and Satellite Data Dashboard"),
        dbc.Row([
            dbc.Col(dbc.Button("Overview", id="btn-overview", color="primary", className="m-1"), width="auto"),
            dbc.Col(dbc.Button("Temperature", id="btn-temperature", color="secondary", className="m-1"), width="auto"),
            dbc.Col(dbc.Button("Humidity", id="btn-humidity", color="secondary", className="m-1"), width="auto"),
            dbc.Col(dbc.Button("Pressure", id="btn-pressure", color="secondary", className="m-1"), width="auto"),
            dbc.Col(dbc.Button("Rainfall", id="btn-rainfall", color="secondary", className="m-1"), width="auto"),
            dbc.Col(dbc.Button("CO Level (Satellite)", id="btn-satellite", color="secondary", className="m-1"), width="auto"),
        ]),
        dcc.Graph(id="graph-content", style={"height": "80vh"})
    ])

    # Add this new component to your layout
    app.layout.children.append(dcc.Interval(
        id='interval-component',
        interval=20*60*1000,  # in milliseconds, 20 minutes
        n_intervals=0
    ))

    def get_updated_data():
        time_coarse, time_fine, temperature, humidity, pressure, rainfall = iot_time_series()
        t, co_val = sat_time_series(sat_data_dir)
        
        dates_fine = [datetime.datetime.fromtimestamp(ts) for ts in time_fine]
        dates_coarse = [datetime.datetime.fromtimestamp(ts) for ts in time_coarse]
        dates_sat = [datetime.datetime.strptime(ts, '%Y-%m-%d-%H-%M') for ts in t]
        
        return dates_fine, dates_coarse, dates_sat, temperature, humidity, pressure, rainfall, co_val

    @app.callback(
        Output("graph-content", "figure"),
        [Input("btn-overview", "n_clicks"),
         Input("btn-temperature", "n_clicks"),
         Input("btn-humidity", "n_clicks"),
         Input("btn-pressure", "n_clicks"),
         Input("btn-rainfall", "n_clicks"),
         Input("btn-satellite", "n_clicks"),
         Input("interval-component", "n_intervals")]  # Add this new input
    )
    def update_graph(*args):
        ctx = dash.callback_context
        if not ctx.triggered:
            button_id = "btn-overview"
        else:
            button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        # Get updated data
        dates_fine, dates_coarse, dates_sat, temperature, humidity, pressure, rainfall, co_val = get_updated_data()

        if button_id == "btn-overview":
            fig = make_subplots(rows=3, cols=2, subplot_titles=("Temperature", "Humidity", "Pressure", "Rainfall", "Satellite Data"))
            fig.add_trace(go.Scatter(x=dates_coarse, y=temperature, name="Temperature"), row=1, col=1)
            fig.add_trace(go.Scatter(x=dates_fine, y=humidity, name="Humidity"), row=1, col=2)
            fig.add_trace(go.Scatter(x=dates_fine, y=pressure, name="Pressure"), row=2, col=1)
            fig.add_trace(go.Scatter(x=dates_fine, y=rainfall, name="Rainfall"), row=2, col=2)
            fig.add_trace(go.Scatter(x=dates_sat, y=co_val, name="Satellite Data"), row=3, col=1)
            fig.update_xaxes(title_text="Time", row=2, col=1)
            fig.update_xaxes(title_text="Time", row=2, col=2)
            fig.update_xaxes(title_text="Time", row=3, col=1)
            fig.update_yaxes(title_text="Temperature [°C]", row=1, col=1)
            fig.update_yaxes(title_text="Humidity [%]", row=1, col=2)
            fig.update_yaxes(title_text="Pressure [hPa]", row=2, col=1)
            fig.update_yaxes(title_text="Rainfall [mm]", row=2, col=2)
            fig.update_yaxes(title_text="CO Level", row=3, col=1)
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
        elif button_id == "btn-satellite":
            fig = go.Figure(go.Scatter(x=dates_sat, y=co_val, name="CO Level (Satellite)"))
            fig.update_layout(title="Satellite Data", xaxis_title="Time", yaxis_title="CO Level")

        fig.update_layout(height=700)
        return fig

    return app


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



if __name__ == "__main__":
    app = create_dashboard(SAT_DATA_DIR)
    app.run_server(debug=True)
