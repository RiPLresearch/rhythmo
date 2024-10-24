import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
import plotly.graph_objects as go 
from logger.logger import get_logger
logger = get_logger(__name__)

def output_handler(_rhythmo_inputs, rhythmo_outputs, parameters) -> None:
    """
    This output handler outputs a plot of the schedule times and the corresponding csv file.
    """
    future_phases = rhythmo_outputs.future_phases
    future_phases.to_csv(os.path.join("results", f"sampling_times.csv"), index=False)

    print(future_phases)

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
    # d = 1