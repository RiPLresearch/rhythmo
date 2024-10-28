import numpy as np
import pandas as pd
import datetime
import os
import matplotlib.pyplot as plt
from rhythmo.data import MILLISECONDS_IN_A_DAY
import plotly.graph_objects as go 
from logger.logger import get_logger
logger = get_logger(__name__)

def output_handler(_rhythmo_inputs, rhythmo_outputs, parameters) -> None:
    """
    This output handler outputs a plot of the schedule times and the corresponding csv file.
    """
    resampled_data = rhythmo_outputs.resampled_data
    strongest_peak = rhythmo_outputs.cycle_period
    projection_duration = parameters.projection_duration

    filtered_cycle = rhythmo_outputs.historic_cycle.value
    time_in_past = rhythmo_outputs.historic_cycle.timestamps

    projected_cycle = rhythmo_outputs.future_cycle.value
    time_in_future = rhythmo_outputs.future_cycle.timestamps
    future_phases = rhythmo_outputs.future_phases
    
    ## Outputting csv file of schedule times
    future_phases.to_csv(os.path.join("results", f"sampling_times.csv"), index=False)

    print(future_phases)

    if projection_duration is not None:
        projection_duration = min(4*strongest_peak, projection_duration)
    else:
        projection_duration = 4 * strongest_peak
    
    projection_duration_ms = projection_duration * MILLISECONDS_IN_A_DAY

    fig = go.Figure()
    fig.add_trace(go.Scatter(x = resampled_data['timestamp'], 
                            y = pd.Series(resampled_data['value']).rolling(window = 13).mean(),
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

    fig.update_layout(
        yaxis = dict(range = [y_axis_min, y_axis_max]),
        xaxis = dict(range = [time_in_past[0], time_in_future[-1]])
        )
    
    if 'regular_sampling' in future_phases:
        samples_dates = pd.to_datetime(future_phases['regular_sampling'])
        time_in_future_datetime = pd.to_datetime(time_in_future, unit='ms')
        indices =  np.where(np.isin(time_in_future_datetime, samples_dates))

        regular_samples = go.Scatter(
            x = time_in_future[indices],
            y = projected_cycle[indices],
            mode = 'markers',
            name = 'Sample Times',
            marker = dict(size = 10, color = 'purple')
        )
        # Add the shaded region trace to the figure
        fig.add_trace(regular_samples)

    elif 'peaks' in future_phases or 'troughs' in future_phases:
        
        # Define the start and end dates for the shaded region
        trough_start_date = pd.to_datetime(future_phases['troughs']) - pd.Timedelta(days = 1)
        trough_end_date = pd.to_datetime(future_phases['troughs']) + pd.Timedelta(days = 1)

        # Create a shaded region trace
        trough = go.Scatter(
            x = [trough_start_date[0], trough_start_date[0], trough_end_date[0], trough_end_date[0]],
            y = [y_axis_min, y_axis_max, y_axis_max, y_axis_min],
            fill = 'toself',
            fillcolor = 'rgba(0, 128, 0, 0.4)',
            line = dict(color = 'rgba(0, 0, 0, 0)'),
            showlegend = True,
            name = 'trough of cycle'
        )

        peak_start_date = pd.to_datetime(future_phases['peaks']) - pd.Timedelta(days = 1)
        peak_end_date = pd.to_datetime(future_phases['peaks']) + pd.Timedelta(days = 1)

        peak = go.Scatter(
            x = [peak_start_date[0], peak_start_date[0], peak_end_date[0], peak_end_date[0]],
            y = [y_axis_min, y_axis_max, y_axis_max, y_axis_min],
            fill = 'toself',
            fillcolor = 'rgba(255, 0, 0, 0.4)',
            line = dict(color = 'rgba(0, 0, 0, 0)'),
            showlegend = True,
            name = 'peak of cycle'
        )

        # Add the shaded region trace to the figure
        fig.add_trace(peak)
        fig.add_trace(trough)

        if 'rising' in future_phases or 'falling' in future_phases:
            # Define the start and end dates for the shaded region
            rising_start_date = pd.to_datetime(future_phases['rising']) - pd.Timedelta(days = 1)
            rising_end_date = pd.to_datetime(future_phases['rising']) + pd.Timedelta(days = 1)

            # Create a shaded region trace
            rising = go.Scatter(
                x = [rising_start_date[0], rising_start_date[0], rising_end_date[0], rising_end_date[0]],
                y = [y_axis_min, y_axis_max, y_axis_max, y_axis_min],
                fill = 'toself',
                fillcolor = 'rgba(128, 0, 128, 0.5)',
                line = dict(color = 'rgba(0, 0, 0, 0)'),
                showlegend = True,
                name = 'rising'
            )

            falling_start_date = pd.to_datetime(future_phases['falling']) - pd.Timedelta(days = 1)
            falling_end_date = pd.to_datetime(future_phases['falling']) + pd.Timedelta(days = 1)

            falling = go.Scatter(
                x = [falling_start_date[0], falling_start_date[0], falling_end_date[0], falling_end_date[0]],
                y = [y_axis_min, y_axis_max, y_axis_max, y_axis_min],
                fill = 'toself',
                fillcolor = 'rgba(0, 0, 255, 1)',
                line = dict(color = 'rgba(0, 0, 0, 0)'),
                showlegend = True,
                name = 'falling'
            )

            # Add the shaded region trace to the figure
            fig.add_trace(rising)
            fig.add_trace(falling)
    else:
        error_message = f"Unable to plot schedule times as {future_phases} is not valid. Please either add this functionality or select one of: regular_sampling, peak_trough, peak_trough_rising_falling."
        logger.error(error_message, exc_info=True)
        raise ValueError(error_message)

    ## Display the figure
    fig.update_layout(xaxis_title = 'Time',
                yaxis_title = 'Heart Rate',
                showlegend = True)
    fig.show()