import numpy as np

import datetime
import matplotlib.pyplot as plt
import plotly.graph_objects as go 
from logger.logger import get_logger
logger = get_logger(__name__)

from logger.logger import get_logger

logger = get_logger(__name__)


def output_handler(_rhythmo_inputs, rhythmo_outputs, _parameters) -> None:
    filtered_cycle = rhythmo_outputs.filtered_cycle
    projected_cycle = rhythmo_outputs.projected_cycle

    time_in_past = filtered_cycle['timestamp'].apply(lambda x: x.timestamp() * 1000)
    timestamp_dif = time_in_past.iloc[-1] - time_in_past.iloc[-2]
    time_in_future = np.arange(time_in_past.iloc[-1], time_in_past.iloc[-1] + timestamp_dif*1000, timestamp_dif)

    fig = go.Figure()
    
    fig.add_trace(go.Scatter(x = time_in_future[:200], 
                            y = projected_cycle[:200], 
                            mode = 'lines', name=f'predicted future cycle', 
                            line = {'color': 'tomato', 'dash': 'dash'}))

    # Define the start and end dates for the shaded region
    start_date = datetime.datetime(1971, 3, 5)
    end_date = datetime.datetime(1971, 3, 7)

    # Create a shaded region trace
    trough = go.Scatter(
        x = [start_date, start_date, end_date, end_date],
        y = [50, 75, 75, 50],
        fill = 'toself',
        fillcolor = 'rgba(0, 128, 0, 0.4)',
        line = dict(color = 'rgba(0, 0, 0, 0)'),
        showlegend = True,
        name = 'trough of cycle'
    )

    start_date = datetime.datetime(1971, 8, 30)
    end_date = datetime.datetime(1971, 11, 2)
    peak = go.Scatter(
        x = [start_date, start_date, end_date, end_date],
        y = [50, 75, 75, 50],
        fill = 'toself',
        fillcolor = 'rgba(255, 0, 0, 0.4)',
        line = dict(color = 'rgba(0, 0, 0, 0)'),
        showlegend = True,
        name = 'peak of cycle'
    )

    # Add the shaded region trace to the figure
    fig.add_trace(peak)
    fig.add_trace(trough)

    # Display the figure
    fig.update_layout(
        yaxis = dict(range = [51, 70]),
        xaxis = dict(range = [datetime.datetime(1971, 1, 1), datetime.datetime(1972, 4, 1)])
    )

    fig.update_layout(xaxis_title = 'Time',
                    yaxis_title = 'Heart Rate',
                    showlegend = True)
    fig.show()
