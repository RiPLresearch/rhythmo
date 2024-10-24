import numpy as np
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import plotly.graph_objects as go 
from rhythmo.data import MILLISECONDS_IN_A_DAY
from logger.logger import get_logger
logger = get_logger(__name__)

def output_handler(_rhythmo_inputs, rhythmo_outputs, parameters) -> None:
    """
    Plots the forecasted cycle to the user's chosen projection duration.
    """
    resampled_data = rhythmo_outputs.resampled_data
    filtered_cycle = rhythmo_outputs.historic_cycle.value
    time_in_past = rhythmo_outputs.historic_cycle.timestamps
    strongest_peak = rhythmo_outputs.cycle_period
    projection_duration = parameters.projection_duration
    projected_cycle = rhythmo_outputs.future_cycle.value
    time_in_future = rhythmo_outputs.future_cycle.timestamps

    if projection_duration is not None:
        projection_duration = min(4*strongest_peak, projection_duration)
    else:
        projection_duration = 4 * strongest_peak
    
    projection_duration_ms = projection_duration * MILLISECONDS_IN_A_DAY

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=resampled_data['timestamp'], 
                            y=resampled_data['value'],
                            mode='lines', name='heart rate',
                            line={'color': 'rgb(115,115,115)'}))
    
    fig.add_trace(go.Scatter(x= time_in_past,
                            y=filtered_cycle,
                            mode='lines', name=f'{strongest_peak} day cycle',
                            line={'color': 'tomato'}))
    
    fig.add_trace(go.Scatter(x = time_in_future[:int(projection_duration_ms)], 
                            y = projected_cycle[:int(projection_duration_ms)], 
                            mode = 'lines', name=f'predicted future cycle', 
                            line = {'color': 'tomato', 'dash': 'dash'}))

    # Display the figure
    # fig.update_layout(
    #     yaxis = dict(range = [resampled_data['value'].min(), resampled_data['value'].max()]),
    #     xaxis = dict(range = [datetime.datetime(1971, 1, 1), datetime.datetime(1972, 4, 1)])
    # )

    fig.update_layout(xaxis_title = 'Time',
                    yaxis_title = 'Heart Rate',
                    showlegend = True)
    fig.show()
    
  