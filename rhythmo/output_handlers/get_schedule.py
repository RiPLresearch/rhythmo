import numpy as np

import datetime
import matplotlib.pyplot as plt
import plotly.graph_objects as go 
from logger.logger import get_logger
logger = get_logger(__name__)

def output_handler(_rhythmo_inputs, rhythmo_outputs, parameters) -> None:
    timing_of_future_phases = parameters.timing_of_future_phases
    number_of_future_phases = parameters.number_of_future_phases
    projection_duration = parameters.projection_duration
    projected_cycle = rhythmo_outputs.projected_cycle
    future_phases = rhythmo_outputs.future_phases

    if timing_of_future_phases == 'regular_sampling':
        regular_samples = future_phases['regular_samples']

    elif timing_of_future_phases == 'peak_trough':
        peaks = future_phases['peaks']
        troughs = future_phases['troughs']

    elif timing_of_future_phases == 'peak_trough_rising_falling':
        peaks = future_phases['peaks']
        troughs = future_phases['troughs']
        rising = 1
        falling = 1

    else:
        error_message = f"Timing of future phases {timing_of_future_phases} is not valid. Please either add this functionality or select one of: regular_sampling, peak_trough, peak_trough_rising_falling."
        logger.error(error_message, exc_info=True)
        raise ValueError(error_message)
    
    # # Define the start and end dates for the shaded region
    # start_date = datetime.datetime(1971, 3, 5)
    # end_date = datetime.datetime(1971, 3, 7)

    # # Create a shaded region trace
    # trough = go.Scatter(
    #     x = [start_date, start_date, end_date, end_date],
    #     y = [50, 75, 75, 50],
    #     fill = 'toself',
    #     fillcolor = 'rgba(0, 128, 0, 0.4)',
    #     line = dict(color = 'rgba(0, 0, 0, 0)'),
    #     showlegend = True,
    #     name = 'trough of cycle'
    # )

    # start_date = datetime.datetime(1971, 8, 30)
    # end_date = datetime.datetime(1971, 11, 2)
    # peak = go.Scatter(
    #     x = [start_date, start_date, end_date, end_date],
    #     y = [50, 75, 75, 50],
    #     fill = 'toself',
    #     fillcolor = 'rgba(255, 0, 0, 0.4)',
    #     line = dict(color = 'rgba(0, 0, 0, 0)'),
    #     showlegend = True,
    #     name = 'peak of cycle'
    # )

    # # Add the shaded region trace to the figure
    # fig.add_trace(peak)
    # fig.add_trace(trough)
    d = 1