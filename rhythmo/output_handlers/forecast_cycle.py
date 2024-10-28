import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import plotly.graph_objects as go 
from rhythmo.data import MILLISECONDS_IN_A_DAY
from logger.logger import get_logger
logger = get_logger(__name__)

def output_handler(_rhythmo_inputs, rhythmo_outputs, parameters) -> None:
    """
    Plots the forecasted cycle to the user's chosen projection duration.
    """
    resampled_data = rhythmo_outputs.resampled_data
    strongest_peak = rhythmo_outputs.cycle_period
    projection_duration = parameters.projection_duration

    filtered_cycle = rhythmo_outputs.historic_cycle.value
    time_in_past = rhythmo_outputs.historic_cycle.timestamps

    projected_cycle = rhythmo_outputs.future_cycle.value
    time_in_future = rhythmo_outputs.future_cycle.timestamps

    if projection_duration is not None:
        projection_duration = min(4 * strongest_peak, projection_duration)
    else:
        projection_duration = 4 * strongest_peak
    
    projection_duration_ms = projection_duration * MILLISECONDS_IN_A_DAY

    fig = go.Figure()
    fig.add_trace(go.Scatter(x = resampled_data['timestamp'], 
                            y = resampled_data['value'],
                            mode = 'lines', name = 'heart rate',
                            line = {'color': 'rgb(115,115,115)'}))
    
    fig.add_trace(go.Scatter(x = time_in_past,
                            y = filtered_cycle,
                            mode = 'lines', name = f'{strongest_peak} day cycle',
                            line = {'color': 'tomato'}))
    
    fig.add_trace(go.Scatter(x = time_in_future[:int(projection_duration_ms)], 
                            y = projected_cycle[:int(projection_duration_ms)], 
                            mode = 'lines', name = f'predicted future cycle', 
                            line = {'color': 'tomato', 'dash': 'dash'}))

    # Determining margin for y-axis boundaries
    y_axis_margin = (resampled_data['value'].max() - resampled_data['value'].min()) * 0.1
    y_axis_min = resampled_data['value'].min() - y_axis_margin
    y_axis_max = resampled_data['value'].max() + y_axis_margin

    ## Display the figure
    fig.update_layout(
        yaxis = dict(range = [y_axis_min, y_axis_max]),
        xaxis = dict(range = [time_in_past[0], time_in_future[-1]])
        )
    fig.update_layout(xaxis_title = 'Time',
                    yaxis_title = 'Heart Rate',
                    showlegend = True)
    fig.show()
    
  